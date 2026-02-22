FROM python:3.12-slim

LABEL maintainer="Sovereign Stack" \
      description="Governance Engine — Layer 2: Governance & Trust"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cache-friendly layer)
COPY src/ghoststack/governance/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Data directory for the SQLite database
RUN mkdir -p /data

# Default environment
ENV GOV_DATABASE_URL=sqlite:////data/governance.db \
    GOV_API_HOST=0.0.0.0 \
    GOV_API_PORT=8000 \
    GOV_QUORUM=0.5 \
    GOV_LOG_LEVEL=INFO \
    PYTHONPATH=/app/src

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "ghoststack.governance.main", "--host", "0.0.0.0", "--port", "8000"]
