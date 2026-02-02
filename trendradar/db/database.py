# coding=utf-8
"""
数据库连接与会话管理

使用 SQLModel (SQLAlchemy 2.0 + Pydantic) 提供 ORM 功能
"""

import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

# 数据目录
DB_DIR = Path("output")
DB_DIR.mkdir(parents=True, exist_ok=True)

# 数据库文件 - Nina 扩展专用
SQLITE_FILE_NAME = "nina_dispatch.db"
SQLITE_URL = f"sqlite:///{DB_DIR / SQLITE_FILE_NAME}"

# 创建引擎
engine = create_engine(SQLITE_URL, echo=False)


def init_db():
    """初始化数据库表结构"""
    from . import models  # noqa: F401 - 导入模型以注册表结构
    SQLModel.metadata.create_all(engine)
    print(f"✅ Nina 扩展数据库已初始化: {SQLITE_URL}")


def get_session():
    """获取数据库会话 (FastAPI Dependency)"""
    with Session(engine) as session:
        yield session
