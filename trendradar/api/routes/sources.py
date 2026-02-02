# coding=utf-8
"""
数据源管理 API

管理热榜平台和 RSS 订阅源
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from trendradar.db import get_session, Source

router = APIRouter(prefix="/sources", tags=["数据源管理"])


class SourceCreate(BaseModel):
    name: str
    type: str  # platform | rss
    target: str
    description: Optional[str] = None
    enabled: bool = True


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    target: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("/", response_model=List[Source])
def list_sources(session: Session = Depends(get_session)):
    """获取所有数据源"""
    return session.exec(select(Source).order_by(Source.type, Source.id)).all()


@router.get("/{source_id}", response_model=Source)
def get_source(source_id: int, session: Session = Depends(get_session)):
    """获取单个数据源"""
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return source


@router.post("/", response_model=Source)
def create_source(data: SourceCreate, session: Session = Depends(get_session)):
    """创建数据源"""
    source = Source(
        name=data.name,
        type=data.type,
        target=data.target,
        description=data.description,
        enabled=data.enabled,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.put("/{source_id}", response_model=Source)
def update_source(source_id: int, data: SourceUpdate, session: Session = Depends(get_session)):
    """更新数据源"""
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(source, key, value)
    source.updated_at = datetime.now()

    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.delete("/{source_id}")
def delete_source(source_id: int, session: Session = Depends(get_session)):
    """删除数据源"""
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    session.delete(source)
    session.commit()
    return {"ok": True, "msg": f"数据源 {source.name} 已删除"}
