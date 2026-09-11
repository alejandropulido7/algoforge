# ==============================================================================
# AlgoForge Backend & Celery Worker Dockerfile
# Multi-stage build for Python 3.11 with C/C++ compilation tools and minimal runtime
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build / Compilation
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system compilation packages for scientific Python libraries (numpy, ta, vectorbt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate installed dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies (utilizing Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Runtime
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

# Create non-root user for security
RUN groupadd -r algoforge && useradd -r -g algoforge -d /app -s /sbin/nologin algoforge

# Install minimal runtime libraries (curl for healthchecks, OpenMP/BLAS runtime support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

# Copy application source code
COPY --chown=algoforge:algoforge . /app

# Create and set permissions for runtime storage directories
RUN mkdir -p /app/data_storage /app/models /app/logs \
    && chown -R algoforge:algoforge /app/data_storage /app/models /app/logs

USER algoforge

# Default port for FastAPI
EXPOSE 8000

# Health check against the health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command runs the FastAPI server. Celery worker service overrides CMD with:
# celery -A workers.celery_app.celery_app worker --loglevel=info --concurrency=2
CMD ["uvicorn", "algoforge.main:app", "--host", "0.0.0.0", "--port", "8000"]
