# Astrologico Operations Runbook v2.0

**Purpose**: Quick reference guide for common operational tasks  
**Audience**: DevOps, SRE, Operations teams  
**Last Updated**: 2025-03-30

---

## Quick Reference

### Common Commands

#### Start/Stop Services
```bash
# Docker
docker run -d --name astrologico -p 8000:8000 astrologico:latest
docker stop astrologico
docker restart astrologico
docker logs astrologico -f  # Follow logs

# Docker Compose
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml stop
docker-compose logs -f astrologico

# Native Python
astrologico-api --host 0.0.0.0 --port 8000 --workers 4
```

#### Health & Status
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Detailed status
curl http://localhost:8000/api/v1/status | jq .

# Metrics
curl http://localhost:8000/api/v1/metrics | jq .

# Container status
docker ps | grep astrologico
docker inspect astrologico --format='{{.State.Health.Status}}'
```

#### Logs
```bash
# Recent logs (last 100 lines)
docker logs --tail 100 astrologico

# Follow logs in real-time
docker logs -f astrologico

# Logs since specific time
docker logs --since 5m astrologico

# Export logs
docker logs astrologico > astrologico.log 2>&1
```

---

## Incident Response Guide

### Issue: API Not Responding

**Symptoms**: `curl` times out, health check failing

**Step 1: Check if container is running**
```bash
docker ps | grep astrologico
# If not running:
docker ps -a | grep astrologico
```

**Step 2: Check logs for errors**
```bash
docker logs --tail 50 astrologico | grep ERROR
```

**Step 3: Restart service**
```bash
docker restart astrologico
sleep 5
docker logs astrologico | tail -20  # Check for errors
```

**Step 4: Verify port**
```bash
netstat -tlnp | grep 8000
# Or:
lsof -i :8000
```

**Step 5: Manual restart if needed**
```bash
docker rm -f astrologico
docker run -d --name astrologico \
  -e ASTROLOGICO_ENV=production \
  -e ASTROLOGICO_API_KEY="your-key" \
  -p 8000:8000 \
  astrologico:latest

# Wait 30 seconds for healthcheck
sleep 30
curl http://localhost:8000/api/v1/health
```

---

### Issue: High Memory Usage

**Symptoms**: Memory usage > 1GB, container killed by OOMKiller

**Step 1: Check memory**
```bash
docker stats astrologico --no-stream
```

**Step 2: Check for memory leaks**
```bash
docker logs astrologico | grep -i memory
```

**Step 3: Restart container**
```bash
docker restart astrologico
```

**Step 4: Increase memory limit (if running with limits)**
```bash
docker update --memory 2gb astrologico
docker restart astrologico
```

**Step 5: Review API usage**
```bash
curl http://localhost:8000/api/v1/metrics | jq .memory
```

---

### Issue: High CPU Usage

**Symptoms**: CPU > 80%, slow API responses

**Step 1: Check CPU usage**
```bash
docker stats astrologico --no-stream
```

**Step 2: Check request metrics**
```bash
curl http://localhost:8000/api/v1/metrics | jq '.requests_total'
```

**Step 3: Increase worker count (if using multiple workers)**
```bash
# Stop current
docker stop astrologico

# Start with more workers
docker run -d --name astrologico \
  -e ASTROLOGICO_ENV=production \
  -p 8000:8000 \
  astrologico:latest
  # Note: Add --workers flag in astrologico-api command
```

**Step 4: Add load balancing**
See DEPLOYMENT.md for Nginx/HAProxy configuration

---

### Issue: Auth Failures

**Symptoms**: 401 errors on /api/v1/ask endpoint, "API key invalid"

**Step 1: Verify API key is set**
```bash
docker inspect astrologico --format='{{index .Config.Env}}'
# Look for ASTROLOGICO_API_KEY
```

**Step 2: Test with valid key**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "X-API-Key: your-actual-key" \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'
```

**Step 3: Check if auth is enabled**
```bash
docker inspect astrologico --format='{{index .Config.Env}}' | grep REQUIRE_API_KEY
```

**Step 4: Update key if needed**
```bash
docker stop astrologico
docker rm astrologico
docker run -d --name astrologico \
  -e ASTROLOGICO_API_KEY="new-key-value" \
  -e ASTROLOGICO_ENV=production \
  -p 8000:8000 \
  astrologico:latest
```

---

### Issue: Rate Limiting (Too Many Requests)

**Symptoms**: 429 errors, "Rate limit exceeded"

**Step 1: Check current rate limits**
```bash
curl http://localhost:8000/api/v1/metrics | jq '.rate_limit'
```

**Step 2: Is it legitimate traffic?**
```bash
# Review metrics for request sources
curl http://localhost:8000/api/v1/metrics | jq '.
requests_per_endpoint'
```

**Step 3: Increase rate limit if needed**
```bash
docker stop astrologico
docker run -d --name astrologico \
  -e ASTROLOGICO_ENV=production \
  -e ASTROLOGICO_RATE_LIMIT_REQUESTS=200 \
  -e ASTROLOGICO_RATE_LIMIT_PERIOD=60 \
  -p 8000:8000 \
  astrologico:latest
```

**Step 4: Add load balancing for multiple instances**
See DEPLOYMENT.md

---

### Issue: CORS Errors

**Symptoms**: Browser errors "Cross-Origin Request Blocked"

**Step 1: Check allowed origins**
```bash
docker inspect astrologico --format='{{index .Config.Env}}' | grep ALLOWED_ORIGINS
```

**Step 2: Add origin if needed**
```bash
docker stop astrologico
docker rm astrologico

# Add your domain to allowed origins
docker run -d --name astrologico \
  -e ASTROLOGICO_ALLOWED_ORIGINS="https://yoursite.com,https://app.yoursite.com" \
  -e ASTROLOGICO_ENV=production \
  -p 8000:8000 \
  astrologico:latest
```

**Step 3: Verify CORS headers**
```bash
curl -H "Origin: https://yoursite.com" \
  http://localhost:8000/api/v1/health -v | grep -i access-control
```

---

## Performance Tuning

### Worker Configuration
```bash
# Default: 1 worker
astrologico-api

# Multiple workers for better throughput
astrologico-api --workers 4

# Auto-detect CPU count
astrologico-api --workers 0  # Uses CPU count
```

### Load Balancing Setup
```bash
# See DEPLOYMENT.md for full nginx/haproxy configs

# Basic round-robin (3 instances)
docker run -d --name astrologico-1 -p 8001:8000 astrologico:latest
docker run -d --name astrologico-2 -p 8002:8000 astrologico:latest
docker run -d --name astrologico-3 -p 8003:8000 astrologico:latest

# Nginx reverse proxy in front (see DEPLOYMENT.md)
```

---

## Maintenance Tasks

### Daily (Automated)
- [ ] Health checks every 30 seconds
- [ ] Metrics collection every 5 minutes
- [ ] Log rotation (if log drivers configured)
- [ ] Automated backups (if database used)

### Weekly
- [ ] Review error logs: `docker logs astrologico | grep ERROR`
- [ ] Check resource usage: `docker stats`
- [ ] Verify backup status
- [ ] Review metrics dashboard

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Security scan: `bandit src/astrologico/`
- [ ] Performance review
- [ ] Capacity planning

### Quarterly
- [ ] Rotate API keys/secrets
- [ ] Update base Docker image (`python:3.13-slim`)
- [ ] Load test and capacity planning
- [ ] Security audit

---

## Monitoring Setup

### Prometheus Metrics (example)
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'astrologico'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
```

### Key Metrics to Monitor
```bash
# Get all metrics
curl http://localhost:8000/api/v1/metrics | jq .

# Example dashboard queries:
# - Request rate (req/sec)
# - Error rate (%)
# - Response time (ms)
# - Memory usage (MB)
# - CPU usage (%)
```

### Alerting Rules
```
- Alert if health check fails > 2 times
- Alert if error rate > 1%
- Alert if response time > 5 seconds
- Alert if memory > 1.5GB
- Alert if CPU > 85%
```

---

## Backup & Recovery

### Data to Backup
```bash
# Configuration and secrets
/etc/astrologico/  # or your config location

# Ephemeris data (already in container, no backup needed)
# Logs (if stored locally)
/var/log/astrologico/
```

### Docker Image Management
```bash
# Save image to tar
docker save astrologico:latest > astrologico-v2.0.0.tar

# Load image from tar
docker load < astrologico-v2.0.0.tar

# Push to registry
docker tag astrologico:latest myregistry/astrologico:latest
docker push myregistry/astrologico:latest

# Pull from registry
docker pull myregistry/astrologico:latest
```

---

## Security Checklist

### Before Production
- [ ] API keys generated and stored in vault
- [ ] CORS origins configured for your domain
- [ ] TLS/SSL configured (reverse proxy)
- [ ] Firewall rules configured
- [ ] Log aggregation configured
- [ ] Monitoring/alerting enabled
- [ ] Incident response plan documented

### During Runtime
- [ ] No secrets in logs
- [ ] API keys rotated quarterly
- [ ] Dependencies kept updated
- [ ] Security patches applied immediately
- [ ] Access logs reviewed regularly
- [ ] Rate limiting active

### Emergency Procedures
```bash
# Disable public access (firewall block)
sudo ufw deny 8000/tcp

# Kill containers
docker rm -f astrologico astrologico-1 astrologico-2 astrologico-3

# Restart with no auth (emergency recovery only)
docker run -d --name astrologico \
  -e ASTROLOGICO_REQUIRE_API_KEY_FOR_AI=false \
  -p 8000:8000 \
  astrologico:latest

# Restore from backup
docker load < astrologico-backup.tar
```

---

## Contacts & Escalation

**For Issues**, escalate based on severity:

- **P0 (Down)**: ops-on-call@company.com → page on-call
- **P1 (Degraded)**: ops-lead@company.com → within 1 hour
- **P2 (Feature)**: platform-team@company.com → within 4 hours
- **P3 (UX)**: product-team@company.com → within 1 day

**Repository**: https://github.com/ME0094/astrologico  
**CI/CD**: https://github.com/ME0094/astrologico/actions

---

## Additional Resources

- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- [SECURITY_FIXES.md](SECURITY_FIXES.md) - Security implementation details
- [PHASE_7_COMPLETE.md](PHASE_7_COMPLETE.md) - Phase completion summary
- [README.md](README.md) - Project overview

---

**Last Updated**: 2025-03-30  
**Version**: 1.0  
**Status**: Ready for Production Use
