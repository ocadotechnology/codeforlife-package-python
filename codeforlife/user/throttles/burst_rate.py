"""
© Ocado Group
Created on 17/01/2024 at 09:36:24(+00:00).
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """Throttles requests sent in bursts from authenticated users."""

    scope = "user_burst"


class AnonBurstRateThrottle(AnonRateThrottle):
    """Throttles requests sent in bursts from anonymous users."""

    scope = "anon_burst"
