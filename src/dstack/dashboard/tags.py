from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dstack.backend import load_backend

router = APIRouter(prefix="/api/tags", tags=["tags"])


class ArtifactHeadItem(BaseModel):
    job_id: str
    artifact_path: str


class TagItem(BaseModel):
    repo_user_name: str
    repo_name: str
    tag_name: str
    run_name: str
    workflow_name: Optional[str]
    provider_name: Optional[str]
    created_at: int
    artifact_heads: Optional[List[ArtifactHeadItem]]


class QueryTagsResponse(BaseModel):
    tags: List[TagItem]


class DeleteTagRequest(BaseModel):
    repo_user_name: str
    repo_name: str
    tag_name: str


class AddTagRequest(BaseModel):
    repo_user_name: str
    repo_name: str
    run_name: str
    tag_name: str


@router.get("/query", response_model=QueryTagsResponse)
async def query(repo_user_name: str, repo_name: str) -> QueryTagsResponse:
    backend = load_backend()
    tag_heads = backend.list_tag_heads(repo_user_name, repo_name)
    return QueryTagsResponse(
        tags=[TagItem(repo_user_name=t.repo_user_name,
                      repo_name=t.repo_name,
                      tag_name=t.tag_name,
                      run_name=t.run_name,
                      workflow_name=t.workflow_name,
                      provider_name=t.provider_name,
                      created_at=t.created_at,
                      artifact_heads=[
                          ArtifactHeadItem(job_id=a.job_id, artifact_path=a.artifact_path)
                          for a in t.artifact_heads
                      ] if t.artifact_heads else None) for t in tag_heads])


@router.post("/delete")
async def delete(request: DeleteTagRequest):
    backend = load_backend()
    tag_head = backend.get_tag_head(request.repo_user_name, request.repo_name, request.tag_name)
    if tag_head:
        backend.delete_tag_head(request.repo_user_name, request.repo_name, tag_head)
    else:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.post("/add")
async def delete(request: AddTagRequest):
    backend = load_backend()
    backend.add_tag_from_run(request.repo_user_name, request.repo_name, request.tag_name, request.run_name)