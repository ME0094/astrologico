# Multi-stage build for Astrologico
# Stage 1: Builder
FROM python:3.13-slim as builder

LABEL maintainer="Astrologico Team <info@astrologico.dev>"
LABEL description="Professional astrological calculation suite with REST API"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and build requirements
COPY pyproject.toml README.md ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# Stage 2: Runtime
FROM python:3.13-slim

# Set metadata
LABEL maintainer="Astrologico Team <info@astrologico.dev>"
LABEL version="2.0.0"
LABEL description="Professional astrological calculation suite with REST API"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/app \
    ASTROLOGICO_ENV=production

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=nobody:nobody src/ ./src/
COPY --chown=nobody:nobody setup.py pyproject.toml README.md ./
COPY --chown=nobody:nobody de421.bsp ./

# Create non-root user for security
RUN useradd -m -u 1000 -s /sbin/nologin astrologico && \
    chown -R astrologico:astrologico /app

# Switch to non-root user
USER astrologico

# Expose port (default FastAPI port)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/status/health || exit 1

# Run the API server
CMD ["uvicorn", "src.astrologico.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
