"""Example usage of the Pulso package."""

import pulso

# Register some domains with their policies
pulso.register_domain(
    "example.com",
    ttl="12h",
    driver="requests"
)

pulso.register_domain(
    "news.site",
    ttl="6h",
    driver="playwright"
)

# Get all registered domains
domains = pulso.get_registered_domains()
print(f"Registered domains: {list(domains.keys())}")
for domain, policy in domains.items():
    print(f"  {domain}: ttl={policy.ttl_seconds}s, driver={policy.driver}")

# Fetch content (uses cache if fresh)
url = "https://example.com"
html = pulso.fetch(url)
print(f"Fetched {len(html)} bytes from {url}")

# Check if content has changed
if pulso.has_changed(url):
    print("Content has changed!")
    # Create a snapshot of the new content
    snapshot_path = pulso.snapshot(url)
    print(f"Snapshot saved to: {snapshot_path}")
else:
    print("No changes detected")

# Get metadata about the cached URL
metadata = pulso.get_metadata(url)
if metadata:
    print(f"\nMetadata:")
    print(f"  Content hash: {metadata['content_hash'][:16]}...")
    print(f"  Fetch time: {metadata['fetch_time']}")
    print(f"  Change time: {metadata['change_time']}")
    print(f"  Change count: {metadata['change_count']}")

# Clear cache for specific domain
# pulso.cache.clear(domain="example.com")

# Clear cache for specific URL
# pulso.cache.clear(url=url)
