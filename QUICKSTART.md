# AlphaAgent Quick Start Guide

Get AlphaAgent running in minutes.

## Prerequisites

- Docker & Docker Compose (easiest)
- OR Python 3.10+ for local development
- API keys: GROQ_API_KEY and TAVILY_API_KEY

## Quick Start (5 minutes)

### 1. Clone & Configure

```bash
git clone <repository-url>
cd AlphaAgent

# Create .env file with your API keys
cat > .env << EOF
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
GF_SECURITY_ADMIN_PASSWORD=secure_password_here
EOF
```

### 2. Start with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (30 seconds)
sleep 30

# Verify services are running
docker-compose ps

# Check API health
curl http://localhost:8000/health
```

### 3. Access the System

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| API Docs | http://localhost:8000/docs | - |
| Alternative Docs | http://localhost:8000/redoc | - |
| Metrics | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / (from .env) |

### 4. Test with cURL

```bash
# Parse portfolio
curl -X POST http://localhost:8000/api/v1/parse_portfolio \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/test_portfolios/sample_portfolio.csv"}'

# Get recommendations
curl -X GET "http://localhost:8000/api/v1/recommend_replace?portfolio_json=%7B%22AAPL%22%3A100%7D"

# Check health
curl http://localhost:8000/health
```

## Quick Start (Local Python)

### 1. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Run Application

```bash
# Start server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run Tests

```bash
# All tests
pytest simple_test.py comprehensive_test.py -v

# With coverage
pytest simple_test.py comprehensive_test.py --cov=backend

# Integration tests
pytest integration_test.py -v
```

## Monitoring Your System

### 1. Access Grafana Dashboard

```bash
# Open browser
http://localhost:3000

# Login
username: admin
password: (from .env GF_SECURITY_ADMIN_PASSWORD)

# Navigate to
Dashboards → AlphaAgent API Monitoring
```

### 2. View Key Metrics

- **Request Rate**: Requests per minute
- **Latency**: P50, P95, P99 percentiles
- **Error Rate**: 5xx errors as percentage
- **Active Requests**: Currently processing requests

### 3. Check Prometheus

```bash
# View targets
http://localhost:9090/graph

# Example queries
# Request rate
rate(http_requests_total{job="alphaagent-api"}[5m]) * 60

# Error rate
rate(http_requests_total{job="alphaagent-api", status=~"5.."}[5m]) * 60

# Latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Common Tasks

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f chroma
docker-compose logs -f prometheus
```

### Restart a Service

```bash
docker-compose restart web
```

### Scale Services

```bash
# Note: Current setup runs single instance
# For multi-instance, see DEPLOYMENT.md
```

### Clear Data

```bash
# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Then restart
docker-compose up -d
```

## API Endpoints

### Portfolio Management
- `POST /api/v1/parse_portfolio` - Parse portfolio from file
- `GET /api/v1/portfolio_holdings` - Get portfolio holdings

### Tax-Loss Harvesting
- `POST /api/v1/identify_loss` - Identify tax-loss opportunities
- `GET /api/v1/recommend_replace` - Get replacement recommendations

### Compliance
- `POST /api/v1/check_compliance` - Check wash-sale compliance

### Calculations
- `POST /api/v1/calculate_savings` - Calculate tax savings

### Explanations
- `POST /api/v1/explain` - Get AI explanations

See `/docs` for interactive API documentation.

## Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
netstat -an | grep 8000  # Windows: netstat -ano
lsof -i :8000            # macOS/Linux

# Free up port
# Windows
taskkill /PID <PID> /F

# Or use different port
docker-compose -f docker-compose.yml -p alphav2 up -d
```

### Connection Refused

```bash
# Wait for services to be ready
sleep 30

# Check service status
docker-compose ps

# Verify network
docker network ls
docker network inspect alphaagent_alphaagent-network
```

### High Memory Usage

```bash
# Check Docker stats
docker stats

# Restart services
docker-compose down
docker system prune
docker-compose up -d
```

### API Not Responding

```bash
# Check API logs
docker-compose logs web

# Check health endpoint
curl http://localhost:8000/health

# Restart API
docker-compose restart web
```

### Metrics Not Showing in Grafana

```bash
# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets

# Check Prometheus data
curl 'http://localhost:9090/api/v1/query?query=up'

# Restart Prometheus
docker-compose restart prometheus

# Restart Grafana
docker-compose restart grafana
```

## Performance Tips

1. **Allocate Adequate Resources**
   - Docker Desktop: Settings → Resources → 4GB+ memory
   - 2+ CPU cores recommended

2. **Monitor System Load**
   - Watch Grafana for resource trends
   - Set up alerts for high memory

3. **Cache Management**
   - Redis stores price cache data
   - Check Redis memory: `docker-compose exec redis redis-cli info memory`

4. **Database Optimization**
   - ChromaDB stores vector embeddings
   - Larger collections require more memory

## Next Steps

1. **Review Documentation**
   - `DEPLOYMENT.md` - Detailed deployment guide
   - `MONITORING.md` - Monitoring and observability
   - `README.md` - Project overview

2. **Load Test Data**
   - Copy portfolios to `data/test_portfolios/`
   - Use `/parse_portfolio` endpoint

3. **Configure Alerts**
   - Set up Grafana alert notifications
   - Configure email/Slack integration

4. **Customize Dashboard**
   - Add custom panels to Grafana
   - Track business-specific metrics

5. **Scale for Production**
   - See DEPLOYMENT.md for Kubernetes setup
   - Implement multi-replica deployment

## Getting Help

| Issue | Resource |
|-------|----------|
| API Questions | `/docs` (Swagger UI) |
| Deployment Issues | `DEPLOYMENT.md` |
| Monitoring Issues | `MONITORING.md` |
| Code Issues | GitHub Issues |
| General Questions | README.md |

## System Architecture

```
┌─────────────┐
│   FastAPI   │ (8000)
│   Backend   │ ← Processes requests
└──────┬──────┘
       │
  ┌────┴────┐
  │          │
┌─▼──────┐  ┌─▼────────┐
│ ChromaDB│  │  Redis   │ (cache)
│ (8001)  │  │ (6379)   │
└────────┘  └──────────┘
       │
       ▼
┌──────────────┐
│ Prometheus   │ (9090)
│ Metrics      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Grafana    │ (3000)
│  Dashboard   │
└──────────────┘
```

## Support

- **Documentation**: Check DEPLOYMENT.md and MONITORING.md
- **Tests**: `pytest simple_test.py -v`
- **Logs**: `docker-compose logs -f`
- **Issues**: GitHub Issues tab

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready

Happy harvesting! 🚀
