# coding=utf-8
"""
推送渠道管理 API

管理飞书、钉钉、Telegram 等推送渠道
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from trendradar.db import get_session, Channel

router = APIRouter(prefix="/channels", tags=["推送渠道"])


class ChannelCreate(BaseModel):
    name: str
    type: str  # feishu | dingtalk | telegram | n8n | dify | ...
    config: Dict[str, Any] = {}
    enabled: bool = True


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


# 渠道类型说明
CHANNEL_TYPES = {
    "feishu": {"name": "飞书", "fields": ["webhook_url"]},
    "dingtalk": {"name": "钉钉", "fields": ["webhook_url"]},
    "wework": {"name": "企业微信", "fields": ["webhook_url", "msg_type"]},
    "telegram": {"name": "Telegram", "fields": ["bot_token", "chat_id"]},
    "email": {"name": "邮件", "fields": ["from", "password", "to", "smtp_server", "smtp_port"]},
    "n8n": {"name": "n8n", "fields": ["webhook_url", "auth_type", "auth_key", "auth_value"]},
    "dify": {"name": "Dify", "fields": ["api_url", "api_key", "input_variable"]},
    "bark": {"name": "Bark", "fields": ["url"]},
    "slack": {"name": "Slack", "fields": ["webhook_url"]},
    "generic": {"name": "通用 Webhook", "fields": ["webhook_url", "payload_template"]},
}


@router.get("/types")
def get_channel_types():
    """获取支持的渠道类型"""
    return CHANNEL_TYPES


@router.get("/", response_model=List[Channel])
def list_channels(session: Session = Depends(get_session)):
    """获取所有推送渠道"""
    return session.exec(select(Channel).order_by(Channel.id)).all()


@router.get("/{channel_id}", response_model=Channel)
def get_channel(channel_id: int, session: Session = Depends(get_session)):
    """获取单个推送渠道"""
    channel = session.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return channel


@router.post("/", response_model=Channel)
def create_channel(data: ChannelCreate, session: Session = Depends(get_session)):
    """创建推送渠道"""
    if data.type not in CHANNEL_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的渠道类型: {data.type}")

    channel = Channel(
        name=data.name,
        type=data.type,
        config=data.config,
        enabled=data.enabled,
    )
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel


@router.put("/{channel_id}", response_model=Channel)
def update_channel(channel_id: int, data: ChannelUpdate, session: Session = Depends(get_session)):
    """更新推送渠道"""
    channel = session.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "type" in update_data and update_data["type"] not in CHANNEL_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的渠道类型: {update_data['type']}")

    for key, value in update_data.items():
        setattr(channel, key, value)
    channel.updated_at = datetime.now()

    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, session: Session = Depends(get_session)):
    """删除推送渠道"""
    channel = session.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    session.delete(channel)
    session.commit()
    return {"ok": True, "msg": f"渠道 {channel.name} 已删除"}


@router.post("/{channel_id}/test")
def test_channel(channel_id: int, session: Session = Depends(get_session)):
    """测试推送渠道连通性"""
    channel = session.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    # 构造测试消息
    test_msg = f"🔔 TrendRadar Nina 测试消息\n\n渠道: {channel.name}\n类型: {channel.type}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✅ 连通性测试成功！"

    try:
        from trendradar.notification.senders import (
            send_to_feishu, send_to_dingtalk, send_to_wework,
            send_to_telegram, send_to_bark, send_to_slack
        )

        cfg = channel.config
        success = False

        if channel.type == "feishu":
            success = send_to_feishu(
                webhook_url=cfg.get("webhook_url"),
                report_data={"stats": [], "new_titles": {}, "failed_ids": []},
                report_type="测试消息",
                mode="current",
                split_content_func=lambda *args, **kwargs: [test_msg],
                get_time_func=datetime.now,
            )
        elif channel.type == "dingtalk":
            success = send_to_dingtalk(
                webhook_url=cfg.get("webhook_url"),
                report_data={"stats": [], "new_titles": {}, "failed_ids": []},
                report_type="测试消息",
                mode="current",
                split_content_func=lambda *args, **kwargs: [test_msg],
                get_time_func=datetime.now,
            )
        elif channel.type == "telegram":
            success = send_to_telegram(
                bot_token=cfg.get("bot_token"),
                chat_id=cfg.get("chat_id"),
                report_data={"stats": [], "new_titles": {}, "failed_ids": []},
                report_type="测试消息",
                mode="current",
                split_content_func=lambda *args, **kwargs: [test_msg],
                get_time_func=datetime.now,
            )
        else:
            # 通用 Webhook 测试
            import requests
            url = cfg.get("webhook_url") or cfg.get("url")
            if url:
                resp = requests.post(url, json={"text": test_msg}, timeout=10)
                success = resp.status_code < 400

        return {
            "ok": success,
            "msg": "✅ 测试成功" if success else "❌ 测试失败",
            "channel": channel.name
        }
    except Exception as e:
        return {"ok": False, "msg": f"❌ 测试失败: {str(e)}", "channel": channel.name}
