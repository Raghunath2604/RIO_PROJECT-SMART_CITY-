"""
tests/test_fr5_hysteresis.py
============================
Automated unit and integration tests verifying FR5 dynamic tier switcher logic,
asymmetric deadband hysteresis (ΔH = 5), and dwell-time smoothing (τ = 1.0s).
"""

import time
import pytest
from src.tier_switcher import DynamicTierSwitcher


def test_initial_tier_state_low_cpu():
    """Initial tier state under low CPU load (< 45%) must be FULL tier."""
    switcher = DynamicTierSwitcher(
        high_load_thresh=75.0,
        medium_load_thresh=45.0,
        hysteresis=5.0,
        dwell_time_seconds=1.0,
        simulate_resources=True
    )
    t0 = 1000.0
    switcher.last_switch_time = t0 - 2.0

    tier = switcher.evaluate_tier(30.0, current_time=t0)
    assert tier == "FULL"
    assert switcher.TIERS[tier] == "LightGBM"


def test_dwell_time_prevents_rapid_flapping():
    """Dwell time smoothing (τ = 1.0s) prevents rapid switching during burst spikes."""
    switcher = DynamicTierSwitcher(
        high_load_thresh=75.0,
        medium_load_thresh=45.0,
        hysteresis=5.0,
        dwell_time_seconds=1.0
    )
    t0 = 1000.0
    switcher.last_switch_time = t0

    tier = switcher.evaluate_tier(85.0, current_time=t0 + 0.5)
    assert tier == "FULL", "Must NOT switch before dwell time expires"

    tier = switcher.evaluate_tier(85.0, current_time=t0 + 1.2)
    assert tier == "MINIMAL", "Must transition to MINIMAL after dwell time expires"


def test_transition_to_reduced_tier():
    """Moderate CPU load (45% <= CPU < 75%) transitions to REDUCED tier."""
    switcher = DynamicTierSwitcher(
        high_load_thresh=75.0,
        medium_load_thresh=45.0,
        hysteresis=5.0,
        dwell_time_seconds=1.0
    )
    t0 = 1000.0
    switcher.last_switch_time = t0 - 2.0

    tier = switcher.evaluate_tier(55.0, current_time=t0)
    assert tier == "REDUCED"
    assert switcher.TIERS[tier] == "CompactMLP"


def test_hysteresis_deadband_downward():
    """
    Downward transition must satisfy deadband hysteresis (ΔH = 5):
    - Moving MINIMAL -> REDUCED requires CPU < (75 - 5) = 70%
    - Moving REDUCED -> FULL requires CPU < (45 - 5) = 40%
    """
    switcher = DynamicTierSwitcher(
        high_load_thresh=75.0,
        medium_load_thresh=45.0,
        hysteresis=5.0,
        dwell_time_seconds=1.0
    )
    
    t = 1000.0
    switcher.last_switch_time = t - 2.0
    tier = switcher.evaluate_tier(85.0, current_time=t)
    assert tier == "MINIMAL"

    t += 2.0
    tier = switcher.evaluate_tier(72.0, current_time=t)
    assert tier == "MINIMAL", "Must stay in MINIMAL because 72% > (75 - 5)%"

    t += 2.0
    tier = switcher.evaluate_tier(68.0, current_time=t)
    assert tier == "REDUCED", "Must transition to REDUCED once below 70%"

    t += 2.0
    tier = switcher.evaluate_tier(43.0, current_time=t)
    assert tier == "REDUCED", "Must stay in REDUCED because 43% > (45 - 5)%"

    t += 2.0
    tier = switcher.evaluate_tier(38.0, current_time=t)
    assert tier == "FULL", "Must transition to FULL once below 40%"
