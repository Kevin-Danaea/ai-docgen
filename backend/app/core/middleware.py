from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.core.exceptions import RateLimitError
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host
        
        # Limpiar solicitudes antiguas
        current_time = time.time()
        self.requests = {
            ip: timestamps 
            for ip, timestamps in self.requests.items()
            if current_time - timestamps[-1] < 60
        }
        
        # Verificar límite de solicitudes
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
                raise RateLimitError()
            self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        # Continuar con la solicitud
        response = await call_next(request)
        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": "Error interno del servidor"}
            ) 