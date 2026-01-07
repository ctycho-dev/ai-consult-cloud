import io
import pytest
from httpx import AsyncClient

from app.domain.file.model import File
from app.enums.enums import FileState


class TestPublicFileAPI:
    async def test_secure_download_success(
        self,
        client: AsyncClient,
        session_factory,
        file_access_token_factory,
        s3_bytes: bytes,
        default_vector_store_id
    ):
        # 1) Seed a downloadable File in DB
        async with session_factory() as session:
            f = File(
                name="пример.pdf",
                vector_store_id=default_vector_store_id,
                s3_bucket="test-bucket",
                s3_object_key="public/пример.pdf",
                size=len(s3_bytes),
                content_type="application/pdf",
                status=FileState.STORED,
            )
            session.add(f)
            await session.commit()
            await session.refresh(f)
            file_id = f.id

        token = file_access_token_factory(file_id)

        # 3) Call public download endpoint
        r = await client.get("/api/v1/file/secure-download", params={"token": token})

        assert r.status_code == 200
        assert r.content == s3_bytes
        assert "content-disposition" in {k.lower() for k in r.headers.keys()}
        assert r.headers.get("content-length") == str(len(s3_bytes))

    async def test_secure_download_file_not_found(self, client: AsyncClient, file_access_token_factory):
        token = file_access_token_factory(99999999)

        r = await client.get("/api/v1/file/secure-download", params={"token": token})

        assert r.status_code == 404

    async def test_secure_download_invalid_token(self, client: AsyncClient):
        r = await client.get("/api/v1/file/secure-download", params={"token": "not-a-jwt"})

        assert r.status_code in (400, 401, 403)
