import urllib
from fastapi import (
    HTTPException
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.file.repository import FileRepository
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client

from app.core.logger import get_logger

logger = get_logger()

CHUNK_SIZE = 1024 * 1024  # 1 MB


class PublicFileService:
    def __init__(
        self,
        db: AsyncSession,
        repo: FileRepository,
        s3_client: YandexS3Client,
    ):
        self.db = db
        self.repo = repo
        self.s3_client = s3_client

    async def download_file(self, file_id: int):

        file = await self.repo.get_by_id(self.db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail='File with provided id is not found.')
        
        if not file.s3_bucket or not file.s3_object_key:
            raise HTTPException(status_code=404, detail="File not available for download")
        
        # self.s3_client.download_file(file.s3_bucket, file.s3_object_key)
        def generate():
            response = self.s3_client._s3.get_object(
                Bucket=file.s3_bucket, 
                Key=file.s3_object_key
            )
            stream = response['Body']
            try:
                while chunk := stream.read(CHUNK_SIZE):
                    yield chunk
            finally:
                stream.close()

        # Build headers dict, only include Content-Length if size is known
        headers = {}
    
        if file.name:
            # Create a fallback ASCII filename by removing/replacing problematic characters
            ascii_filename = file.name.encode('ascii', 'ignore').decode('ascii')
            if not ascii_filename:
                ascii_filename = "download"

            # RFC 5987 encoded filename for full Unicode support
            encoded_filename = urllib.parse.quote(file.name, safe='')

            # Include both for maximum browser compatibility
            headers["Content-Disposition"] = (
                f'attachment; filename="{ascii_filename}"; '
                f"filename*=UTF-8''{encoded_filename}"
            )
            headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        # if file.size:
        #     headers["Content-Length"] = str(file.size)

        return StreamingResponse(
            generate(),
            media_type=file.content_type or "application/octet-stream",
            headers=headers
        )
