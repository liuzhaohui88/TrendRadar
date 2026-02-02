# TrendRadar Nina 部署指南

> 基于官方 TrendRadar v5.5.0 的 Nina 扩展版部署文档

## 前置条件

- 服务器已安装 Docker
- 已有 Nginx 反向代理（可选，用于域名访问）
- 已有 Let's Encrypt 证书工具（可选，用于 HTTPS）

## 一、上传代码到服务器

```bash
# 创建项目目录
mkdir -p /root/trendradar
cd /root/trendradar

# 上传以下文件/目录到服务器：
# - Dockerfile.nina
# - docker-compose.nina.yml
# - trendradar/          (后端代码)
# - frontend/dist/       (前端构建产物)
# - pyproject.toml
# - requirements.txt
# - config/              (配置文件目录，如已有可保留)
```

## 二、构建 Docker 镜像

```bash
cd /root/trendradar
docker build -t trendradar-nina:5.5.0 -f Dockerfile.nina .
```

> **注意**：Dockerfile.nina 已配置阿里云镜像源，国内服务器可正常构建。

## 三、启动容器

```bash
docker run -d \
  --name trendradar-nina \
  --restart unless-stopped \
  -p 0.0.0.0:8080:8000 \
  -v /root/trendradar/config:/app/config \
  -v /root/trendradar/output:/app/output \
  -e TZ=Asia/Shanghai \
  -e ADMIN_USER=admin \
  -e ADMIN_PASSWORD=你的密码 \
  trendradar-nina:5.5.0
```

### 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ADMIN_USER` | 管理员账号 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `trendradar` |
| `TZ` | 时区 | `Asia/Shanghai` |
| `AI_API_KEY` | AI 分析 API Key（可选） | - |

### 验证服务

```bash
# 健康检查
curl http://127.0.0.1:8080/health

# 应返回：
# {"status":"ok","version":"5.5.2","service":"TrendRadar Nina"}
```

## 四、配置 Nginx 反向代理（可选）

如果 Nginx 也在 Docker 容器内，需要使用 Docker 网桥 IP：

```nginx
server {
    listen 80;
    server_name news.example.com;

    client_max_body_size 50M;

    location / {
        # 如果 Nginx 在 Docker 容器内，使用 172.17.0.1
        # 如果 Nginx 在宿主机，使用 127.0.0.1
        proxy_pass http://172.17.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

重载 Nginx：

```bash
nginx -t && nginx -s reload
```

## 五、配置 HTTPS（可选）

使用 Certbot 申请 Let's Encrypt 免费证书：

```bash
# 如果 Nginx 在 Docker 容器内，需要先停止释放 80 端口
docker stop nginx-container

# 申请证书
certbot certonly --standalone -d news.example.com --non-interactive --agree-tos --email your@email.com

# 重启 Nginx
docker start nginx-container
```

更新 Nginx 配置启用 HTTPS：

```nginx
server {
    listen 80;
    server_name news.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name news.example.com;

    ssl_certificate /etc/letsencrypt/live/news.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/news.example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://172.17.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

## 六、从旧版本迁移配置

如果之前使用官方版本，配置文件可以直接复用：

1. **config/config.yaml** - 主配置文件（热榜平台、RSS、AI 等配置）
2. **config/frequency_words.txt** - 关键词配置
3. **output/** - 历史数据

Nina 扩展会自动读取这些配置，同时提供 Web 管理界面进行可视化管理。

### 导入配置到数据库（可选）

如果需要在 Web 后台管理配置，可以运行导入脚本将 yaml 配置导入数据库。

## 七、常用运维命令

```bash
# 查看容器状态
docker ps | grep trendradar

# 查看日志
docker logs -f trendradar-nina

# 重启服务
docker restart trendradar-nina

# 停止服务
docker stop trendradar-nina

# 更新镜像后重新部署
docker stop trendradar-nina && docker rm trendradar-nina
docker build -t trendradar-nina:5.5.0 -f Dockerfile.nina .
docker run -d ... (同上启动命令)
```

## 八、访问后台

| 项目 | 地址 |
|------|------|
| Web 管理后台 | `https://your-domain.com` |
| 健康检查 | `https://your-domain.com/health` |
| API 文档 | `https://your-domain.com/docs` |

默认登录凭证：
- 账号：`admin`
- 密码：启动时设置的 `ADMIN_PASSWORD`

## 九、故障排查

### 502 Bad Gateway

1. 检查容器是否运行：`docker ps | grep trendradar`
2. 检查端口绑定：`docker port trendradar-nina`
3. 如果 Nginx 在 Docker 容器内，确保 proxy_pass 使用 `172.17.0.1` 而非 `127.0.0.1`

### 登录失败 401

1. 确认密码正确（区分大小写）
2. 检查环境变量：`docker exec trendradar-nina env | grep ADMIN`

### 构建失败（网络问题）

Dockerfile.nina 已配置阿里云镜像源，如仍有问题：
- apt 源：检查 `/etc/apt/sources.list.d/debian.sources`
- pip 源：检查 `pip config list`

---

**维护者**: 老王 (Claude Code)
**最后更新**: 2026-02-02
