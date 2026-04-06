# Docker Deployment Guide

This guide lets you publish your app once and let friends run it with `docker compose up -d`.

## 1) Build images locally

```bash
# from dyslexia-detection/
docker compose -f docker-compose.build.yml build
```

## 2) Tag images for your registry

```bash
docker tag dyslexai-backend:local yourdockerhubusername/dyslexai-backend:latest
docker tag dyslexai-frontend:local yourdockerhubusername/dyslexai-frontend:latest
```

## 3) Push images

```bash
docker login
docker push yourdockerhubusername/dyslexai-backend:latest
docker push yourdockerhubusername/dyslexai-frontend:latest
```

## 4) Share run steps with friends

Ask them to run:

```bash
# download project and enter folder
cp .env.example .env
# edit .env and set BACKEND_IMAGE and FRONTEND_IMAGE to your tags

docker compose pull
docker compose up -d
```

Open:
- http://localhost:3000

## 5) Optional multi-architecture publish (Intel + Apple Silicon)

```bash
# one-time setup
docker buildx create --use --name dyslexai-builder

# backend
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourdockerhubusername/dyslexai-backend:latest \
  --push backend

# frontend
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourdockerhubusername/dyslexai-frontend:latest \
  --push frontend
```

## Notes

- Backend includes ffmpeg for speech file conversion.
- Uploaded files and SQLite DB are stored in Docker volume `backend_data`.
- To stop services:

```bash
docker compose down
```
