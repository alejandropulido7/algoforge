# ==============================================================================
# AlgoForge Dokploy & Docker Deployment Documentation
# ==============================================================================

This setup provides multi-stage Docker builds separating compilation from runtime for production deployment on Dokploy (or standalone Docker / Docker Compose).

## Components Architecture

| Service | Technology | Build Stage | Runtime Stage | Role |
| :--- | :--- | :--- | :--- | :--- |
| **backend** | Python 3.11 / FastAPI | `python:3.11-slim` (gcc, g++, build-essential) | `python:3.11-slim` (libgomp1, non-root user) | REST API & Health checks |
| **celery_worker** | Python 3.11 / Celery | (Shares `backend/Dockerfile`) | (Shares `backend/Dockerfile`) | Async strategy discovery, genetic search & RL trainer |
| **frontend** | Vite + React + TypeScript | `node:20-alpine` (npm ci && npm run build) | `nginx:alpine` (SPA fallback + gzip + security headers) | Web UI |
| **redis** | Redis 7 Alpine | N/A | `redis:7-alpine` | Celery broker & result backend |

---

## Deploying on Dokploy

### Option A: Dokploy Compose Deployment (Recommended)
1. In the Dokploy Dashboard, select **Create Service** -> **Compose**.
2. Select your Git Repository or paste the root [`docker-compose.yml`](file:///Users/alejandropulido/Documents/software-projects/trading/algoforge/docker-compose.yml).
3. Under the **Environment Variables** tab in Dokploy, configure:
   ```env
   # Supabase Credentials
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key

   # Frontend Build Args & CORS
   VITE_API_URL=https://api.yourdomain.com
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```
4. Click **Deploy**. Dokploy will pull, build the compilation stages, cache dependencies, and spin up all 4 services.

---

### Option B: Individual Dokploy Application Services
If you prefer creating separate application services in Dokploy:

1. **Redis**: Create a **Database** -> **Redis** service named `redis`.
2. **Backend API**:
   - Build Type: **Dockerfile**
   - Context: `/backend`
   - Dockerfile path: `Dockerfile`
   - Port: `8000`
   - Environment variables: `REDIS_URL=redis://<redis-host>:6379/0`, `CELERY_BROKER_URL=redis://<redis-host>:6379/0`, plus Supabase variables.
3. **Celery Worker**:
   - Build Type: **Dockerfile**
   - Context: `/backend`
   - Dockerfile path: `Dockerfile`
   - Command override: `celery -A workers.celery_app.celery_app worker --loglevel=info --concurrency=2`
   - Environment variables: Same as backend.
4. **Frontend**:
   - Build Type: **Dockerfile**
   - Context: `/frontend`
   - Dockerfile path: `Dockerfile`
   - Port: `80`
   - Build Arguments: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
