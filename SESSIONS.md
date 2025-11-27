## Session-Based Caching Guide

Complete guide to using session-based caching in Pulso for multi-tenant and user-specific applications.

## Overview

Sessions allow you to isolate cache between different contexts. Each session maintains its own independent cache namespace, preventing data leakage between users, tenants, or environments.

## Basic Usage

### Setting a Session

```python
import pulso

# Set session for a specific user
pulso.set_session("user_123")

# All subsequent operations use this session
html = pulso.fetch("https://example.com")
```

### Getting Current Session

```python
current = pulso.get_session()
print(f"Current session: {current}")  # Outputs: user_123
```

### Default Session

```python
# Reset to default (shared) session
pulso.set_session("default")

# Or just use without setting (default is "default")
html = pulso.fetch(url)
```

## Use Cases

### 1. Multi-Tenant Applications

Isolate cache between different tenants/customers:

```python
import pulso

def process_tenant_data(tenant_id: str, urls: list):
    """Process data for a specific tenant with isolated cache."""
    # Set tenant-specific session
    pulso.set_session(f"tenant_{tenant_id}")

    # Register domain policies for this tenant
    pulso.register_domain(
        "api.example.com",
        ttl="30m",
        fallback_on_error="return_cached"
    )

    results = {}
    for url in urls:
        results[url] = pulso.fetch(url)

    return results

# Tenant A - gets its own cache
tenant_a_data = process_tenant_data("acme_corp", [
    "https://api.example.com/data",
    "https://api.example.com/users"
])

# Tenant B - completely isolated from Tenant A
tenant_b_data = process_tenant_data("globex", [
    "https://api.example.com/data",
    "https://api.example.com/users"
])
```

### 2. User-Specific Caching

Cache personalized data per user:

```python
import pulso

class UserDataFetcher:
    def __init__(self, user_id: str):
        self.user_id = user_id
        pulso.set_session(f"user_{user_id}")

    def fetch_dashboard(self):
        """Fetch user's personalized dashboard."""
        return pulso.fetch(f"https://app.com/dashboard?user={self.user_id}")

    def fetch_settings(self):
        """Fetch user's settings."""
        return pulso.fetch(f"https://app.com/settings?user={self.user_id}")

# Each user gets isolated cache
user1 = UserDataFetcher("alice")
alice_dashboard = user1.fetch_dashboard()

user2 = UserDataFetcher("bob")
bob_dashboard = user2.fetch_dashboard()
```

### 3. A/B Testing

Separate cache for different test variants:

```python
import pulso

def get_variant(user_id: str) -> str:
    """Determine A/B test variant for user."""
    return "variant_a" if hash(user_id) % 2 == 0 else "variant_b"

def fetch_with_variant(user_id: str, url: str):
    """Fetch content with A/B test variant isolation."""
    variant = get_variant(user_id)
    pulso.set_session(f"ab_test_{variant}")

    return pulso.fetch(url)

# Users in variant A share cache
data_a = fetch_with_variant("user_1", "https://example.com/experiment")

# Users in variant B share different cache
data_b = fetch_with_variant("user_2", "https://example.com/experiment")
```

### 4. Environment Isolation

Separate cache for dev/staging/production:

```python
import pulso
import os

# Set environment-based session
env = os.getenv("ENVIRONMENT", "development")
pulso.set_session(env)

# Development, staging, and production each use separate cache
html = pulso.fetch("https://api.example.com/config")
```

### 5. Request-Scoped Sessions

Create temporary sessions for specific operations:

```python
import pulso
from contextlib import contextmanager

@contextmanager
def temp_session(session_id: str):
    """Context manager for temporary sessions."""
    original = pulso.get_session()
    try:
        pulso.set_session(session_id)
        yield
    finally:
        pulso.set_session(original)

# Use temporary session
with temp_session("temp_operation"):
    data = pulso.fetch("https://example.com/temp")
    # Process data...

# Automatically restored to original session
```

## Configuration

### Via Code

```python
import pulso

# Set session programmatically
pulso.set_session("my_session")
```

### Via Environment Variables

```bash
# .env file
PULSO_SESSION_ID=production
```

```python
import pulso

# Load from environment
pulso.load_config(".env")

# Session is now "production"
print(pulso.get_session())
```

> Pulso still reads the legacy `PULSO_*` environment variables, so existing deployments keep working while you migrate to the `PULSO_*` versions.

### Via Docker

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - PULSO_SESSION_ID=${SESSION_ID}
```

```bash
# Run with specific session
SESSION_ID=user_123 docker-compose up
```

## Cache Storage

### Filesystem Layout

Sessions create subdirectories in the cache:

```
~/.cache/pulso/
├── sessions/
│   ├── user_123/
│   │   ├── example.com/
│   │   │   ├── abc123.json
│   │   │   └── abc123.html
│   ├── user_456/
│   │   ├── example.com/
│   │   │   ├── def456.json
│   │   │   └── def456.html
│   └── default/
│       └── ...
```

### Redis Storage

With Redis backend, sessions use key prefixes:

```
pulso:user_123:<url_hash>
pulso:user_456:<url_hash>
pulso:default:<url_hash>
```

## Cache Management

### Clear Session Cache

```python
import pulso

# Set to specific session
pulso.set_session("temp_session")

# Clear only this session's cache
pulso.cache.clear()

# Other sessions remain intact
```

### Clear Specific Domain in Session

```python
pulso.set_session("user_123")
pulso.cache.clear(domain="example.com")
```

### Clear Specific URL in Session

```python
pulso.set_session("user_123")
pulso.cache.clear(url="https://example.com/page")
```

## Best Practices

### 1. Session Naming Convention

Use consistent, descriptive session IDs:

```python
# Good
pulso.set_session(f"tenant_{tenant_id}")
pulso.set_session(f"user_{user_id}")
pulso.set_session(f"env_{environment}")

# Avoid
pulso.set_session("1")
pulso.set_session("temp")
```

### 2. Session Lifecycle

Set session early in request/operation lifecycle:

```python
# Flask example
from flask import g, request

@app.before_request
def set_session():
    user_id = request.headers.get("X-User-ID")
    if user_id:
        pulso.set_session(f"user_{user_id}")
    else:
        pulso.set_session("anonymous")
```

### 3. Session Isolation

Ensure sessions don't leak between operations:

```python
# FastAPI example
from fastapi import Depends

async def get_session(user_id: str = Header(...)):
    pulso.set_session(f"user_{user_id}")
    try:
        yield
    finally:
        pulso.set_session("default")
```

### 4. Monitor Session Usage

Track session cache usage:

```python
import pulso
from pathlib import Path

def get_session_cache_size(session_id: str) -> int:
    """Get total cache size for a session."""
    pulso.set_session(session_id)
    cache_dir = pulso.cache.cache_dir

    total_size = 0
    for file in cache_dir.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size

    return total_size

# Check cache sizes
print(f"User 123: {get_session_cache_size('user_123')} bytes")
print(f"User 456: {get_session_cache_size('user_456')} bytes")
```

## Advanced Patterns

### Session Pool

Manage multiple sessions efficiently:

```python
import pulso

class SessionPool:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str):
        """Get or create session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = session_id
            pulso.set_session(session_id)
        return session_id

    def clear_old_sessions(self, max_sessions: int = 100):
        """Clear oldest sessions when limit reached."""
        if len(self.sessions) > max_sessions:
            # Clear oldest sessions (simple FIFO)
            old_sessions = list(self.sessions.keys())[:len(self.sessions) - max_sessions]
            for session_id in old_sessions:
                pulso.set_session(session_id)
                pulso.cache.clear()
                del self.sessions[session_id]

pool = SessionPool()
```

### Session Middleware

Create middleware for automatic session management:

```python
# Django example
class SessionCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set session based on user
        if request.user.is_authenticated:
            session_id = f"user_{request.user.id}"
        else:
            session_id = f"anonymous_{request.session.session_key}"

        pulso.set_session(session_id)

        response = self.get_response(request)
        return response
```

## Troubleshooting

### Sessions Not Isolating

Verify session is set:
```python
print(f"Current session: {pulso.get_session()}")
print(f"Cache dir: {pulso.cache.cache_dir}")
```

### Cache Growing Too Large

Implement session cleanup:
```python
import pulso
from datetime import datetime, timedelta

def cleanup_old_sessions(max_age_days: int = 7):
    """Remove sessions older than max_age_days."""
    cache_base = Path.home() / ".cache" / "pulso" / "sessions"

    cutoff = datetime.now() - timedelta(days=max_age_days)

    for session_dir in cache_base.iterdir():
        if session_dir.is_dir():
            mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
            if mtime < cutoff:
                shutil.rmtree(session_dir)
                print(f"Removed old session: {session_dir.name}")
```

### Session ID Conflicts

Use unique, namespaced session IDs:
```python
# Include namespace to avoid conflicts
pulso.set_session(f"app_name:user:{user_id}")
pulso.set_session(f"app_name:tenant:{tenant_id}")
```

## See Also

- [DOCKER.md](DOCKER.md) - Docker deployment with session support
- [README.md](README.md) - Main documentation
- [examples/example_sessions.py](examples/example_sessions.py) - Complete examples
