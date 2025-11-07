"""
Prometheus instrumentation for FastAPI metrics collection.
"""

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, REGISTRY
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

# Create metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

REQUESTS_QUEUED = Gauge(
    'http_requests_queued',
    'Number of HTTP requests waiting to be processed'
)

# Exception metrics
EXCEPTION_COUNT = Counter(
    'http_exceptions_total',
    'Total HTTP exceptions',
    ['method', 'endpoint', 'exception_type']
)

# Database/Cache metrics (optional)
DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    buckets=(0.001, 0.01, 0.1, 0.5, 1.0)
)

CACHE_HIT_RATE = Counter(
    'cache_hits_total',
    'Cache hits',
    ['cache_name']
)

CACHE_MISS_RATE = Counter(
    'cache_misses_total',
    'Cache misses',
    ['cache_name']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting Prometheus metrics on HTTP requests/responses.
    """

    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Extract endpoint path (normalize to avoid high cardinality)
        endpoint = self._normalize_endpoint(request.url.path)
        method = request.method
        
        # Increment active requests
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
        
        try:
            # Record request size
            request_size = len(await request.body()) if request.body else 0
            REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(request_size)
            
            # Call the actual endpoint
            response = await call_next(request)
            
            # Record response size
            response_size = response.headers.get('content-length', 0)
            if response_size:
                RESPONSE_SIZE.labels(method=method, endpoint=endpoint).observe(int(response_size))
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
            
            return response
            
        except Exception as exc:
            # Record exception
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            EXCEPTION_COUNT.labels(
                method=method, 
                endpoint=endpoint, 
                exception_type=type(exc).__name__
            ).inc()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()

    @staticmethod
    def _normalize_endpoint(path: str) -> str:
        """
        Normalize endpoint path to avoid high cardinality.
        E.g., /api/portfolio/123 -> /api/portfolio/{id}
        """
        parts = path.split('/')
        normalized = []
        
        for part in parts:
            if part.isdigit() or (part and part[0].isdigit()):
                # Replace numeric IDs with {id}
                normalized.append('{id}')
            elif len(part) == 36 and part.count('-') == 4:
                # Replace UUIDs with {uuid}
                normalized.append('{uuid}')
            else:
                normalized.append(part)
        
        return '/'.join(normalized)


def get_metrics():
    """Generate Prometheus metrics in text format."""
    return generate_latest(REGISTRY)


def record_db_query(operation: str, table: str, duration: float):
    """Record database query metrics."""
    DB_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)


def record_cache_hit(cache_name: str):
    """Record cache hit."""
    CACHE_HIT_RATE.labels(cache_name=cache_name).inc()


def record_cache_miss(cache_name: str):
    """Record cache miss."""
    CACHE_MISS_RATE.labels(cache_name=cache_name).inc()
