# Pulso Examples

This folder contains complete working examples demonstrating various features of the Pulso library.

## Basic Usage

### [example.py](example.py)
Basic usage example showing:
- Domain registration with TTL
- Fetching URLs with cache
- Change detection
- Content snapshots
- Metadata inspection

**Run:**
```bash
python examples/example.py
```

## Error Handling

### [example_error_handling.py](example_error_handling.py)
Demonstrates error handling patterns:
- Automatic retry logic with configurable attempts and delays
- Three fallback behaviors:
  - `return_cached` - Return last cached data on error (default)
  - `raise_error` - Raise FetchError on failure
  - `return_none` - Return None on failure
- Error callbacks for monitoring and logging
- Handling transient vs permanent failures

**Run:**
```bash
python examples/example_error_handling.py
```

## Session-Based Caching

### [example_sessions.py](example_sessions.py)
Six complete examples of session isolation:
1. **Multi-tenant applications** - Separate cache per tenant
2. **User-specific caching** - Per-user personalized data
3. **A/B testing** - Isolated cache for test variants
4. **Environment isolation** - Dev/staging/production separation
5. **Request-scoped sessions** - Temporary sessions with context manager
6. **Session cleanup** - Managing and clearing old sessions

**Run:**
```bash
python examples/example_sessions.py
```

## Docker Deployment

### [example_docker.py](example_docker.py)
Production-ready Docker application example:
- Environment-based configuration
- Redis cache backend integration
- Proper logging setup
- Error handling with fallback behaviors
- Metadata tracking and reporting
- Health check patterns

**Run with Docker:**
```bash
# Using docker-compose (recommended)
docker-compose up

# Or directly with Docker
docker build -t pulso-app .
docker run --rm pulso-app python examples/example_docker.py
```

**Run with Redis:**
```bash
# Start Redis
docker-compose up -d redis

# Run with Redis backend
PULSO_CACHE_BACKEND=redis PULSO_REDIS_URL=redis://localhost:6379/0 python examples/example_docker.py
```

## Before Running Examples

### Install Dependencies

```bash
# Basic installation
pip install -e .

# With Redis support
pip install -e ".[redis]"

# Development installation (includes testing tools)
pip install -e ".[dev]"

# Install Playwright browsers (required for playwright driver)
playwright install
```

### Environment Configuration

Some examples support environment variables. Create a `.env` file:

```bash
# Cache settings
PULSO_CACHE_DIR=/path/to/cache
PULSO_SESSION_ID=my_session
PULSO_CACHE_BACKEND=filesystem  # or redis

# Redis (if using Redis backend)
PULSO_REDIS_URL=redis://localhost:6379/0

# Logging
PULSO_LOG_LEVEL=INFO

# Default policies
PULSO_DEFAULT_TTL=1d
PULSO_DEFAULT_DRIVER=requests
PULSO_DEFAULT_MAX_RETRIES=3
PULSO_DEFAULT_FALLBACK=return_cached
```

Then load in your script:
```python
import pulso
pulso.load_config(".env")
```

> Legacy `PULSO_*` environment variables are still supported, but migrating to the `PULSO_*` versions is recommended.

## Common Patterns

### Quick Start Pattern
```python
import pulso

# Register domain with policies
pulso.register_domain(
    "example.com",
    ttl="1h",
    max_retries=3,
    fallback_on_error="return_cached"
)

# Fetch with automatic caching
html = pulso.fetch("https://example.com/page")

# Check if content changed
if pulso.has_changed("https://example.com/page"):
    print("Content updated!")
```

### Multi-Tenant Pattern
```python
import pulso

def process_tenant(tenant_id: str):
    # Isolate cache by tenant
    pulso.set_session(f"tenant_{tenant_id}")

    # Each tenant has independent cache
    data = pulso.fetch("https://api.example.com/data")
    return data
```

### Error Handling Pattern
```python
import pulso

pulso.register_domain(
    "example.com",
    max_retries=5,
    retry_delay=2.0,
    fallback_on_error="return_cached",
    on_error=lambda url, e: logger.error(f"Failed: {url} - {e}")
)

# Will retry 5 times, then return cached data if available
html = pulso.fetch("https://example.com/page")
```

## Troubleshooting

### Cache Location
```python
import pulso
print(f"Cache directory: {pulso.cache.cache_dir}")
```

### Clear Cache
```python
# Clear all cache
pulso.cache.clear()

# Clear specific domain
pulso.cache.clear(domain="example.com")

# Clear specific URL
pulso.cache.clear(url="https://example.com/page")
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## See Also

- [../README.md](../README.md) - Main documentation
- [../DOCKER.md](../DOCKER.md) - Docker deployment guide
- [../SESSIONS.md](../SESSIONS.md) - Session-based caching guide
