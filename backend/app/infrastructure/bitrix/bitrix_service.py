import httpx
import asyncio
from dataclasses import dataclass
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote
from app.core.config import settings
from app.domain.message.repository import MessageRepository
from app.domain.chat.repository import ChatRepository
from app.domain.storage.repository import StorageRepo
from app.domain.user.schema import UserOutSchema
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.domain.message.schema import MessageCreate
from app.domain.chat.schema import ChatCreate, ChatOut
from app.enums.enums import UserRole, MessageState
from app.domain.message.schema import ResultPayload, SourceInfo
from app.utils.oauth2 import create_temporary_access_token
from app.database.connection import db_manager
from app.infrastructure.redis.client import get_redis_client
from app.core.decorators import log_timing
from app.core.logger import get_logger


logger = get_logger()


@dataclass(frozen=True)
class BitrixWebhook:
    event: str
    bot_id: str
    dialog_id: str
    message_text: str
    message_id: str
    user_id: str


class BitrixService:
    """
    Complete Bitrix24 service handling parsing, validation, user management, 
    message processing, and response sending.
    """
    
    def __init__(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        user: UserOutSchema,
        openai_manager: OpenAIManager,
        storage_repo: StorageRepo
    ):
        # Dependencies
        self.message_repo = message_repo
        self.chat_repo = chat_repo
        self.user = user
        self.openai_manager = openai_manager
        self.storage_repo = storage_repo

        # Security settings
        self.expected_domain = "crm.clever-trading.ru"

        self.client_id = "354"
        self.base_url = settings.BASE_URL
        self.webhook_url = settings.BITRIX_WEBHOOK_URL
    
    @log_timing('Bitrix process.')
    async def process_webhook(self, form_data: dict):
        logger.info(form_data)
        wh = self._parse_webhook(form_data)
    
        if not self._should_process_event(wh):
            logger.info(f"[bitrix] Event ignored: Bot {wh.bot_id}, User {wh.user_id}")
            return {"action": "ignored"}

        if not all([wh.bot_id, wh.dialog_id, wh.user_id]):
            return {"action": "error", "reason": "missing_ids"}
        
        redis: Redis = await get_redis_client()
        lock_key = f"lock:bitrix:{wh.dialog_id}:{wh.bot_id}"

        if await redis.exists(lock_key):
            if settings.MODE != "test":
                await self.send_response(
                    dialog_id=wh.dialog_id,
                    message="[B]Обрабатываю ваш предыдущий запрос. Пожалуйста, подождите завершения.[/B]",
                    bot_id=wh.bot_id
                )
            return {"action": "locked"}
        try:
            # Set lock for 60 seconds
            await redis.setex(lock_key, 60, 'processing')

            # 4. Database operations and AI Processing
            async with db_manager.session_scope() as db:
                storage = await self.storage_repo.get_by_bot_id(db, wh.bot_id)
                if not storage:
                    await self.send_response(
                        dialog_id=wh.dialog_id,
                        message="Необходимо связать бота с хранилищем. Обратитесь к администратору.",
                        bot_id=wh.bot_id
                    )
                    return {"action": "error_sent", "reason": "bot_not_linked"}
    
                return await self._process_user_message(
                    db=db,
                    wh=wh,
                    vector_store_id=storage.vector_store_id,
                )
        finally:
            await redis.delete(lock_key)

    async def _process_user_message(
        self,
        db: AsyncSession,
        wh: BitrixWebhook,
        vector_store_id: str
    ) -> dict:
        """Process user message - streamlined for background execution."""

        # 1. Get or create chat
        chat = await self._get_or_create_chat(db, wh.dialog_id)

        # 2. Save user message
        await self.message_repo.create(db, MessageCreate(
            chat_id=chat.id,
            content=wh.message_text,
            role=UserRole.USER,
        ))

        # 3. Get AI response
        ai_result = await self._get_ai_response(
            db,
            wh.message_text,
            chat,
            vector_store_id=vector_store_id
        )
        
        # 4. Save assistant message
        await self.message_repo.create(db, MessageCreate(
            chat_id=chat.id,
            content=ai_result.answer,
            sources=ai_result.sources,
            role=UserRole.ASSISTANT,
            state=MessageState.COMPLETED,
        ))

        # 5. Send response to Bitrix
        bitrix_message = ai_result.answer + self._format_sources_for_bitrix(ai_result.sources)

        if settings.MODE != 'test':
            await self.send_response(
                wh.dialog_id, bitrix_message, wh.bot_id
            )

        return {
            "action": "message_processed",
            "ai_response": ai_result.answer,
            "chat_id": chat.id
        }

    def safe_get_form_value(self, form_data, key: str) -> str:
        """Safely extract and decode form data value."""
        value = form_data.get(key)

        if value is None:
            return ""

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        if isinstance(value, str):
            return unquote(value)

        return unquote(str(value))
    
    def _parse_webhook_data(self, form_data) -> dict:
        """Extract all relevant data from Bitrix webhook."""
        bot_id = ""
        for key in form_data.keys():
            if "data[BOT]" in key and "[BOT_ID]" in key:
                bot_id = self.safe_get_form_value(form_data, key)
                break
        
        return {
            "event": self.safe_get_form_value(form_data, 'event'),
            "message": {
                "text": self.safe_get_form_value(form_data, 'data[PARAMS][MESSAGE]'),
                "id": self.safe_get_form_value(form_data, 'data[PARAMS][MESSAGE_ID]'),
                "dialog_id": self.safe_get_form_value(form_data, 'data[PARAMS][DIALOG_ID]'),
                "chat_id": self.safe_get_form_value(form_data, 'data[PARAMS][CHAT_ID]'),
            },
            "user": {
                "id": self.safe_get_form_value(form_data, 'data[USER][ID]'),
                "name": self.safe_get_form_value(form_data, 'data[USER][NAME]'),
                "first_name": self.safe_get_form_value(form_data, 'data[USER][FIRST_NAME]'),
                "last_name": self.safe_get_form_value(form_data, 'data[USER][LAST_NAME]'),
            },
            "bot_id": bot_id
        }

    async def _get_or_create_chat(self, db: AsyncSession, dialog_id: str) -> ChatOut:
        """Find or create chat for Bitrix dialog."""

        # Try to find existing chat for this user
        existing_chat = await self.chat_repo.get_last_created_by_user_id(
            db, int(dialog_id)
        )
        if existing_chat:
            return existing_chat

        # Create new chat with OpenAI thread
        # conv = await self.openai_manager.create_conversation()

        chat_data = ChatCreate(
            name=f"Bitrix Chat {dialog_id}",
            user_id=self.user.id,
            session_handle='conv',
            # session_handle=conv.id,
        )

        chat = await self.chat_repo.create(db, chat_data)

        return chat

    async def _get_ai_response(
        self,
        db: AsyncSession,
        message_text: str,
        chat: ChatOut,
        vector_store_id: str
    ) -> ResultPayload:
        """Get AI response with timeout handling."""

        try:
            if settings.MODE == 'test':
                await asyncio.sleep(20)
    
                return ResultPayload(
                    answer="Test response from AI assistant",
                    sources=[
                        SourceInfo(file_id=1, file_name="test_doc.pdf", page=1)
                    ]
                )

            # Add timeout for AI calls in background tasks
            reply = await asyncio.wait_for(
                self.openai_manager.send_and_receive(
                    db=db,
                    conv_id=chat.session_handle,
                    user=self.user,
                    user_input=message_text,
                    vector_store_id=vector_store_id
                ),
                timeout=30.0
            )

            return reply

        except asyncio.TimeoutError:
            logger.error("[bitrix] AI response timeout")
            return ResultPayload(
                answer="Извините, запрос обрабатывается слишком долго. Попробуйте сформулировать вопрос короче.",
                sources=None
            )
        except Exception as e:
            logger.error(f"[bitrix] OpenAI error: {e}")
            return ResultPayload(
                answer="Извините, возникли технические трудности. Попробуйте позже.",
                sources=None
            )
    
    async def send_response(
        self, dialog_id: str, message: str, bot_id: str
    ) -> bool:
        """Send AI response back to Bitrix24 chat."""
        
        payload = {
            "BOT_ID": bot_id,
            "CLIENT_ID": self.client_id,
            "DIALOG_ID": dialog_id,
            "MESSAGE": message
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                response.json()
                return True
        except Exception as e:
            logger.error(f"[bitrix_service] Failed to send response: {e}")
            return False

    def _format_sources_for_bitrix(
        self, sources: list[SourceInfo] | None
    ) -> str:
        """Format sources as markdown for Bitrix messages."""

        if not sources or len(sources) == 0:
            return ""

        # Filter out sources without valid file names
        valid_sources = [
            source for source in sources 
            if source.file_name and source.file_name.strip()
        ]

        if not valid_sources:
            return ""

        sources_text = "\n\n[B]Источники:[/B]\n"
        for i, source in enumerate(valid_sources, 1):
            token = create_temporary_access_token(source.file_id)

            # Use BBCode URL format to hide the long URL
            sources_text += f"{i}. [URL={self.base_url}/api/v1/file/secure-download?token={token}]{source.file_name}[/URL]"
            if source.page is not None:
                sources_text += f" (стр. {source.page + 1})"
            sources_text += "\n"

        return sources_text
    
    def _parse_webhook(self, form_data: dict) -> BitrixWebhook:
        data = self._parse_webhook_data(form_data)

        # Normalize to str + strip (kills Optional/Any early)
        event = str(data.get("event", "")).strip()
        bot_id = str(data.get("bot_id", "")).strip()

        msg = data.get("message") or {}
        usr = data.get("user") or {}

        dialog_id = str(msg.get("dialog_id", "")).strip()
        message_text = str(msg.get("text", "")).strip()
        message_id = str(msg.get("id", "")).strip()
        user_id = str(usr.get("id", "")).strip()

        return BitrixWebhook(
            event=event,
            bot_id=bot_id,
            dialog_id=dialog_id,
            message_text=message_text,
            message_id=message_id,
            user_id=user_id,
        )
    
    def _should_process_event(self, wh: BitrixWebhook) -> bool:
        return (
            wh.event == "ONIMBOTMESSAGEADD"
            and bool(wh.message_text)
            and wh.user_id != wh.bot_id
        )
