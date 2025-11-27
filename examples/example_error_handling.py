"""Example of error handling and fallback behavior in Pulso."""

import pulso
import logging

# Setup logging to see error messages
logging.basicConfig(level=logging.INFO)


# Example 1: Default behavior - return cached data on error
def error_reporter(url, exception):
    """Custom error callback to log or report failures."""
    print(f"[ERROR CALLBACK] Failed to fetch {url}: {exception}")


pulso.register_domain(
    "example.com",
    ttl="1h",
    driver="requests",
    max_retries=3,
    retry_delay=1.0,
    fallback_on_error="return_cached",  # Return last cached data on error (default)
    on_error=error_reporter  # Optional: callback on errors
)

url = "https://example.com"

# First successful fetch
html = pulso.fetch(url)
print(f"Initial fetch: {len(html) if html else 0} bytes")

# If later fetch fails (e.g., network down), it will:
# 1. Retry 3 times with 1 second delay between attempts
# 2. Call error_reporter callback on each failure
# 3. Return the cached data from the first fetch
# html = pulso.fetch(url, force=True)  # Would return cached data on error


# Example 2: Return None on error (don't raise exception)
pulso.register_domain(
    "api.example.com",
    ttl="30m",
    driver="requests",
    max_retries=2,
    fallback_on_error="return_none",  # Return None instead of raising error
    on_error=lambda url, e: print(f"API call failed: {url}")
)

api_url = "https://api.example.com/data"
data = pulso.fetch(api_url)

if data is None:
    print("API unavailable, using default data")
    # Use fallback logic
else:
    print(f"API data retrieved: {len(data)} bytes")


# Example 3: Raise error (strict mode)
pulso.register_domain(
    "critical.example.com",
    ttl="5m",
    driver="requests",
    max_retries=5,
    retry_delay=2.0,
    fallback_on_error="raise_error",  # Raise exception on failure
    on_error=lambda url, e: print(f"Critical failure: {url}")
)

try:
    critical_url = "https://critical.example.com/important"
    html = pulso.fetch(critical_url)
except pulso.FetchError as e:
    print(f"Critical fetch failed: {e}")
    # Handle error appropriately


# Example 4: Complex error tracking
error_log = []


def track_errors(url, exception):
    """Track all errors for monitoring."""
    error_log.append({
        "url": url,
        "error": str(exception),
        "timestamp": __import__("time").time()
    })
    print(f"Logged error #{len(error_log)}: {url}")


pulso.register_domain(
    "monitored.site",
    ttl="15m",
    driver="requests",
    max_retries=3,
    fallback_on_error="return_cached",
    on_error=track_errors
)

# View all registered domains and their policies
print("\n=== Registered Domains ===")
domains = pulso.get_registered_domains()
for domain, policy in domains.items():
    print(f"\n{domain}:")
    print(f"  TTL: {policy.ttl_seconds}s")
    print(f"  Driver: {policy.driver}")
    print(f"  Max retries: {policy.max_retries}")
    print(f"  Retry delay: {policy.retry_delay}s")
    print(f"  Fallback: {policy.fallback_on_error}")
    print(f"  Error callback: {'Yes' if policy.on_error else 'No'}")
