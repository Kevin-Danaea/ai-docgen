from app.domain.models import DocumentationRequest, DocumentationResponse
from app.infrastructure.repository_analyzer import RepositoryAnalyzer
from app.infrastructure.ai_service import AIService
from app.infrastructure.code_parser import CodeParser

class DocumentationService:
    def __init__(self):
        self.repository_analyzer = RepositoryAnalyzer()
        self.ai_service = AIService()
        self.code_parser = CodeParser()

    async def generate_documentation(self, request: DocumentationRequest) -> DocumentationResponse:
        # Analizar el repositorio
        repo_content = await self.repository_analyzer.analyze_repository(request.repository)
        
        # Parsear el código
        parsed_code = self.code_parser.parse_code(repo_content)
        
        # Generar documentación usando IA
        documentation = await self.ai_service.generate_documentation(parsed_code, request)
        
        return DocumentationResponse(
            readme=documentation.get("readme"),
            comments=documentation.get("comments"),
            architecture=documentation.get("architecture"),
            checklist=documentation.get("checklist")
        ) 