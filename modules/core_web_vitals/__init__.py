from .speed_booster import CoreWebVitalsBooster
from .preload_and_lcp import (
    analyse_preload_and_bfcache,
    decompose_lcp_subparts,
)

__all__ = [
    "CoreWebVitalsBooster",
    "analyse_preload_and_bfcache",
    "decompose_lcp_subparts",
]
