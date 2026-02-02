# coding=utf-8
"""
关键词策略管理 API

管理关键词组、必须词、排除词
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from trendradar.db import get_session, KeywordGroup

router = APIRouter(prefix="/keywords", tags=["关键词策略"])


class KeywordGroupCreate(BaseModel):
    name: str
    keywords: List[str] = []
    must_include: List[str] = []
    exclude: List[str] = []
    priority: int = 0
    enabled: bool = True


class KeywordGroupUpdate(BaseModel):
    name: Optional[str] = None
    keywords: Optional[List[str]] = None
    must_include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None


@router.get("/", response_model=List[KeywordGroup])
def list_keyword_groups(session: Session = Depends(get_session)):
    """获取所有关键词策略"""
    return session.exec(
        select(KeywordGroup).order_by(KeywordGroup.priority.desc(), KeywordGroup.id)
    ).all()


@router.get("/{group_id}", response_model=KeywordGroup)
def get_keyword_group(group_id: int, session: Session = Depends(get_session)):
    """获取单个关键词策略"""
    group = session.get(KeywordGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="关键词策略不存在")
    return group


@router.post("/", response_model=KeywordGroup)
def create_keyword_group(data: KeywordGroupCreate, session: Session = Depends(get_session)):
    """创建关键词策略"""
    group = KeywordGroup(
        name=data.name,
        keywords=data.keywords,
        must_include=data.must_include,
        exclude=data.exclude,
        priority=data.priority,
        enabled=data.enabled,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@router.put("/{group_id}", response_model=KeywordGroup)
def update_keyword_group(group_id: int, data: KeywordGroupUpdate, session: Session = Depends(get_session)):
    """更新关键词策略"""
    group = session.get(KeywordGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="关键词策略不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)
    group.updated_at = datetime.now()

    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@router.delete("/{group_id}")
def delete_keyword_group(group_id: int, session: Session = Depends(get_session)):
    """删除关键词策略"""
    group = session.get(KeywordGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="关键词策略不存在")
    session.delete(group)
    session.commit()
    return {"ok": True, "msg": f"关键词策略 {group.name} 已删除"}
