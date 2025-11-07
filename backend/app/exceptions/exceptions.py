from fastapi import FastAPI, HTTPException, status


class NotFoundError(Exception):
    """Raised when a resource is not found."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class RepositoryError(Exception):
    """Raised when an error occurs in the repository."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DatabaseError(Exception):
    """Exception raised for database-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ExternalServiceError(Exception):
    """Exception raised for database-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request, exc: NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request, exc: ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request, exc: DatabaseError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message
        )

    @app.exception_handler(RepositoryError)
    async def repository_error_handler(request, exc: RepositoryError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message
        )

    @app.exception_handler(RepositoryError)
    async def external_error_handler(request, exc: ExternalServiceError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message
        )
