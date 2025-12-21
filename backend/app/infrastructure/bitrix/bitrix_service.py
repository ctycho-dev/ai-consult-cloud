import httpx
import asyncio
import time
from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote
from app.core.logger import get_logger
from app.core.config import settings
from app.domain.message.repository import MessageRepository
from app.domain.chat.repository import ChatRepository
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


logger = get_logger()


class BitrixService:
    """
    Complete Bitrix24 service handling parsing, validation, user management, 
    message processing, and response sending.
    """
    
    def __init__(
        self,
        # db: AsyncSession,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        user: UserOutSchema,
        openai_manager: OpenAIManager
    ):
        # Dependencies
        self.message_repo = message_repo
        self.chat_repo = chat_repo
        self.user = user
        self.openai_manager = openai_manager

        # Security settings
        self.expected_domain = "crm.clever-trading.ru"
        self.expected_app_token = "354"
        self.expected_bot_id = "357"

        self.base_url = settings.BASE_URL
        # Bitrix API settings
        self.webhook_url = settings.BITRIX_WEBHOOK_URL
        self.webhook_data: dict = {}
        self.dialog_id: str = ""
        self.bot_id: str = ""
        self.client_id: str = ""
    
    @log_timing('Bitrix process.')
    async def process_webhook(self, form_data: dict):
        # Create fresh session for background task
        try:
            self.webhook_data = self._parse_webhook_data(form_data)
            self.dialog_id = self.webhook_data["message"]["dialog_id"]
            self.bot_id = self.webhook_data["bot_id"]
            self.client_id = self.webhook_data["user"]["id"]
            if not self.dialog_id or not self.bot_id or not self.client_id:
                raise ValueError("Missing required webhook fields")

            redis: Redis = await get_redis_client()
            key: str = f'user-{self.user.id}'

            if await redis.exists(key):
                if settings.MODE != 'test':
                    await self.send_response(
                        self.dialog_id,
                        "[B]Обрабатываю ваш предыдущий запрос. Пожалуйста, подождите завершения.[/B]",
                        self.bot_id,
                        self.client_id
                    )
                else:
                    raise HTTPException(status_code=429, detail="Previous request still processing")
            else:
                await redis.setex(key, 60, '')
                async with db_manager.session_scope() as db:
                    await self._do_webhook_processing(db, form_data)
        finally:
            await redis.delete(key)

    async def _do_webhook_processing(self, db: AsyncSession, form_data: dict) -> dict:
        """Main webhook processing with automatic error handling via chat."""
        
        # 1. Validate event type
        if not self._should_process_event(self.webhook_data):
            return {"action": "ignored", "reason": "invalid_event_or_bot_message"}

        # 2. Process message with error handling
        try:
            result = await self._process_user_message(
                db=db,
                message_text=self.webhook_data["message"]["text"],
                dialog_id=self.dialog_id,
                bot_id=self.bot_id,
                client_id=self.client_id
            )
            return result
            
        except Exception as e:
            logger.error(f"[bitrix] Error processing message: {e}")
            if settings.MODE != 'dev':
                await self.send_response(
                    self.dialog_id,
                    "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.",
                    self.bot_id,
                    self.client_id
                )
            return {"action": "error_sent_to_chat", "error": str(e)}
    
    async def _process_user_message(
        self, db: AsyncSession, message_text: str, dialog_id: str, bot_id: str, client_id: str
    ) -> dict:
        """Process user message - streamlined for background execution."""

        # 1. Get or create chat
        chat = await self._get_or_create_chat(db, dialog_id)

        # 2. Save user message
        await self.message_repo.create(db, MessageCreate(
            chat_id=chat.id,
            content=message_text,
            role=UserRole.USER,
        ))

        # 3. Get AI response
        ai_result = await self._get_ai_response(db, message_text, chat)
        
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
                dialog_id, bitrix_message, bot_id, client_id
            )

        return {
            "action": "message_processed",
            "ai_response": ai_result.answer,
            "chat_id": chat.id
        }

    def _should_process_event(self, webhook_data: dict) -> bool:
        """Check if we should process this webhook event."""
        event = webhook_data.get("event", "")
        message_text = webhook_data.get("message", {}).get("text", "")
        user_id = webhook_data.get("user", {}).get("id", "")
        bot_id = webhook_data.get("bot_id", "")
        
        # Only process message add events with text from non-bot users
        return (
            event == 'ONIMBOTMESSAGEADD'
            and message_text
            and user_id != bot_id
        )

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
            "bot_id": self.safe_get_form_value(form_data, 'data[BOT][357][BOT_ID]'),
        }

    async def _get_or_create_chat(self, db: AsyncSession, dialog_id: str) -> ChatOut:
        """Find or create chat for Bitrix dialog."""

        # Try to find existing chat for this user
        existing_chat = await self.chat_repo.get_last_created_by_user_id(
            db, self.user.id
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

    async def _get_ai_response(self, db: AsyncSession, message_text: str, chat: ChatOut) -> ResultPayload:
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
                    user_input=message_text
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
        self, dialog_id: str, message: str, bot_id: str, client_id: str
    ) -> bool:
        """Send AI response back to Bitrix24 chat."""
        
        payload = {
            "BOT_ID": bot_id,
            "CLIENT_ID": '354',
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
