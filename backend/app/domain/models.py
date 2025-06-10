from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum

class RepositoryType(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"

class Repository(BaseModel):
    url: HttpUrl
    type: RepositoryType
    branch: Optional[str] = "main"

class DocumentationRequest(BaseModel):
    repository: Repository
    generate_readme: bool = True
    generate_comments: bool = True
    generate_architecture: bool = True
    generate_checklist: bool = True

class DocumentationResponse(BaseModel):
    readme: Optional[str] = None
    comments: Optional[List[dict]] = None
    architecture: Optional[str] = None
    checklist: Optional[List[str]] = None

# Nuevos modelos para el análisis de repositorios
class FileInfo(BaseModel):
    name: str
    path: str
    type: str  # file, directory
    size: Optional[int] = None
    content: Optional[str] = None
    language: Optional[str] = None
    extension: Optional[str] = None

class RepositoryStructure(BaseModel):
    files: List[FileInfo]
    directories: List[FileInfo]
    main_files: List[FileInfo]  # README, requirements.txt, package.json, etc.
    source_files: List[FileInfo]  # Archivos de código fuente
    config_files: List[FileInfo]  # Archivos de configuración

class RepositoryAnalysis(BaseModel):
    structure: RepositoryStructure
    languages: Dict[str, int]  # Lenguajes y cantidad de archivos
    dependencies: Dict[str, List[str]]  # Dependencias por tipo (pip, npm, etc.)
    main_tech_stack: List[str]  # Tecnologías principales detectadas
    project_type: Optional[str] = None  # Web, CLI, Library, etc.
    complexity_score: Optional[float] = None  # Score de complejidad del proyecto 