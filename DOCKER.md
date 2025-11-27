# Docker Deployment Guide

This guide covers deploying Pulso in Docker containers with session-based caching and Redis support.

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f pulso-app

# Stop services
docker-compose down
```

### 2. Using Dockerfile Only

```bash
# Build image
docker build -t pulso-app .

# Run container
docker run -it \
  -e PULSO_CACHE_DIR=/cache \
  -e PULSO_SESSION_ID=my_session \
  -v pulso-cache:/cache \
  pulso-app python your_script.py
```

## Configuration

### Environment Variables

All configuration is done via environment variables:

```bash
# Cache Settings
PULSO_CACHE_DIR=/cache              # Cache directory
PULSO_SESSION_ID=default            # Session ID for isolation
PULSO_CACHE_BACKEND=filesystem      # Options: filesystem, redis
PULSO_REDIS_URL=redis://redis:6379/0  # Redis connection URL

# Logging
PULSO_LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR

# Default Domain Policies
PULSO_DEFAULT_TTL=1d
PULSO_DEFAULT_DRIVER=requests
PULSO_DEFAULT_MAX_RETRIES=3
PULSO_DEFAULT_RETRY_DELAY=1.0
PULSO_DEFAULT_FALLBACK=return_cached

# Playwright Settings
PULSO_PLAYWRIGHT_HEADLESS=true
PULSO_PLAYWRIGHT_TIMEOUT=30000
```

> Pulso still honors legacy `PULSO_*` environment variables for older deployments, but new setups should switch to the `PULSO_*` prefix.

### Using .env File

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

Docker Compose automatically loads `.env` file.

## Session-Based Caching

### What are Sessions?

Sessions allow you to isolate cache between different users, tenants, or contexts. Each session has its own cache namespace.

### Use Cases

1. **Multi-tenant Applications**
   ```python
   import pulso

   # Each tenant gets isolated cache
   pulso.set_session(f"tenant_{tenant_id}")
   data = pulso.fetch(url)
   ```

2. **User-Specific Caching**
   ```python
   pulso.set_session(f"user_{user_id}")
   personalized_data = pulso.fetch(user_url)
   ```

3. **A/B Testing**
   ```python
   pulso.set_session("variant_a" if is_variant_a else "variant_b")
   ```

4. **Environment Isolation**
   ```python
   pulso.set_session("development")  # vs "staging" or "production"
   ```

### Session API

```python
import pulso

# Set session
pulso.set_session("my_session")

# Get current session
current = pulso.get_session()  # Returns: "my_session"

# Reset to default
pulso.set_session("default")

# Or via environment
import os
os.environ["PULSO_SESSION_ID"] = "my_session"
```

## Redis Backend

### Why Redis?

- **Distributed caching** - Share cache across multiple containers
- **Persistence** - Survives container restarts
- **Performance** - Fast in-memory storage
- **Scalability** - Handles high concurrency

### Configuration

#### Docker Compose (Automatic)

```yaml
services:
  pulso-app:
    environment:
      - PULSO_CACHE_BACKEND=redis
      - PULSO_REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
```

#### Manual Setup

```python
import os

os.environ["PULSO_CACHE_BACKEND"] = "redis"
os.environ["PULSO_REDIS_URL"] = "redis://localhost:6379/0"

import pulso

# Now all cache operations use Redis
pulso.fetch("https://example.com")
```

### Redis + Sessions

Sessions work seamlessly with Redis:

```python
# Set session
pulso.set_session("user_123")

# Data stored in Redis as: pulso:user_123:<url_hash>
data = pulso.fetch(url)
```

## Docker Compose Examples

### Basic Setup

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - PULSO_SESSION_ID=production
      - PULSO_CACHE_BACKEND=filesystem
    volumes:
      - cache:/cache
    command: python app.py

volumes:
  cache:
```

### With Redis

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - PULSO_CACHE_BACKEND=redis
      - PULSO_REDIS_URL=redis://redis:6379/0
      - PULSO_SESSION_ID=${SESSION_ID:-default}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

### Multi-Worker Setup

```yaml
version: '3.8'

services:
  worker:
    build: .
    environment:
      - PULSO_CACHE_BACKEND=redis
      - PULSO_REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    deploy:
      replicas: 3  # Multiple workers share Redis cache

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

## Volume Management

### Persistent Cache

```bash
# Create named volume
docker volume create pulso-cache

# Use in container
docker run -v pulso-cache:/cache pulso-app

# Backup volume
docker run --rm -v pulso-cache:/cache -v $(pwd):/backup \
  alpine tar czf /backup/cache-backup.tar.gz -C /cache .

# Restore volume
docker run --rm -v pulso-cache:/cache -v $(pwd):/backup \
  alpine tar xzf /backup/cache-backup.tar.gz -C /cache
```

### Bind Mounts

```yaml
services:
  app:
    volumes:
      - ./cache:/cache  # Local directory
```

## Production Deployment

### Best Practices

1. **Use Redis for production**
   ```yaml
   environment:
     - PULSO_CACHE_BACKEND=redis
     - PULSO_REDIS_URL=redis://redis:6379/0
   ```

2. **Set appropriate session IDs**
   ```yaml
   environment:
     - PULSO_SESSION_ID=production
   ```

3. **Configure error handling**
   ```yaml
   environment:
     - PULSO_DEFAULT_FALLBACK=return_cached
     - PULSO_DEFAULT_MAX_RETRIES=5
   ```

4. **Enable Redis persistence**
   ```yaml
   redis:
     command: redis-server --appendonly yes
   ```

5. **Set resource limits**
   ```yaml
   app:
     deploy:
       resources:
         limits:
           cpus: '2'
           memory: 2G
   ```

### Health Checks

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "python", "-c", "import pulso"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Kubernetes Deployment

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pulso-config
data:
  PULSO_CACHE_BACKEND: "redis"
  PULSO_REDIS_URL: "redis://redis-service:6379/0"
  PULSO_SESSION_ID: "production"
  PULSO_LOG_LEVEL: "INFO"
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pulso-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pulso-app
  template:
    metadata:
      labels:
        app: pulso-app
    spec:
      containers:
      - name: pulso-app
        image: pulso-app:latest
        envFrom:
        - configMapRef:
            name: pulso-config
        volumeMounts:
        - name: cache
          mountPath: /cache
      volumes:
      - name: cache
        persistentVolumeClaim:
          claimName: pulso-cache-pvc
```

## Monitoring

### Logging

```python
import logging

logging.basicConfig(
    level=os.getenv("PULSO_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Pulso automatically logs:
# - Fetch attempts and retries
# - Cache hits/misses
# - Errors and fallbacks
```

### Metrics

Track cache performance:

```python
import pulso

# Before operation
metadata_before = pulso.get_metadata(url)

# Fetch
html = pulso.fetch(url)

# After operation
metadata_after = pulso.get_metadata(url)

# Was it a cache hit?
cache_hit = metadata_before == metadata_after
```

## Troubleshooting

### Cache Not Persisting

```bash
# Check volume mount
docker inspect <container_id> | grep Mounts -A 10

# Verify permissions
docker exec <container_id> ls -la /cache
```

### Redis Connection Issues

```bash
# Test Redis connectivity
docker exec pulso-app ping redis

# Check Redis logs
docker-compose logs redis

# Test Redis directly
docker exec redis redis-cli PING
```

### Session Isolation Issues

```python
# Verify session
import pulso
print(f"Current session: {pulso.get_session()}")

# Check cache location
print(f"Cache dir: {pulso.cache.cache_dir}")
```

## Examples

See:
- [examples/example_docker.py](examples/example_docker.py) - Docker application example
- [examples/example_sessions.py](examples/example_sessions.py) - Session-based caching examples
- [docker-compose.yml](docker-compose.yml) - Complete Docker setup
