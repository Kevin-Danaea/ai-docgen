from pydantic import BaseModel, HttpUrl
from typing import List, Optional
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