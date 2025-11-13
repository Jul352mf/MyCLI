"""Discovery plugin framework scaffolding.

Users of this package typically import only `DiscoveryEngine` and
`DiscoveryPlugin` for registering plugins and running discovery.
"""

from .base import DiscoveryPlugin  # noqa: F401
from .engine import DiscoveryEngine, DiscoveryResult  # noqa: F401
