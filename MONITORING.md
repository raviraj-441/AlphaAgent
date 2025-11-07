# Monitoring and Observability Guide

## Overview

AlphaAgent includes comprehensive monitoring and observability features using industry-standard tools:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboarding
- **Uvicorn/FastAPI**: Built-in metrics exposure
- **Custom Middleware**: Request tracking and performance metrics

## Architecture

```
┌─────────────────┐
│   FastAPI App   │ (/metrics endpoint)
│  + Middleware   │ (PrometheusMiddleware)
└────────┬────────┘
         │ Metrics (HTTP/1.1)
         ↓
┌─────────────────┐
│  Prometheus     │ (9090)
│  Time-series DB │ Scrapes every 15s
└────────┬────────┘
         │ Queries
         ↓
┌─────────────────┐
│    Grafana      │ (3000)
│   Dashboards    │ Visualizes metrics
└─────────────────┘
```

## Metrics Collected

### Request Metrics

- **http_requests_total**: Total HTTP requests by method, endpoint, status
- **http_request_duration_seconds**: Request latency histogram (p50, p95, p99)
- **http_request_size_bytes**: Request payload size
- **http_response_size_bytes**: Response payload size
- **http_requests_in_progress**: Currently processing requests
- **http_exceptions_total**: Exceptions by type

### Performance Metrics

- **P50 Latency**: Median request time (good indicator of typical performance)
- **P95 Latency**: 95th percentile (captures slow requests)
- **P99 Latency**: 99th percentile (captures very slow requests)
- **Request Rate**: Requests per minute (throughput)
- **Error Rate**: Failed requests as percentage

### Optional Metrics (if enabled)

- **db_query_duration_seconds**: Database query performance
- **cache_hits_total**: Cache hit count
- **cache_misses_total**: Cache miss count

## Setup

### 1. Enable Prometheus in docker-compose.yml

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Or individually
docker-compose up -d prometheus grafana
```

### 2. Verify Prometheus is Scraping

```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# Should show alphaagent-api as UP
```

### 3. Add Grafana Data Source

1. Open Grafana: `http://localhost:3000`
2. Login: `admin` / (password from `.env`)
3. Go to **Configuration** → **Data Sources**
4. Click **Add data source**
5. Select **Prometheus**
6. URL: `http://prometheus:9090`
7. Click **Save & Test**

### 4. Import Dashboard

1. Go to **+ Create** → **Import**
2. Upload `monitoring/grafana/dashboards/alphaagent-dashboard.json`
3. Select the Prometheus data source
4. Click **Import**

## Key Dashboards

### API Performance Dashboard

Shows:
- Request rate (req/min)
- P95 latency (seconds)
- Error rate (5xx per minute)
- Active requests
- Endpoint breakdown

### Service Health

- API availability (uptime percentage)
- ChromaDB connectivity
- Redis cache status
- Error trends

## Alert Rules

Configured alerts in `monitoring/alerts.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | Error rate > 5% for 5 min | Warning |
| APIDown | API unreachable for 1 min | Critical |
| HighLatency | P95 > 1 second for 5 min | Warning |
| ChromaDown | ChromaDB unreachable for 1 min | Critical |
| HighMemory | Memory > 80% for 5 min | Warning |
| HealthCheckFailing | Health check failed for 2 min | Critical |

## Common Queries

### Request Rate (requests per minute)

```promql
rate(http_requests_total{job="alphaagent-api"}[5m]) * 60
```

### Error Rate (percentage)

```promql
(
  rate(http_requests_total{job="alphaagent-api", status=~"5.."}[5m])
  /
  rate(http_requests_total{job="alphaagent-api"}[5m])
) * 100
```

### P95 Latency (seconds)

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="alphaagent-api"}[5m]))
```

### Average Latency by Endpoint

```promql
rate(http_request_duration_seconds_sum{job="alphaagent-api"}[5m])
/
rate(http_request_duration_seconds_count{job="alphaagent-api"}[5m])
```

### Active Requests

```promql
http_requests_in_progress{job="alphaagent-api"}
```

### Request Count by Status

```promql
rate(http_requests_total{job="alphaagent-api"}[5m])
```

## Prometheus Configuration

### Scrape Targets

Located in `monitoring/prometheus.yml`:

- **alphaagent-api**: Main FastAPI application (10s interval)
- **alphaagent-chroma**: ChromaDB vector store (30s interval)
- **alphaagent-redis**: Redis cache (15s interval)
- **node**: System metrics (30s interval, optional)

### Tuning Scrape Intervals

```yaml
# More frequent scraping (more accurate, more storage)
scrape_interval: 5s    # Default: 15s

# Less frequent scraping (less accurate, less storage)
scrape_interval: 60s   # For non-critical metrics
```

### Retention Policy

```yaml
# Modify prometheus command in docker-compose.yml
command:
  - "--storage.tsdb.retention.time=30d"  # Keep 30 days of data
  - "--storage.tsdb.retention.size=50GB"  # Or limit by size
```

## Grafana Advanced Features

### Custom Panels

Create panels for:
- P99 latency
- Request size distribution
- Error breakdown by endpoint
- Cache hit rate trends

### Alert Notifications

Configure notifications to:
- **Slack**: `/alerting/notification/slack`
- **Email**: `/alerting/notification/email`
- **PagerDuty**: `/alerting/notification/pagerduty`

### Variable Panels

Create dashboard variables for:
- Time range
- Job selector
- Endpoint filter

## Performance Baseline

Expected metrics for healthy system:

| Metric | Value | Notes |
|--------|-------|-------|
| Request Rate | 10-100 req/s | Depends on load |
| P50 Latency | 50-200ms | Normal endpoint |
| P95 Latency | 200-500ms | Some variance |
| P99 Latency | 500ms-2s | Acceptable peak |
| Error Rate | < 1% | Below 5% warning |
| Active Requests | < 50 | Under normal load |

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check target status
curl http://localhost:9090/api/v1/targets

# View prometheus logs
docker-compose logs prometheus

# Verify metrics endpoint
curl http://localhost:8000/metrics
```

### Grafana Data Not Showing

```bash
# Test Prometheus connectivity from Grafana container
docker-compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Check data source configuration
# Settings → Data Sources → Prometheus
# URL should be http://prometheus:9090 (from Grafana's perspective)
```

### High Memory Usage

```bash
# Check Prometheus storage
curl http://localhost:9090/api/v1/tsdb/stats | jq '.seriesCountByMetricName'

# Reduce retention
# monitoring/prometheus.yml: --storage.tsdb.retention.time=7d

# Or remove old data
docker-compose exec prometheus rm -rf /prometheus/wal/*
```

## Integration with Application Code

### Using Metrics in Code

```python
from backend.utils.prometheus_metrics import (
    record_db_query,
    record_cache_hit,
    record_cache_miss
)

# Track database queries
with measure_time() as elapsed:
    result = db.query("SELECT * FROM portfolio")
record_db_query("select", "portfolio", elapsed.seconds)

# Track cache operations
if cache.get(key):
    record_cache_hit("portfolio_cache")
else:
    record_cache_miss("portfolio_cache")
    cache.set(key, value)
```

### Custom Metrics

Add custom metrics to `backend/utils/prometheus_metrics.py`:

```python
from prometheus_client import Counter, Histogram

CUSTOM_COUNTER = Counter(
    'custom_events_total',
    'Total custom events',
    ['event_type']
)

CUSTOM_HISTOGRAM = Histogram(
    'custom_duration_seconds',
    'Custom operation duration',
    ['operation']
)
```

## Best Practices

### 1. Alert Fatigue Prevention

- Set thresholds based on actual baselines
- Use severity levels (warning vs critical)
- Implement alert suppression for known issues

### 2. Metric Cardinality

- Avoid high-cardinality labels (like user IDs)
- Use endpoint normalization (e.g., `/api/portfolio/{id}` not `/api/portfolio/123`)
- Limit the number of label combinations

### 3. Data Retention

- Balance retention time with storage capacity
- Archive old data externally if needed
- Use Prometheus remote storage for long-term retention

### 4. Dashboard Design

- Group related metrics on same dashboard
- Use consistent color schemes (green = good, red = bad)
- Include runbooks for critical alerts
- Keep dashboards simple and focused

## SLA Monitoring

Create SLOs (Service Level Objectives):

```yaml
# 99.9% uptime (8.64s downtime per day)
availability_slo = (rate(up{job="alphaagent-api"}[1d]) > 0.999)

# 95% of requests < 500ms
latency_slo = (histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1d])) < 0.5)

# Error rate < 1%
error_slo = (rate(http_requests_total{status=~"5.."}[1d]) / rate(http_requests_total[1d]) < 0.01)
```

## External Monitoring

### Third-party Services

- **Datadog**: Agent for metrics
- **New Relic**: APM and monitoring
- **Sentry**: Error tracking
- **StatusPage**: Public status page

### Remote Storage

```yaml
# Send metrics to external system
remote_write:
  - url: https://example.prometheus.cloud/write
    basic_auth:
      username: 'prometheus'
      password: 'secret'
```

## Support

For issues with monitoring:
1. Check Prometheus targets
2. Verify Grafana data source connectivity
3. Review application logs
4. Check system resources (CPU, memory, disk)
