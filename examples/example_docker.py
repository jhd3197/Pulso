"""Example application for Docker deployment with Redis caching."""

import pulso
import os
import logging

# Setup logging
logging.basicConfig(
    level=os.getenv("PULSO_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main application using Pulso in Docker environment."""

    logger.info("Starting Pulso application in Docker")

    # Configuration is loaded from environment variables automatically
    logger.info(f"Session ID: {pulso.get_session()}")
    logger.info(f"Cache backend: {os.getenv('PULSO_CACHE_BACKEND', 'filesystem')}")

    # Register domains with error handling
    pulso.register_domain(
        "httpbin.org",
        ttl="5m",
        driver="requests",
        max_retries=3,
        fallback_on_error="return_cached",
        on_error=lambda url, e: logger.error(f"Fetch failed: {url} - {e}")
    )

    # Example URLs
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/user-agent",
    ]

    # Fetch and process
    for url in urls:
        logger.info(f"Fetching: {url}")

        try:
            html = pulso.fetch(url)

            if html:
                logger.info(f"Success: {url} - {len(html)} bytes")

                # Get metadata
                metadata = pulso.get_metadata(url)
                if metadata:
                    logger.info(
                        f"  Hash: {metadata['content_hash'][:16]}... "
                        f"Changes: {metadata['change_count']}"
                    )
            else:
                logger.warning(f"No data returned for: {url}")

        except pulso.FetchError as e:
            logger.error(f"Failed to fetch {url}: {e}")

    # Check for changes
    logger.info("\nChecking for changes...")
    for url in urls:
        if pulso.has_changed(url):
            logger.info(f"Changed: {url}")
            # Create snapshot
            snapshot_path = pulso.snapshot(url)
            if snapshot_path:
                logger.info(f"  Snapshot saved: {snapshot_path}")
        else:
            logger.info(f"No change: {url}")

    # View registered domains
    logger.info("\nRegistered domains:")
    domains = pulso.get_registered_domains()
    for domain, policy in domains.items():
        logger.info(
            f"  {domain}: TTL={policy.ttl_seconds}s, "
            f"Driver={policy.driver}, Retries={policy.max_retries}"
        )

    logger.info("Application completed")


if __name__ == "__main__":
    main()
