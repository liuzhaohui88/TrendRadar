# coding=utf-8
"""
新闻数据查询 API
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from trendradar.db import get_session, NewsItem

router = APIRouter(prefix="/news", tags=["新闻数据"])


@router.get("/")
def list_news(
    limit: int = Query(50, le=200),
    offset: int = 0,
    platform: Optional[str] = None,
    keyword: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """查询新闻列表"""
    query = select(NewsItem).order_by(NewsItem.last_seen_at.desc())

    if platform:
        query = query.where(NewsItem.platform_id == platform)
    if keyword:
        query = query.where(NewsItem.title.contains(keyword))

    query = query.offset(offset).limit(limit)
    news = session.exec(query).all()

    return {
        "items": news,
        "count": len(news),
        "offset": offset,
        "limit": limit
    }


@router.get("/stats")
def get_news_stats(session: Session = Depends(get_session)):
    """获取新闻统计"""
    from sqlmodel import func

    # 总数
    total = session.exec(select(func.count(NewsItem.id))).one()

    # 今日新增
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = session.exec(
        select(func.count(NewsItem.id)).where(NewsItem.first_seen_at >= today)
    ).one()

    # 按平台统计
    platform_stats = session.exec(
        select(NewsItem.platform_id, func.count(NewsItem.id))
        .group_by(NewsItem.platform_id)
    ).all()

    return {
        "total": total,
        "today": today_count,
        "by_platform": {p: c for p, c in platform_stats}
    }


@router.get("/{news_id}")
def get_news(news_id: int, session: Session = Depends(get_session)):
    """获取单条新闻详情"""
    news = session.get(NewsItem, news_id)
    if not news:
        return {"error": "新闻不存在"}
    return news
