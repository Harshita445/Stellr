# Deployment

## Prerequisites

- Docker & Docker Compose v2
- Git
- A domain name pointed at your server (for TLS)
- Cloudflare, Let's Encrypt (certbot), or Caddy for TLS termination

## Local Development with Docker Compose

```bash
# 1. Clone and enter the project
git clone <repo-url> constellation
cd constellation

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET and FINGERPRINT_SALT

# 3. Start all services
docker compose up --build -d

# 4. Run database migrations
docker compose exec api alembic upgrade head

# The app is now available at http://localhost
```

## Production Deployment

### 1. Server Provisioning

A VPS with at least 2 GB RAM and 20 GB disk running Ubuntu 22.04+ is recommended.

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in, or run: newgrp docker
```

### 2. Deploy

```bash
git clone <repo-url> /opt/constellation
cd /opt/constellation

cp .env.example .env
nano .env   # Fill in secrets

docker compose up -d
docker compose exec api alembic upgrade head
```

### 3. TLS (Let's Encrypt via Certbot)

```bash
# Stop nginx briefly so certbot can bind port 80
docker compose stop nginx

sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to a docker-accessible volume
mkdir -p /opt/constellation/certs
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/constellation/certs/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/constellation/certs/
sudo chown -R $USER:$USER /opt/constellation/certs
```

Create `nginx-ssl.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # ... same proxy blocks as nginx.conf ...
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

Update `docker-compose.yml` to mount the SSL config and certs, then restart:

```bash
docker compose up -d
```

### 4. Auto-renew TLS (cron)

```bash
sudo crontab -e
# Add:
# 0 3 * * * certbot renew --quiet && docker compose -f /opt/constellation/docker-compose.yml restart nginx
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) does:

| Trigger | Action |
|---------|--------|
| PR to `main` | Run backend tests (if any), frontend build check |
| Push to `main` | All of the above, plus build & push Docker images to `ghcr.io` |

After CI pushes images, you can pull them on the server:

```bash
docker compose pull
docker compose up -d
docker compose exec api alembic upgrade head
```

Or automate this via a deploy key / watchtower.

## Rolling Updates

Services are configured with `restart: unless-stopped`. To update:

```bash
git pull
docker compose build --no-cache api frontend
docker compose up -d
```

Nginx is reloaded automatically by Docker Compose when its config changes.

## Health Check

```bash
curl http://localhost/api/v1/health
# {"status":"healthy","version":"1.0.0","uptime_seconds":42.0,"database":{"status":"healthy"}}
```

## Architecture Overview

```
Internet
    │
    ▼
  Nginx (:80 / :443)
    │
    ├── /api/* → FastAPI (api:8000)
    │
    └── /*     → Next.js (frontend:3000)
                        │
                        ▼
                   PostgreSQL (db:5432)
```
