# coding=utf-8
"""
分发规则管理 API

核心功能：配置 源 -> 策略 -> 渠道 的分发规则
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from trendradar.db import get_session, DispatchRule, Channel, KeywordGroup, Source

router = APIRouter(prefix="/rules", tags=["分发规则"])


class RuleCreate(BaseModel):
    name: str
    source_ids: List[int] = []
    keyword_group_ids: List[int] = []
    channel_ids: List[int] = []
    cron: str = "*/10 * * * *"
    interval_seconds: int = 600
    report_mode: str = "incremental"
    enabled: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    source_ids: Optional[List[int]] = None
    keyword_group_ids: Optional[List[int]] = None
    channel_ids: Optional[List[int]] = None
    cron: Optional[str] = None
    interval_seconds: Optional[int] = None
    report_mode: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("/", response_model=List[DispatchRule])
def list_rules(session: Session = Depends(get_session)):
    """获取所有分发规则"""
    return session.exec(select(DispatchRule).order_by(DispatchRule.id)).all()


@router.get("/{rule_id}", response_model=DispatchRule)
def get_rule(rule_id: int, session: Session = Depends(get_session)):
    """获取单个分发规则"""
    rule = session.get(DispatchRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule


@router.get("/{rule_id}/detail")
def get_rule_detail(rule_id: int, session: Session = Depends(get_session)):
    """获取规则详情（含关联的源、策略、渠道名称）"""
    rule = session.get(DispatchRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    # 获取关联对象
    sources = session.exec(select(Source).where(Source.id.in_(rule.source_ids))).all()
    keywords = session.exec(select(KeywordGroup).where(KeywordGroup.id.in_(rule.keyword_group_ids))).all()
    channels = session.exec(select(Channel).where(Channel.id.in_(rule.channel_ids))).all()

    return {
        "rule": rule,
        "sources": [{"id": s.id, "name": s.name, "type": s.type} for s in sources],
        "keywords": [{"id": k.id, "name": k.name} for k in keywords],
        "channels": [{"id": c.id, "name": c.name, "type": c.type} for c in channels],
    }


@router.post("/", response_model=DispatchRule)
def create_rule(data: RuleCreate, session: Session = Depends(get_session)):
    """创建分发规则"""
    rule = DispatchRule(
        name=data.name,
        source_ids=data.source_ids,
        keyword_group_ids=data.keyword_group_ids,
        channel_ids=data.channel_ids,
        cron=data.cron,
        interval_seconds=data.interval_seconds,
        report_mode=data.report_mode,
        enabled=data.enabled,
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=DispatchRule)
def update_rule(rule_id: int, data: RuleUpdate, session: Session = Depends(get_session)):
    """更新分发规则"""
    rule = session.get(DispatchRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    rule.updated_at = datetime.now()

    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, session: Session = Depends(get_session)):
    """删除分发规则"""
    rule = session.get(DispatchRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    session.delete(rule)
    session.commit()
    return {"ok": True, "msg": f"规则 {rule.name} 已删除"}


@router.post("/{rule_id}/test")
def test_rule(rule_id: int, session: Session = Depends(get_session)):
    """测试分发规则（发送测试消息到目标渠道）"""
    rule = session.get(DispatchRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    if not rule.channel_ids:
        return {"ok": False, "msg": "规则未配置目标渠道"}

    # 获取目标渠道
    channels = session.exec(select(Channel).where(Channel.id.in_(rule.channel_ids))).all()
    if not channels:
        return {"ok": False, "msg": "目标渠道不存在"}

    # 构造测试消息
    test_msg = f"""🔔 **TrendRadar Nina 规则测试**

规则名称: {rule.name}
报告模式: {rule.report_mode}
调度间隔: {rule.interval_seconds}秒
目标渠道: {', '.join([c.name for c in channels])}

✅ 规则连通性测试成功！"""

    results = []
    for ch in channels:
        try:
            from trendradar.notification.senders import send_to_feishu, send_to_dingtalk

            cfg = ch.config
            success = False

            if ch.type == "feishu":
                success = send_to_feishu(
                    webhook_url=cfg.get("webhook_url"),
                    report_data={"stats": [], "new_titles": {}, "failed_ids": []},
                    report_type=f"规则测试: {rule.name}",
                    mode=rule.report_mode,
                    split_content_func=lambda *args, **kwargs: [test_msg],
                    get_time_func=datetime.now,
                )
            elif ch.type == "dingtalk":
                success = send_to_dingtalk(
                    webhook_url=cfg.get("webhook_url"),
                    report_data={"stats": [], "new_titles": {}, "failed_ids": []},
                    report_type=f"规则测试: {rule.name}",
                    mode=rule.report_mode,
                    split_content_func=lambda *args, **kwargs: [test_msg],
                    get_time_func=datetime.now,
                )
            else:
                # 通用处理
                import requests
                url = cfg.get("webhook_url") or cfg.get("url")
                if url:
                    resp = requests.post(url, json={"text": test_msg}, timeout=10)
                    success = resp.status_code < 400

            results.append(f"{ch.name}: {'✅' if success else '❌'}")
        except Exception as e:
            results.append(f"{ch.name}: ❌ ({str(e)[:50]})")

    return {"ok": True, "msg": " | ".join(results)}
