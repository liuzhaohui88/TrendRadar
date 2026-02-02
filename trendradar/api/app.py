# coding=utf-8
"""
FastAPI 应用主入口

功能：
- Token 认证机制
- 登录/登出接口
- 路由注册与鉴权
"""

import os
import secrets
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
from pydantic import BaseModel

from trendradar.db import init_db
from trendradar import __version__

# === 安全配置 ===
# 内存 Token 存储 (Token -> Expiry)
VALID_TOKENS: Dict[str, datetime] = {}
TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天过期

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """验证 Token，返回用户名"""
    # 1. 检查是否存在
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 检查是否过期
    expiry = VALID_TOKENS[token]
    if datetime.now() > expiry:
        del VALID_TOKENS[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return "admin"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"🚀 TrendRadar Nina v{__version__} API Server Starting...")
    init_db()
    yield
    print("👋 Shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="TrendRadar Nina API",
    version=__version__,
    description="智能热点情报分发中心 - Nina 扩展版",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 登录接口 ===
@app.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """登录获取 Token"""
    # 验证账号密码（从环境变量读取，默认 admin/trendradar）
    correct_user = os.environ.get("ADMIN_USER", "admin")
    correct_pass = os.environ.get("ADMIN_PASSWORD", "trendradar")

    if not (secrets.compare_digest(req.username, correct_user) and
            secrets.compare_digest(req.password, correct_pass)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 Token
    token = secrets.token_hex(16)
    expiry = datetime.now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    VALID_TOKENS[token] = expiry

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=correct_user
    )


@app.post("/api/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """登出"""
    if token in VALID_TOKENS:
        del VALID_TOKENS[token]
    return {"msg": "Logged out"}


# === 健康检查 ===
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": __version__,
        "service": "TrendRadar Nina"
    }


@app.get("/api/health")
async def health_check_api():
    """API 健康检查"""
    return {
        "status": "ok",
        "version": __version__,
        "service": "TrendRadar Nina API"
    }


# === 注册路由（延迟导入，避免循环依赖）===
def register_routes():
    """注册所有路由"""
    from trendradar.api.routes import sources, keywords, channels, rules, dashboard, news

    # 所有路由都需要登录
    auth_dependency = [Depends(get_current_user)]

    app.include_router(sources.router, prefix="/api", dependencies=auth_dependency)
    app.include_router(keywords.router, prefix="/api", dependencies=auth_dependency)
    app.include_router(channels.router, prefix="/api", dependencies=auth_dependency)
    app.include_router(rules.router, prefix="/api", dependencies=auth_dependency)
    app.include_router(dashboard.router, prefix="/api", dependencies=auth_dependency)
    app.include_router(news.router, prefix="/api", dependencies=auth_dependency)


# 注册路由
register_routes()


# === 静态文件与前端入口 ===
# 检查是否有前端构建产物
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    async def root():
        """Web 入口（不强制鉴权，加载登录页）"""
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """SPA 路由兜底"""
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
