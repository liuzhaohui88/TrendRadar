# coding=utf-8
"""
仪表盘 API

提供统计数据和概览信息
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from trendradar.db import get_session, Source, KeywordGroup, Channel, DispatchRule, PushLog

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    """获取仪表盘统计数据"""
    # 各类资源数量
    source_count = session.exec(select(func.count(Source.id))).one()
    keyword_count = session.exec(select(func.count(KeywordGroup.id))).one()
    channel_count = session.exec(select(func.count(Channel.id))).one()
    rule_count = session.exec(select(func.count(DispatchRule.id))).one()

    # 启用状态统计
    enabled_sources = session.exec(
        select(func.count(Source.id)).where(Source.enabled == True)
    ).one()
    enabled_rules = session.exec(
        select(func.count(DispatchRule.id)).where(DispatchRule.enabled == True)
    ).one()

    # 今日推送统计
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_push_count = session.exec(
        select(func.count(PushLog.id)).where(PushLog.created_at >= today)
    ).one()
    today_success_count = session.exec(
        select(func.count(PushLog.id)).where(
            PushLog.created_at >= today,
            PushLog.status == "success"
        )
    ).one()

    return {
        "sources": {"total": source_count, "enabled": enabled_sources},
        "keywords": {"total": keyword_count},
        "channels": {"total": channel_count},
        "rules": {"total": rule_count, "enabled": enabled_rules},
        "push_today": {"total": today_push_count, "success": today_success_count},
    }


@router.get("/recent-logs")
def get_recent_logs(limit: int = 20, session: Session = Depends(get_session)):
    """获取最近的推送日志"""
    logs = session.exec(
        select(PushLog).order_by(PushLog.created_at.desc()).limit(limit)
    ).all()
    return logs


@router.get("/rules-summary")
def get_rules_summary(session: Session = Depends(get_session)):
    """获取规则概览（含最后执行时间）"""
    rules = session.exec(select(DispatchRule).order_by(DispatchRule.id)).all()

    result = []
    for rule in rules:
        # 获取关联的渠道名称
        channels = session.exec(
            select(Channel).where(Channel.id.in_(rule.channel_ids))
        ).all()

        result.append({
            "id": rule.id,
            "name": rule.name,
            "enabled": rule.enabled,
            "report_mode": rule.report_mode,
            "interval_seconds": rule.interval_seconds,
            "last_run_at": rule.last_run_at,
            "channels": [c.name for c in channels],
        })

    return result
