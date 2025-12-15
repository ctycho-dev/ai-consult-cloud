import os
import tempfile
import aiofiles
import io
import time
import csv
from typing import Any
import asyncio
import io
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import NOT_GIVEN
from openai import (
    AsyncOpenAI,
    BadRequestError, NotFoundError, ConflictError,
    InternalServerError, RateLimitError, APIError
)
from app.domain.user.schema import UserOut
from app.domain.message.schema import ResultPayload, SourceInfo
from app.domain.file.repository import FileRepository
from app.domain.storage.repository import StorageRepository
from app.core.logger import get_logger
from app.core.decorators import log_timing


logger = get_logger()


class OpenAIManager:
    def __init__(
        self,
        client: AsyncOpenAI,
        file_repo: FileRepository,
        storage_repo: StorageRepository
    ):
        """
        Initialize OpenAIManager with OpenAI client and file repository.

        :param client: OpenAI client instance
        :param file_repo: File repository for file metadata access
        """
        self.client = client
        self.file_repo = file_repo
        self.storage_repo = storage_repo

    @log_timing("OpenAI:create_conversation")
    async def create_conversation(self, user_id: int) -> str:
        """
        Create a conversation for a specific user.

        :param user_id: ID of the user
        :return: Conversation ID string
        """
        conversation = await self.client.conversations.create(
            items=[],
            metadata={"user_id": f'user_{str(user_id)}'},
        )
        return conversation.id
    
    @log_timing("OpenAI:delete_conversation")
    async def delete_conversation(self, conv_id: str) -> None:
        """
        Delete conversation by ID.

        :param conv_id: Conversation ID
        """
        await self.client.conversations.delete(conv_id)

    async def is_conversation_active(self, conv_id: str) -> bool:
        start_time = time.perf_counter()
        try:
            await self.client.responses.create(
                model="gpt-4o-mini",
                conversation=conv_id,
                input=[{"role": "system", "content": "ping"}],  # Use list format to match expected input
            )
            elapsed = time.perf_counter() - start_time
            logger.info(f"is_conversation_active ping took {elapsed:.3f} seconds")
            return True
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.warning(f"Conversation {conv_id} inactive or invalid after {elapsed:.3f}s: {e}")
            return False

    async def create_response(
        self,
        db: AsyncSession,
        conv_id: str,
        user: UserOut,
        user_input: str
    ) -> ResultPayload:
        vector_store_ids = await self.get_vector_store_ids(db, user)
        tools_arg = self._get_user_tools(vector_store_ids)
        model = user.model or "gpt-4o-mini"

        instructions = None
        if user.source == 'bitrix':
            instructions = self._get_bitrix_instruction()
        else:
            # parts = [getattr(user, "user_instructions", None), getattr(user, "instructions", None)]
            # merged_instructions = "\n\n".join(p for p in parts if p).strip()
            # instructions = merged_instructions or NOT_GIVEN
            instructions = self._get_web_instruction()

        resp = await self.client.responses.create(
            model=model,
            tools=tools_arg or NOT_GIVEN,
            instructions=instructions,
            # conversation=conv_id,
            input=[{"role": "user", "content": user_input}],
            # temperature=0.7,
        )

        answer = ""
        sources = []
        
        for output_item in getattr(resp, "output", []):
            if getattr(output_item, "type", None) == "message":
                for content_item in getattr(output_item, "content", []):
                    if getattr(content_item, "type", None) == "output_text":
                        answer = content_item.text or ""
                        source_infos = await self.extract_sources_from_content(db, content_item)
                        sources.extend(source_infos)
        
        return ResultPayload(answer=answer, sources=sources)

    @log_timing("OpenAI:message")
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((InternalServerError, RateLimitError, APIError)),
        reraise=True
    )
    async def send_and_receive(
        self,
        db: AsyncSession,
        conv_id: str,
        user: UserOut,
        user_input: str
    ) -> ResultPayload:
        """
        Send user input and receive AI response with retry on transient errors.

        :param conv_id: Conversation ID
        :param user: UserOut instance containing model and tool info
        :param user_input: User message input string
        :return: ResultPayload containing answer and sources
        """
        try:
            # active = self.is_conversation_active(conv_id)
            # if not active:
            #     # Optionally create new conversation here or throw exception
            #     logger.warning(f"Conversation {conv_id} inactive, consider creating a new one.")

            return await self.create_response(db, conv_id, user, user_input)

        except (InternalServerError, RateLimitError, APIError) as e:
            logger.exception("OpenAIManager send_and_receive failed with retryable error: %s", e)
            raise
        except Exception as e:
            logger.exception("OpenAIManager unexpected error in send_and_receive: %s", e)
            raise

    @log_timing("OpenAI:create_file")
    async def create_file_from_path(self, path: str, vector_store_id: str):
        async with aiofiles.open(path, "rb") as f:
            file_content = await f.read()
        
        openai_file = await self.client.files.create(
            file=(path, file_content),
            purpose="assistants"
        )
        await self.client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=openai_file.id,
        )
        return openai_file

    @log_timing("OpenAI:delete_file")
    async def delete_file(
        self, vector_store_id: str, file_id: str, max_retries=3, delay=1
    ):
        """
        Deletes a file safely by detaching from vector store and removing from OpenAI storage with retries.

        :param vector_store_id: ID of vector store
        :param file_id: ID of file to delete
        :param max_retries: Number of retries if file is still attached
        :param delay: Delay between retries in seconds
        """
        client = self.client  # assuming sync client, you may need to wrap in a thread executor if using async
        # Step 1: Detach from vector store
        try:
            await client.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
        except NotFoundError:
            logger.info(f"File {file_id} not found in vector store {vector_store_id}, assuming already detached.")
            # fine, proceed
        except Exception as e:
            logger.error("Error detaching file from vector store: %s", e)
            raise

        # Step 2: Delete file from OpenAI
        for _ in range(max_retries):
            try:
                await client.files.delete(file_id)
                break  # Success!
            except NotFoundError:
                logger.info(f"File {file_id} already deleted from OpenAI storage.")
                break  # Success!
            except BadRequestError as e:
                logger.error("BadRequestError while deleting file from OpenAI: %s", e)
                raise e
            except ConflictError:
                logger.info("File %s still attached, retrying...", file_id)
                await asyncio.sleep(delay)
            except Exception as e:
                logger.error("Error deleting file from OpenAI: %s", e)
                raise

    def list_uploaded_files(self):
        """
        List uploaded files in OpenAI.

        :return: List of files metadata
        """
        try:
            pass
            # files = self.client.files.list()
            # return files.data
        except Exception as e:
            logger.exception("Failed to fetch uploaded files from OpenAI.")
            raise RuntimeError("Could not retrieve OpenAI files.") from e
    
    @log_timing("OpenAI:list_vector_store_files")
    async def list_vector_store_files(self, vector_store_id: str):
        """
        List all files attached to a specific vector store.
        """
        all_files = []
        after = None
        while True:
            page = await self.client.vector_stores.files.list(
                vector_store_id=vector_store_id,
                limit=100,
                after=after,
            )
            all_files.extend(page.data)

            # OpenAI returns a cursor (e.g. page.has_more / page.last_id / page.next_cursor)
            # Adjust field names to your actual client object.
            if not getattr(page, "has_more", False):
                break

            after = getattr(page, "last_id", None)
            if not after:
                break

        res = [file for file in all_files if file.status != 'completed']
        return res  # result.data is list[VectorStoreFile] [web:21][web:35]

    @log_timing("OpenAI:retrieve_file")
    async def retrieve_file(self, vector_store_id: str, file_id: str):
        """
        Retrieve OpenAI file metadata by file id.
        """
        vs_file = await self.client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )
        return vs_file

    async def get_vector_store_ids(
        self, db: AsyncSession, user: UserOut
    ) -> list[str]:
        """
        Get vector store IDs for user. Uses user's vector_store_ids if set,
        otherwise falls back to default storage.

        :param db: Database session
        :param user: UserOut instance
        :return: List of vector store IDs
        """
        # Priority 1: User's configured vector stores
        if user.vector_store_ids:
            return user.vector_store_ids
        
        # Priority 2: Default storage from storages table
        default_storage = await self.storage_repo.get_default_storage(db)
        if default_storage:
            return [default_storage.vector_store_id]
        
        logger.warning(
            "No vector stores found for user %s and no default storage configured",
            user.email
        )
        return []
    
    def _get_user_tools(
        self, vector_store_ids: list[str] | None
    ) -> list[dict[str, Any]]:
        """
        Build file_search tool configuration with vector store IDs.

        :param user: UserOut instance
        :param vector_store_ids: List of vector store IDs to use
        :return: List of tool dicts for OpenAI API
        """
        if not vector_store_ids:
            return []
        
        return [{
            "type": "file_search",
            "vector_store_ids": vector_store_ids,
        }]
    
    async def extract_sources_from_content(
        self,
        db: AsyncSession,
        content_item
    ) -> list[SourceInfo]:
        """
        Extract unique sources from the content annotations, avoiding duplicates.
        
        :param content_item: AI response content item with annotations
        :return: List of SourceInfo
        """
        sources = []
        seen_file_ids = set()
        for annotation in getattr(content_item, "annotations", []):
            if getattr(annotation, "type", None) == "file_citation":
                file_id = getattr(annotation, "file_id", None)
                if not file_id or file_id in seen_file_ids:
                    continue
                seen_file_ids.add(file_id)
                page = getattr(annotation, "page", None)
                source_info = await self.get_source_file(db, file_id, page)
                if source_info:
                    sources.append(source_info)
        return sources

    async def get_source_file(
        self, db: AsyncSession, file_id: str, page: int | None
    ) -> SourceInfo | None:
        """
        Retrieve file metadata by file id from repository.

        :param file_id: File storage key ID
        :param page: Page number (optional)
        :return: SourceInfo or None
        """
        file = await self.file_repo.get_by_storage_key(db, file_id)
        if not file:
            logger.warning("Source file %s not found in DB", file_id)
            return None
        source_info = SourceInfo(
            file_id=file.id,
            file_name=file.name,
            page=page
        )
        return source_info

    def _get_bitrix_instruction(self) -> str:
    
        return (
            "You are a professional AI assistant integrated into Bitrix24. Provide expert, accurate answers using the provided document context.\n\n"

            "MANDATORY SOURCE TRACKING:\n"
            "- ALWAYS reference the source file when using information\n"
            "- Include file references for all factual claims\n"
            "- When listing multiple items, indicate which document contains each item\n"
            
            "FORMATTING FOR BITRIX24:\n"
            "- Use BBCode formatting: [B]text[/B] for bold, not **text**\n"
            "- DO NOT use table BBCode - tables are not supported in chat\n"
            "- Structure data with bullet points and clear paragraphs\n"
            "- Use [I]italics[/I] for emphasis\n"
            "- Keep responses clear and business-focused\n\n"
            
            "FOR TABULAR DATA:\n"
            "- Use structured lists instead of tables\n"
            "- Format as: [B]Category:[/B] Details\n"
            "- Use bullet points for multiple items\n"
            "- Separate sections with line breaks\n\n"
            "- Never use pipes (|), dashes (---), or table-like formatting\n\n"
            
            "RESPONSE STYLE:\n"
            "- Start with a direct answer\n"
            "- Support with details from sources\n"
            "- Keep tone professional but conversational\n"
            "- Be honest about any limitations in the source material"
        )
    
    def _get_web_instruction(self) -> str:

        return (
            "You are an expert assistant. Use the provided context to answer accurately and clearly.\n\n"
        
            "FORMATTING:\n"
            "- Respond in **Markdown** format with structured headings and bullet points\n"
            "- Use tables for structured data when they enhance clarity\n"
            "- Apply appropriate emphasis and formatting for readability\n\n"
            
            "SOURCE REFERENCES:\n" 
            "- Reference source material when using specific information\n"
            "- Indicate when information comes from provided documents\n"
            "- Be transparent about source limitations or gaps\n\n"
            
            "RESPONSE QUALITY:\n"
            "- Provide comprehensive, well-structured answers\n"
            "- Be honest about limitations in the source material\n"
            "- Suggest what additional information might be helpful when relevant"
        )
