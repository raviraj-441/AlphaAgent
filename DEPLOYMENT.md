# AlphaAgent Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying AlphaAgent in development, testing, and production environments. The deployment is designed with security, scalability, and reliability in mind.

## Prerequisites

### Required Software

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.10+ (for local development)
- **Git** 2.0+

### Required API Keys

Create a `.env` file in the project root with:

```bash
# Groq LLM API (https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# Tavily Search API (https://tavily.com)
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: For Grafana
GF_SECURITY_ADMIN_PASSWORD=your_secure_password
```

## Development Setup

### 1. Local Development

```bash
# Clone repository
git clone <repository-url>
cd AlphaAgent

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -e .

# Load environment
python -c "from backend.utils.env import EnvManager; EnvManager.load_env()"

# Run tests
pytest simple_test.py comprehensive_test.py integration_test.py -v

# Start development server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Docker Development (Recommended)

```bash
# Build Docker image
docker build -t alphaagent:dev .

# Run single container for development
docker run -it \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  alphaagent:dev

# Or use docker-compose (development profile)
docker-compose up -d web
docker-compose logs -f web
```

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest simple_test.py comprehensive_test.py -v

# Run with coverage
pytest simple_test.py comprehensive_test.py --cov=backend --cov-report=html

# Run specific test
pytest simple_test.py::test_parse_portfolio -v
```

### Integration Tests

```bash
# Run integration tests
pytest integration_test.py -v

# Test environment variable handling
pytest integration_test.py::TestEnvManager -v

# Test path resolution
pytest integration_test.py::TestPathManager -v

# Test recommendation engine
pytest integration_test.py::TestRecommendationEngine -v
```

### Docker Tests

```bash
# Build and test Docker image
docker build -t alphaagent:test .
docker run --rm alphaagent:test pytest simple_test.py comprehensive_test.py -v

# Run tests with coverage in container
docker run --rm alphaagent:test pytest simple_test.py comprehensive_test.py --cov=backend
```

## Production Deployment

### 1. Docker Compose Stack

The complete stack includes:
- **Web**: FastAPI backend (port 8000)
- **ChromaDB**: Vector store (port 8001)
- **Redis**: Cache layer (port 6379)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Monitoring dashboard (port 3000)

```bash
# Start full production stack
docker-compose up -d

# View logs
docker-compose logs -f web

# Check service health
docker-compose ps

# Verify services are running
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/heartbeat
```

### 2. Health Checks

```bash
# API health check
curl -X GET http://localhost:8000/health

# Metrics endpoint (Prometheus format)
curl -X GET http://localhost:8000/metrics

# ChromaDB health
curl -X GET http://localhost:8001/api/v1/heartbeat
```

### 3. Monitoring

#### Access Grafana Dashboard

1. Open browser: `http://localhost:3000`
2. Login: 
   - Username: `admin`
   - Password: (from `.env` file `GF_SECURITY_ADMIN_PASSWORD`)
3. Navigate to **Dashboards** > **AlphaAgent API Monitoring**

#### Prometheus Queries

Access Prometheus directly: `http://localhost:9090`

Key metrics:
```
# Request rate (requests per minute)
rate(http_requests_total{job="alphaagent-api"}[5m]) * 60

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="alphaagent-api"}[5m]))

# Error rate
rate(http_requests_total{job="alphaagent-api", status=~"5.."}[5m]) * 60

# Active requests
http_requests_in_progress{job="alphaagent-api"}
```

### 4. Scaling

#### Horizontal Scaling with Load Balancer

```yaml
# Add to docker-compose.yml
load_balancer:
  image: traefik:latest
  ports:
    - "80:80"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
```

#### Kubernetes Deployment

```bash
# Create Kubernetes resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Scale replicas
kubectl scale deployment/alphaagent-api --replicas=3 -n alphaagent

# View deployment
kubectl get pods -n alphaagent
kubectl logs -n alphaagent -l app=alphaagent-api
```

## Environment Variables

### Application Settings

```bash
# API Configuration
PORT=8000
HOST=0.0.0.0
WORKERS=4

# Python Configuration
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# LLM Configuration
GROQ_API_KEY=<your_key>
GROQ_MODEL=llama-3.1-8b-instant

# Search Configuration
TAVILY_API_KEY=<your_key>

# Vector Store
CHROMA_HOST=chroma
CHROMA_PORT=8000

# Cache
REDIS_HOST=redis
REDIS_PORT=6379

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=8000
```

### Security Best Practices

1. **Never commit `.env` to version control**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong passwords for services**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Rotate API keys regularly**
   - Set expiration dates in Groq and Tavily consoles
   - Monitor usage for unusual activity

4. **Run containers as non-root**
   - Dockerfile uses `appuser` (UID 1000)
   - Do not modify to use root (uid 0)

5. **Use secrets management for production**
   ```bash
   # With Docker Swarm
   docker secret create groq_key -
   
   # With Kubernetes
   kubectl create secret generic api-keys --from-literal=groq_key=$GROQ_API_KEY
   ```

## Troubleshooting

### Docker Build Issues

```bash
# Clean Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache

# Check build logs
docker build -t alphaagent:debug --progress=plain .
```

### Service Connectivity Issues

```bash
# Check network connectivity
docker-compose exec web ping chroma

# Inspect network
docker network inspect alphaagent_alphaagent-network

# View service logs
docker-compose logs chroma
docker-compose logs redis
```

### Memory/Resource Issues

```bash
# Monitor resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory: 4GB or higher

# Configure limits in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Path Resolution Issues

```bash
# Test path manager from any directory
python -c "
from backend.utils.paths import PathManager
print('Root:', PathManager.get_project_root())
print('Data:', PathManager.get_data_dir())
"

# Verify paths are absolute
cd /tmp
python -c "
from backend.utils.paths import PathManager
root = PathManager.get_project_root()
assert root.is_absolute(), 'Path is not absolute!'
"
```

### Environment Variable Issues

```bash
# Test environment loading
python -c "
from backend.utils.env import EnvManager
EnvManager.load_env()
print('GROQ_API_KEY:', EnvManager.get('GROQ_API_KEY'))
"

# Test subprocess env passing
python -c "
from backend.utils.env import EnvManager
import os
os.environ['TEST_VAR'] = 'test_value'
result = EnvManager.run_subprocess(['python', '-c', 'import os; print(os.getenv(\"TEST_VAR\"))'])
print('Result:', result)
"
```

## Performance Tuning

### API Server

```bash
# Increase worker processes
docker-compose.yml:
  environment:
    - WORKERS=8  # Match number of CPU cores

# Uvicorn settings
backend/main.py:
  uvicorn.run(app, workers=8, loop="uvloop")
```

### Database/Cache

```bash
# Redis optimization
docker-compose.yml:
  redis:
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

# ChromaDB optimization
  chroma:
    environment:
      - CACHE_SIZE=1000
      - BATCH_SIZE=100
```

### Monitoring

```bash
# Adjust scrape intervals for fewer data points
monitoring/prometheus.yml:
  scrape_interval: 30s  # Reduce from 15s for production
  evaluation_interval: 30s
```

## Backup and Recovery

### Data Backup

```bash
# Backup ChromaDB data
docker-compose exec chroma tar czf /tmp/chroma-backup.tar.gz /chroma/chroma

# Backup Redis data
docker-compose exec redis redis-cli BGSAVE
docker cp alphaagent-redis:/data/dump.rdb ./backups/

# Backup application data
tar czf backups/app-data-$(date +%Y%m%d).tar.gz data/
```

### Restore from Backup

```bash
# Restore ChromaDB
docker-compose exec chroma tar xzf /tmp/chroma-backup.tar.gz -C /

# Restore Redis
docker cp ./backups/dump.rdb alphaagent-redis:/data/
docker-compose restart redis

# Restore application data
tar xzf backups/app-data-YYYYMMDD.tar.gz
```

## CI/CD Pipeline

### GitHub Actions

The project includes a comprehensive CI/CD pipeline in `.github/workflows/ci.yml`:

1. **Tests**: Unit + integration tests on Python 3.10, 3.11, 3.12
2. **Code Quality**: Linting (flake8), formatting (black), type checking (mypy)
3. **Security**: Bandit security scanning, dependency vulnerability check
4. **Docker**: Build Docker image and verify
5. **Coverage**: Generate coverage reports and upload to Codecov

```bash
# View CI logs
# GitHub > Actions tab > Select workflow run

# Run locally
act -j test
```

## Maintenance

### Regular Tasks

```bash
# Weekly: Run security updates
docker-compose pull
docker-compose up -d

# Monthly: Clear Docker unused resources
docker system prune

# Quarterly: Update dependencies
pip list --outdated
pip install --upgrade <package_name>

# Annually: Review and rotate API keys
```

### Monitoring Alerts

Set up alerts in Grafana for:
- API downtime (critical)
- Error rate > 5% (warning)
- P95 latency > 1s (warning)
- Memory usage > 80% (warning)
- ChromaDB connectivity (critical)

## Support and Documentation

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **GitHub Issues**: Report bugs and feature requests
- **Contributing**: See CONTRIBUTING.md

## License

See LICENSE file for details.
