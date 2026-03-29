# Astrologico Deployment Guide

**Version**: 2.0.0  
**Last Updated**: March 30, 2026  
**Status**: Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Health Checks & Monitoring](#health-checks--monitoring)
6. [Scaling](#scaling)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)

---

## Quick Start

### Local Development with Docker Compose

```bash
# Clone repository
git clone https://github.com/ME0094/astrologico.git
cd astrologico

# Create .env file (see Environment Configuration)
cp .env.example .env

# Start services
docker-compose up -d

# Check service health
curl http://localhost:8000/api/status/health
```

### With Docker Directly

```bash
# Build image
docker build -t astrologico:2.0.0 .

# Run container
docker run -d \
  --name astrologico \
  -p 8000:8000 \
  -e ASTROLOGICO_ENV=production \
  -e AI_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  astrologico:2.0.0
```

---

## Docker Deployment

### Build the Image

**Using Docker Compose** (recommended):
```bash
docker-compose build
```

**Using Docker CLI**:
```bash
docker build -t astrologico:2.0.0 -f Dockerfile .
```

### Run the Container

**Production Configuration**:
```bash
docker run -d \
  --name astrologico-prod \
  --restart unless-stopped \
  -p 8000:8000 \
  --memory=1g \
  --cpus=2 \
  -e ASTROLOGICO_ENV=production \
  -e DEBUG=false \
  -e LOG_LEVEL=info \
  -e AI_PROVIDER=openai \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -v astrologico-data:/app/data \
  -v astrologico-logs:/app/logs \
  --health-cmd='curl -f http://localhost:8000/api/status/health' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --health-start-period=40s \
  astrologico:2.0.0
```

### Docker Compose Stack

**Development**:
```bash
docker-compose up -d
```

**Production**:
```bash
docker-compose -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d
```

**Scale services**:
```bash
docker-compose up -d --scale astrologico-api=3
```

### Multi-Container Setup

For production environments, consider using:
- **Nginx** reverse proxy
- **Redis** for caching
- **PostgreSQL** for persistent data (if needed)

Example with Nginx:
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - astrologico-api

  astrologico-api:
    build: .
    environment:
      - ASTROLOGICO_ENV=production
    expose:
      - "8000"
```

---

## Kubernetes Deployment

### Prerequisites

- `kubectl` configured
- Kubernetes cluster (1.24+)
- Helm 3.0+ (optional)

### Using Helm

```bash
# Add Helm repository
helm repo add astrologico https://charts.astrologico.dev
helm repo update

# Install release
helm install astrologico-prod astrologico/astrologico \
  --namespace astrologico \
  --create-namespace \
  --values values.yaml
```

### Manual Kubernetes Deployment

**Create Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: astrologico-api
  namespace: astrologico
spec:
  replicas: 3
  selector:
    matchLabels:
      app: astrologico-api
  template:
    metadata:
      labels:
        app: astrologico-api
    spec:
      containers:
      - name: api
        image: ghcr.io/me0094/astrologico:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ASTROLOGICO_ENV
          value: "production"
        - name: AI_PROVIDER
          valueFrom:
            configMapKeyRef:
              name: astrologico-config
              key: ai-provider
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: astrologico-secrets
              key: openai-api-key
        resources:
          requests:
            cpu: 500m
            memory: 256Mi
          limits:
            cpu: 2000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /api/status/health
            port: 8000
          initialDelaySeconds: 40
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /api/status/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Create Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: astrologico-api
  namespace: astrologico
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    name: http
  selector:
    app: astrologico-api
```

**Create Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: astrologico-ingress
  namespace: astrologico
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.astrologico.dev
    secretName: astrologico-tls
  rules:
  - host: api.astrologico.dev
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: astrologico-api
            port:
              number: 80
```

**Apply manifests**:
```bash
kubectl apply -f k8s/
```

---

## Environment Configuration

### Configuration Files

**Default (.env.example)**:
```bash
# Environment
ASTROLOGICO_ENV=production
DEBUG=false
LOG_LEVEL=info

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ASTROLOGICO_ENV` | string | `production` | Environment: development, testing, production |
| `DEBUG` | boolean | `false` | Enable debug mode |
| `LOG_LEVEL` | string | `info` | Logging level: debug, info, warning, error |
| `API_HOST` | string | `0.0.0.0` | API bind address |
| `API_PORT` | integer | `8000` | API port |
| `ALLOWED_ORIGINS` | string | `*` | CORS allowed origins (comma-separated) |
| `AI_PROVIDER` | string | `openai` | AI provider: openai, anthropic |
| `OPENAI_API_KEY` | string | `` | OpenAI API key |
| `ANTHROPIC_API_KEY` | string | `` | Anthropic API key |
| `ENABLE_RATE_LIMITING` | boolean | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | integer | `100` | Requests per period |
| `RATE_LIMIT_PERIOD` | integer | `60` | Rate limit period (seconds) |

### Configuration via ConfigMap (K8s)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: astrologico-config
  namespace: astrologico
data:
  ai-provider: "openai"
  log-level: "info"
  debug: "false"
```

### Secrets Management

**Docker Secrets**:
```bash
echo 'sk-...' | docker secret create openai_api_key -
```

**Kubernetes Secrets**:
```bash
kubectl create secret generic astrologico-secrets \
  --from-literal=openai-api-key=sk-... \
  --namespace=astrologico
```

---

## Health Checks & Monitoring

### Health Endpoints

- **Liveness**: `GET /api/status/health`
- **Metrics**: `GET /api/status/metrics`
- **Info**: `GET /api/status/info`

### Docker Health Check

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' astrologico

# Manual health check
curl -f http://localhost:8000/api/status/health
```

### Kubernetes Probes

**Liveness Probe**: Restarts unhealthy pods
**Readiness Probe**: Removes pods from load balancer
**Startup Probe**: Waits for application startup

### Monitoring Stack (Prometheus + Grafana)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'astrologico'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/status/metrics'
```

### Logging

**Container logs**:
```bash
docker logs astrologico

# Follow logs
docker logs -f astrologico
```

**Kubernetes logs**:
```bash
kubectl logs -n astrologico deployment/astrologico-api

# Stream logs
kubectl logs -f -n astrologico deployment/astrologico-api
```

---

## Scaling

### Horizontal Scaling (Docker Compose)

```bash
# Scale to 3 instances
docker-compose up -d --scale astrologico-api=3
```

### Load Balancing

**Nginx configuration** (`nginx.conf`):
```nginx
upstream astrologico {
    server astrologico-1:8000;
    server astrologico-2:8000;
    server astrologico-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://astrologico;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Kubernetes Scaling

```bash
# Scale deployment
kubectl scale deployment astrologico-api \
  --replicas=5 \
  -n astrologico

# Auto-scaling with HPA
kubectl autoscale deployment astrologico-api \
  --min=2 \
  --max=10 \
  --cpu-percent=80 \
  -n astrologico
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs astrologico

# Verify image
docker image inspect astrologico:latest

# Rebuild image
docker build --no-cache -t astrologico:latest .
```

### Health Check Failures

```bash
# Manual health check
curl -v http://localhost:8000/api/status/health

# Inside container
docker exec astrologico curl http://localhost:8000/api/status/health

# Check startup time
docker inspect astrologico | grep -A 5 "State"
```

### High Memory Usage

```bash
# Check container stats
docker stats astrologico

# Limit memory in docker-compose
services:
  astrologico-api:
    deploy:
      resources:
        limits:
          memory: 1G
```

### API Unresponsive

```bash
# Restart container
docker restart astrologico

# Restart service (docker-compose)
docker-compose restart astrologico-api

# Check port binding
docker port astrologico

# Verify network
docker network inspect astrologico-network
```

### Certificate Issues (TLS/SSL)

```bash
# Using Let's Encrypt with Certbot
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certify -d api.astrologico.dev

# Mount certificates
docker run -d \
  -v /etc/letsencrypt:/app/certs:ro \
  -e TLS_CERT=/app/certs/live/api.astrologico.dev/fullchain.pem \
  -e TLS_KEY=/app/certs/live/api.astrologico.dev/privkey.pem \
  astrologico:latest
```

---

## Security Considerations

### Image Security

✅ **Best Practices**:
- Use multi-stage builds to reduce image size
- Run as non-root user (astrologico:1000)
- Minimize base image (python:3.13-slim)
- Remove build tools from runtime image

```bash
# Scan image for vulnerabilities
docker scout cves astrologico:latest

# Sign images
docker trust sign astrologico:latest
```

### Network Security

```yaml
# Network policy (K8s)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: astrologico-netpol
spec:
  podSelector:
    matchLabels:
      app: astrologico-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8000
```

### Secret Management

**Never commit secrets**:
```bash
# Use .gitignore
echo ".env" >> .gitignore

# Use external secret stores
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Cloud Secret Manager
```

### SSL/TLS Configuration

```bash
# Generate self-signed certificate (testing)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Use Let's Encrypt (production)
# See docker-compose.prod.yml for full setup
```

### Container Registry Security

```bash
# Authenticate to registry
docker login ghcr.io

# Use PAT (Personal Access Token)
cat ~/pat.txt | docker login ghcr.io -u USERNAME --password-stdin

# Push signed image
docker push ghcr.io/me0094/astrologico:latest
```

---

## Backup & Recovery

### Volume Backups

```bash
# Backup data volume
docker run --rm -v astrologico-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/astrologico-data.tar.gz -C /data .

# Restore from backup
docker run --rm -v astrologico-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/astrologico-data.tar.gz -C /data
```

### Database Backups (if used)

```bash
# PostgreSQL backup
docker exec astrologico-db pg_dump -U user dbname > backup.sql

# MySQL backup
docker exec astrologico-db mysqldump -u user -p database > backup.sql
```

---

## Performance Tuning

### Resource Limits

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Connection Pooling

Configure in API settings to optimize database connections.

### Caching

Use Redis for caching expensive calculations:
```bash
docker-compose exec astrologico-api redis-cli PING
```

---

## Related Documentation

- [README.md](./README.md) - Project overview
- [INSTALLATION_SUMMARY.md](./INSTALLATION_SUMMARY.md) - Installation guide
- [PHASE_6_COMPLETE.md](./PHASE_6_COMPLETE.md) - Test suite documentation
- [SECURITY.md](./SECURITY.md) - Security guidelines
- [OPTIMIZATION.md](./OPTIMIZATION.md) - Performance optimization

---

## Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/ME0094/astrologico/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ME0094/astrologico/discussions)
- **Security**: [SECURITY.md](./SECURITY.md)

---

**Status**: ✅ **Production Ready**
