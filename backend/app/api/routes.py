from fastapi import APIRouter, HTTPException
from app.domain.models import DocumentationRequest, DocumentationResponse
from app.services.documentation_service import DocumentationService
from app.core.config import settings

router = APIRouter()
documentation_service = DocumentationService()

@router.post("/generate", response_model=DocumentationResponse)
async def generate_documentation(request: DocumentationRequest):
    try:
        return await documentation_service.generate_documentation(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/config")
async def check_config():
    return {
        "openai_api_key": "present" if settings.OPENAI_API_KEY else "missing",
        "github_token": "present" if settings.GITHUB_TOKEN else "missing",
        "env_file": settings.Config.env_file
    } 