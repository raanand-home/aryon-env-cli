
from pydantic import BaseModel, Field
from typing import Optional, Dict
class EnvConfig(BaseModel):
    name: str = Field(..., description="Unique environment name")
    git_repo: str = Field(..., description="Git repository URL for the environment")
    follow_branch: Optional[str] = Field(default="main", description="Branch to follow for deployment")
    