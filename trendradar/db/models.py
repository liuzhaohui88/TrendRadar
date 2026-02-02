# coding=utf-8
"""
数据模型定义

Nina 扩展的核心数据表：
- SystemConfig: 系统全局配置
- KeywordGroup: 关键词策略
- Source: 数据源（平台/RSS）
- Channel: 推送渠道
- DispatchRule: 分发规则（核心：源 -> 策略 -> 渠道）
- NewsItem: 新闻数据
- PushLog: 推送日志
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON


class SystemConfig(SQLModel, table=True):
    """系统全局配置"""
    key: str = Field(primary_key=True, description="配置键")
    value: str = Field(description="配置值")
    description: Optional[str] = Field(default=None, description="配置说明")
    updated_at: datetime = Field(default_factory=datetime.now)


class KeywordGroup(SQLModel, table=True):
    """
    关键词策略

    支持多种匹配规则：
    - keywords: 普通关键词列表
    - must_include: 必须同时包含的词
    - exclude: 排除词（命中则过滤）
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="策略名称")

    keywords: List[str] = Field(default=[], sa_type=JSON, description="关键词列表")
    must_include: List[str] = Field(default=[], sa_type=JSON, description="必须包含")
    exclude: List[str] = Field(default=[], sa_type=JSON, description="排除词")

    priority: int = Field(default=0, description="优先级（数字越大越优先）")
    enabled: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Source(SQLModel, table=True):
    """
    数据源 - 统一管理热榜平台和 RSS

    type:
    - platform: 热榜平台，target 为平台 ID（如 weibo, zhihu）
    - rss: RSS 订阅，target 为订阅 URL
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="显示名称")
    type: str = Field(description="类型: platform | rss")
    target: str = Field(description="目标标识（Platform ID 或 RSS URL）")

    description: Optional[str] = Field(default=None)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Channel(SQLModel, table=True):
    """
    推送渠道

    type: 渠道类型
    - feishu: 飞书
    - dingtalk: 钉钉
    - wework: 企业微信
    - telegram: Telegram
    - email: 邮件
    - n8n: n8n Webhook
    - dify: Dify API
    - bark: Bark
    - slack: Slack
    - generic: 通用 Webhook

    config: 渠道配置（JSON 格式，根据类型不同存储不同字段）
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="渠道名称")
    type: str = Field(description="渠道类型")
    config: Dict = Field(default={}, sa_type=JSON, description="连接配置")

    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DispatchRule(SQLModel, table=True):
    """
    分发规则 - Nina 扩展核心

    实现精准分流：源 -> 策略 -> 渠道

    - source_ids: 从哪些数据源抓取
    - keyword_group_ids: 用哪些关键词策略过滤
    - channel_ids: 推送到哪些渠道
    - cron: 独立调度表达式
    - report_mode: 报告模式（daily/current/incremental）
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="规则名称")

    # 关联三要素：源 -> 策略 -> 渠道
    source_ids: List[int] = Field(default=[], sa_type=JSON, description="数据源 ID 列表")
    keyword_group_ids: List[int] = Field(default=[], sa_type=JSON, description="关键词策略 ID 列表")
    channel_ids: List[int] = Field(default=[], sa_type=JSON, description="推送渠道 ID 列表")

    # 调度配置
    cron: str = Field(default="*/10 * * * *", description="Cron 表达式")
    interval_seconds: int = Field(default=600, description="执行间隔（秒）")

    # 报告配置
    report_mode: str = Field(default="incremental", description="报告模式: daily | current | incremental")

    enabled: bool = Field(default=True)
    last_run_at: Optional[datetime] = Field(default=None, description="上次执行时间")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class NewsItem(SQLModel, table=True):
    """
    新闻数据

    存储抓取到的新闻，记录命中的规则
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[int] = Field(default=None, index=True, description="数据源 ID")

    platform_id: str = Field(index=True, description="平台标识")
    title: str = Field(index=True, description="标题")
    url: str = Field(description="链接")
    mobile_url: Optional[str] = Field(default=None, description="移动端链接")

    first_seen_at: datetime = Field(description="首次发现时间")
    last_seen_at: datetime = Field(description="最后发现时间")

    highest_rank: int = Field(default=0, description="最高排名")
    hit_count: int = Field(default=1, description="命中次数")

    # 命中记录
    matched_group_ids: List[int] = Field(default=[], sa_type=JSON, description="命中的关键词策略 ID")

    raw_data: Optional[Dict] = Field(default=None, sa_type=JSON, description="原始数据")


class PushLog(SQLModel, table=True):
    """
    推送日志

    记录每次推送的状态和结果
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: Optional[int] = Field(default=None, index=True, description="规则 ID")
    channel_id: Optional[int] = Field(default=None, index=True, description="渠道 ID")
    channel_name: str = Field(description="渠道名称")

    status: str = Field(description="状态: success | failed")
    message: Optional[str] = Field(default=None, description="消息/错误信息")
    news_count: int = Field(default=0, description="推送新闻数量")

    created_at: datetime = Field(default_factory=datetime.now)
