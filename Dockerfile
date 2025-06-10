FROM --platform=linux/amd64 node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM --platform=linux/amd64 python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --timeout=1000 --retries=5 --no-cache-dir -r requirements.txt

RUN solc-select install 0.8.0 && \
    solc-select use 0.8.0 && \
    solc --version && \
    echo "Solidity 0.8.0 installed and activated"

COPY . .
COPY --from=frontend-builder /frontend/dist ./frontend/dist

RUN mkdir -p /app/reports /app/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV OPENAI_API_KEY=""
ENV WEAVIATE_URL="http://localhost:8080"
ENV SOLC_VERSION=0.8.0

HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.simple_api:app", "--host", "0.0.0.0", "--port", "8000"]