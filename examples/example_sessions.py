"""Example of session-based caching in Pulso."""

import pulso

# Example 1: Basic session usage
print("=== Example 1: Basic Session Usage ===")

# Set session for user 1
pulso.set_session("user_123")
print(f"Current session: {pulso.get_session()}")

pulso.register_domain("example.com", ttl="1h")

# Fetch data for user 1 - cached in user_123 session
url = "https://example.com"
html_user1 = pulso.fetch(url)
print(f"Fetched for user_123: {len(html_user1) if html_user1 else 0} bytes")

# Switch to user 2 session
pulso.set_session("user_456")
print(f"Switched to session: {pulso.get_session()}")

# This will fetch again because it's a different session
html_user2 = pulso.fetch(url)
print(f"Fetched for user_456: {len(html_user2) if html_user2 else 0} bytes")

# Switch back to user 1 - will use cached data
pulso.set_session("user_123")
html_user1_cached = pulso.fetch(url)
print(f"Cached for user_123: {len(html_user1_cached) if html_user1_cached else 0} bytes")


# Example 2: Multi-tenant application
print("\n=== Example 2: Multi-tenant Application ===")


def fetch_for_tenant(tenant_id: str, urls: list) -> dict:
    """Fetch data for a specific tenant with isolated cache."""
    # Set tenant-specific session
    pulso.set_session(f"tenant_{tenant_id}")

    results = {}
    for url in urls:
        results[url] = pulso.fetch(url)

    return results


# Tenant A
tenant_a_data = fetch_for_tenant("company_a", [
    "https://example.com/data",
    "https://example.com/config"
])
print(f"Tenant A: {len(tenant_a_data)} URLs fetched")

# Tenant B - completely isolated cache
tenant_b_data = fetch_for_tenant("company_b", [
    "https://example.com/data",
    "https://example.com/config"
])
print(f"Tenant B: {len(tenant_b_data)} URLs fetched")


# Example 3: Using environment variables
print("\n=== Example 3: Environment Configuration ===")

import os

# Set via environment variable (typically in .env file)
os.environ["PULSO_SESSION_ID"] = "production_session"
os.environ["PULSO_CACHE_DIR"] = "/tmp/pulso_cache"

# Reload configuration
pulso.load_config()  # Or load from .env file: pulso.load_config(".env")

print(f"Session from env: {pulso.get_session()}")


# Example 4: Session-based change detection
print("\n=== Example 4: Session-based Change Detection ===")

# Different users might have different cached versions
pulso.set_session("monitor_1")
url = "https://example.com/news"

# First monitor
pulso.fetch(url)
if pulso.has_changed(url):
    print("Monitor 1: Content changed!")

# Second monitor (different session, different baseline)
pulso.set_session("monitor_2")
if pulso.has_changed(url):
    print("Monitor 2: Content changed!")


# Example 5: Clear session-specific cache
print("\n=== Example 5: Cache Management per Session ===")

pulso.set_session("temp_session")
pulso.fetch("https://example.com/temp")

# View cache info
metadata = pulso.get_metadata("https://example.com/temp")
if metadata:
    print(f"Temp session cache: {metadata['content_hash'][:16]}...")

# Clear cache for specific session
# Note: Cache is isolated by session automatically
pulso.cache.clear()
print("Temp session cache cleared")

# Switch to different session - cache still intact
pulso.set_session("user_123")
metadata = pulso.get_metadata(url)
if metadata:
    print(f"User 123 cache still intact: {metadata['content_hash'][:16]}...")


# Example 6: Default session
print("\n=== Example 6: Default Session ===")

# Reset to default session (shared across non-session usage)
pulso.set_session("default")
print(f"Using default session: {pulso.get_session()}")

# This is equivalent to not setting a session at all
html = pulso.fetch("https://example.com")
print(f"Default session fetch: {len(html) if html else 0} bytes")
