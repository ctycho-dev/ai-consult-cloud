import logging
import time
import uuid
from contextvars import ContextVar
from starlette.types import ASGIApp
from starlette.requests import Request

logger = logging.getLogger("app.access")
_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_user_email: ContextVar[str | None] = ContextVar("user_email", default=None)


def get_request_id() -> str:
    return _request_id.get()


def get_user_email() -> str | None:
    return _user_email.get()


def set_user_email(email: str | None, request: Request = None) -> None:
    _user_email.set(email)
    if request:
        request.scope["user_email"] = email


class RequestIDFilter(logging.Filter):
    """Inject request_id and user_email from ContextVar into every log record."""
    
    def filter(self, record):
        record.request_id = get_request_id()
        record.user_email = get_user_email() or "anonymous"
        return True


class AccessLogMiddleware:

    SKIP_PATHS = {"/health", "/metrics", "/favicon.ico"}

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        if scope["path"] in self.SKIP_PATHS:
            return await self.app(scope, receive, send)
        
        headers = dict(scope.get("headers") or [])

        rid = dict(scope["headers"]).get(b"x-request-id", b"").decode() or str(uuid.uuid4())
        token = _request_id.set(rid)
        start = time.perf_counter()
        scope["user_email"] = None


        # ---- Extract debug info (Bitrix visibility) ----
        xff = headers.get(b"x-forwarded-for", b"").decode()
        xri = headers.get(b"x-real-ip", b"").decode()

        client_ip = None
        if xff:
            client_ip = xff.split(",")[0].strip()
        elif xri:
            client_ip = xri.strip()
        elif scope.get("client"):
            client_ip = scope["client"][0]

        user_agent = headers.get(b"user-agent", b"").decode()
        content_type = headers.get(b"content-type", b"").decode()
        content_length = headers.get(b"content-length", b"").decode()
        host = headers.get(b"host", b"").decode()

        # Log request start (so we know if Bitrix hits at all)
        logger.info("http_request_start", extra={
            "method": scope.get("method"),
            "path": scope.get("path"),
            "client_ip": client_ip,
            "host": host or None,
            "user_agent": user_agent or None,
            "content_type": content_type or None,
            "content_length": content_length or None,
        })

        async def send_wrapper(message):

            if message["type"] == "http.response.start":
                duration_s = time.perf_counter() - start
                query_string = scope.get("query_string", b"").decode()

                logger.info("http_request", extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "query_params": query_string if query_string else None,
                    "status_code": message["status"],
                    "latency_s": round(duration_s, 3),
                })
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            _request_id.reset(token)
