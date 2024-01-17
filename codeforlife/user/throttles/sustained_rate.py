"""
© Ocado Group
Created on 17/01/2024 at 09:37:14(+00:00).
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttles requests sent over a sustained period of time from authenticated
    users.
    """

    scope = "user_sustained"


class AnonSustainedRateThrottle(AnonRateThrottle):
    """
    Throttles requests sent over a sustained period of time from anonymous
    users.
    """

    scope = "anon_sustained"
