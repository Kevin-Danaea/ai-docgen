import httpx
from app.domain.models import Repository
from typing import Dict, Any

class RepositoryAnalyzer:
    async def analyze_repository(self, repository: Repository) -> Dict[str, Any]:
        """
        Analiza un repositorio y devuelve su contenido y estructura.
        """
        if repository.type == "github":
            return await self._analyze_github_repository(repository)
        else:
            raise NotImplementedError(f"Análisis de repositorios {repository.type} no implementado")

    async def _analyze_github_repository(self, repository: Repository) -> Dict[str, Any]:
        """
        Analiza un repositorio de GitHub.
        """
        # Extraer owner y repo del URL
        url_parts = str(repository.url).split("/")
        owner = url_parts[-2]
        repo = url_parts[-1].replace(".git", "")

        async with httpx.AsyncClient() as client:
            # Obtener información básica del repositorio
            repo_info = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            repo_info.raise_for_status()

            # Obtener contenido del repositorio
            contents = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            contents.raise_for_status()

            return {
                "info": repo_info.json(),
                "contents": contents.json()
            } 