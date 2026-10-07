"""
tests/test_tier_switcher.py
===========================
"""

import time
import pytest
from src.tier_switcher import DynamicTierSwitcher


def test_tier_switcher_transitions():
    switcher = DynamicTierSwitcher(
        high_load_thresh=75.0,
        medium_load_thresh=45.0,
        hysteresis=5.0,
        dwell_time_seconds=0.01,
        simulate_resources=True
    )
    
    # Initial state (low load)
    assert switcher.current_tier == "FULL"
    
    # Moderate load (45% - 75%)
    switcher.evaluate_tier(55.0)
    time.sleep(0.02)
    tier = switcher.evaluate_tier(55.0)
    assert tier == "REDUCED"
    
    # High load (>75%)
    switcher.evaluate_tier(85.0)
    time.sleep(0.02)
    tier = switcher.evaluate_tier(85.0)
    assert tier == "MINIMAL"
    
    # Recovery with hysteresis (must drop below medium - 5 = 40% to return to FULL)
    switcher.evaluate_tier(42.0)
    time.sleep(0.02)
    tier = switcher.evaluate_tier(42.0)
    assert tier == "REDUCED"
    
    switcher.evaluate_tier(30.0)
    time.sleep(0.02)
    tier = switcher.evaluate_tier(30.0)
    assert tier == "FULL"
