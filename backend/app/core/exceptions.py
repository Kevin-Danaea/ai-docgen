from fastapi import HTTPException, status

class RepositoryError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el repositorio: {detail}"
        )

class RepositoryNotFoundError(RepositoryError):
    def __init__(self, repo_url: str):
        super().__init__(f"Repositorio no encontrado: {repo_url}")

class RepositoryAccessError(RepositoryError):
    def __init__(self, repo_url: str):
        super().__init__(f"No se puede acceder al repositorio: {repo_url}")

class FileAnalysisError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el análisis de archivos: {detail}"
        )

class AIServiceError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servicio de IA: {detail}"
        )

class RateLimitError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Límite de solicitudes excedido"
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {detail}"
        ) 