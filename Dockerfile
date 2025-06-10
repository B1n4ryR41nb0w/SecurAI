FROM --platform=linux/amd64 node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

FROM --platform=linux/amd64 python:3.11-slim
WORKDIR /app

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y build-essential
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip cache purge

RUN solc-select install 0.8.0 && solc-select use 0.8.0

COPY . .
COPY --from=frontend-builder /frontend/dist ./frontend/dist

RUN mkdir -p /app/reports /app/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV SOLC_VERSION=0.8.0

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.simple_api:app", "--host", "0.0.0.0", "--port", "8000"]", "8000"]