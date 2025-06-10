import httpx
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from app.domain.models import Repository, FileInfo, RepositoryStructure, RepositoryAnalysis
from app.core.config import settings

class RepositoryAnalyzer:
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {settings.GITHUB_TOKEN}"
        }

    async def analyze_repository(self, repository: Repository) -> RepositoryAnalysis:
        """
        Analiza un repositorio y devuelve información detallada sobre su estructura y contenido.
        """
        if repository.type == "github":
            return await self._analyze_github_repository(repository)
        else:
            raise NotImplementedError(f"Análisis de repositorios {repository.type} no implementado")

    async def _analyze_github_repository(self, repository: Repository) -> RepositoryAnalysis:
        """
        Analiza un repositorio de GitHub.
        """
        # Extraer owner y repo del URL
        url_parts = str(repository.url).split("/")
        owner = url_parts[-2]
        repo = url_parts[-1].replace(".git", "")

        async with httpx.AsyncClient() as client:
            # Obtener información básica del repositorio
            repo_info = await self._get_repo_info(client, owner, repo)
            
            # Obtener estructura del repositorio
            structure = await self._get_repository_structure(client, owner, repo, repository.branch)
            
            # Analizar lenguajes
            languages = await self._get_languages(client, owner, repo)
            
            # Analizar dependencias
            dependencies = await self._analyze_dependencies(structure)
            
            # Determinar tipo de proyecto y stack tecnológico
            project_type, tech_stack = self._analyze_project_type(structure, languages)
            
            # Calcular score de complejidad
            complexity_score = self._calculate_complexity_score(structure, languages)

            return RepositoryAnalysis(
                structure=structure,
                languages=languages,
                dependencies=dependencies,
                main_tech_stack=tech_stack,
                project_type=project_type,
                complexity_score=complexity_score
            )

    async def _get_repo_info(self, client: httpx.AsyncClient, owner: str, repo: str) -> Dict[str, Any]:
        """Obtiene información básica del repositorio."""
        response = await client.get(
            f"{self.github_api_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def _get_repository_structure(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        branch: str
    ) -> RepositoryStructure:
        """Obtiene la estructura completa del repositorio."""
        files: List[FileInfo] = []
        directories: List[FileInfo] = []
        main_files: List[FileInfo] = []
        source_files: List[FileInfo] = []
        config_files: List[FileInfo] = []

        async def process_directory(path: str = ""):
            response = await client.get(
                f"{self.github_api_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                params={"ref": branch}
            )
            response.raise_for_status()
            items = response.json()

            for item in items:
                file_info = FileInfo(
                    name=item["name"],
                    path=item["path"],
                    type=item["type"],
                    size=item.get("size"),
                    extension=Path(item["name"]).suffix
                )

                if item["type"] == "dir":
                    directories.append(file_info)
                    await process_directory(item["path"])
                else:
                    files.append(file_info)
                    
                    # Clasificar archivos
                    if self._is_main_file(item["name"]):
                        main_files.append(file_info)
                    elif self._is_source_file(item["name"]):
                        source_files.append(file_info)
                    elif self._is_config_file(item["name"]):
                        config_files.append(file_info)

        await process_directory()
        return RepositoryStructure(
            files=files,
            directories=directories,
            main_files=main_files,
            source_files=source_files,
            config_files=config_files
        )

    async def _get_languages(self, client: httpx.AsyncClient, owner: str, repo: str) -> Dict[str, int]:
        """Obtiene los lenguajes utilizados en el repositorio."""
        response = await client.get(
            f"{self.github_api_url}/repos/{owner}/{repo}/languages",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def _analyze_dependencies(self, structure: RepositoryStructure) -> Dict[str, List[str]]:
        """Analiza las dependencias del proyecto."""
        dependencies = {
            "python": [],
            "node": [],
            "other": []
        }

        for file in structure.main_files:
            if file.name == "requirements.txt":
                content = await self._get_file_content(file.path)
                if content:
                    dependencies["python"] = self._parse_requirements(content)
            elif file.name == "package.json":
                content = await self._get_file_content(file.path)
                if content:
                    dependencies["node"] = self._parse_package_json(content)

        return dependencies

    def _analyze_project_type(
        self, 
        structure: RepositoryStructure, 
        languages: Dict[str, int]
    ) -> tuple[Optional[str], List[str]]:
        """Determina el tipo de proyecto y su stack tecnológico."""
        tech_stack = []
        project_type = None

        # Analizar lenguajes principales
        main_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
        tech_stack.extend([lang for lang, _ in main_languages])

        # Determinar tipo de proyecto
        if any(file.name == "package.json" for file in structure.main_files):
            project_type = "web" if any(file.name.endswith(".html") for file in structure.files) else "node"
        elif any(file.name == "requirements.txt" for file in structure.main_files):
            if any(file.name.endswith(".py") for file in structure.files):
                project_type = "python"
        elif any(file.name.endswith(".java") for file in structure.files):
            project_type = "java"
        elif any(file.name.endswith(".go") for file in structure.files):
            project_type = "go"

        return project_type, tech_stack

    def _calculate_complexity_score(
        self, 
        structure: RepositoryStructure, 
        languages: Dict[str, int]
    ) -> float:
        """Calcula un score de complejidad del proyecto."""
        score = 0.0
        
        # Factor 1: Cantidad de archivos
        score += len(structure.files) * 0.1
        
        # Factor 2: Cantidad de lenguajes
        score += len(languages) * 0.2
        
        # Factor 3: Profundidad de directorios
        max_depth = max(len(Path(file.path).parts) for file in structure.files)
        score += max_depth * 0.15
        
        # Factor 4: Cantidad de archivos de configuración
        score += len(structure.config_files) * 0.1
        
        return min(score, 10.0)  # Normalizar a un máximo de 10

    def _is_main_file(self, filename: str) -> bool:
        """Determina si un archivo es un archivo principal del proyecto."""
        main_files = {
            "README.md", "requirements.txt", "package.json", "setup.py",
            "pyproject.toml", "go.mod", "pom.xml", "build.gradle"
        }
        return filename in main_files

    def _is_source_file(self, filename: str) -> bool:
        """Determina si un archivo es un archivo de código fuente."""
        source_extensions = {
            ".py", ".js", ".ts", ".java", ".go", ".rb", ".php",
            ".cpp", ".c", ".h", ".hpp", ".cs", ".swift"
        }
        return Path(filename).suffix in source_extensions

    def _is_config_file(self, filename: str) -> bool:
        """Determina si un archivo es un archivo de configuración."""
        config_files = {
            ".env", ".env.example", "config.json", "config.yaml",
            "config.yml", ".gitignore", ".dockerignore", "Dockerfile",
            "docker-compose.yml", "docker-compose.yaml"
        }
        return filename in config_files

    async def _get_file_content(self, path: str) -> Optional[str]:
        """Obtiene el contenido de un archivo del repositorio."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.github_api_url}/repos/{path}",
                    headers=self.headers
                )
                response.raise_for_status()
                content = response.json().get("content", "")
                if content:
                    return base64.b64decode(content).decode("utf-8")
        except Exception as e:
            print(f"Error getting file content: {e}")
        return None

    def _parse_requirements(self, content: str) -> List[str]:
        """Parsea un archivo requirements.txt."""
        requirements = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line.split("==")[0])
        return requirements

    def _parse_package_json(self, content: str) -> List[str]:
        """Parsea un archivo package.json."""
        try:
            import json
            data = json.loads(content)
            dependencies = []
            if "dependencies" in data:
                dependencies.extend(data["dependencies"].keys())
            if "devDependencies" in data:
                dependencies.extend(data["devDependencies"].keys())
            return dependencies
        except Exception as e:
            print(f"Error parsing package.json: {e}")
            return [] 