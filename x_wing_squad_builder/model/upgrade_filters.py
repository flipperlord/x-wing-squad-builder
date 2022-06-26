from collections import Counter

from typing import List


def upgrade_slot_filter(upgrade_slots: List[str], pilot_slots: List[str]) -> bool:
    """Returns True if the pilot has enough slots available, false otherwise"""
    upgrade_counts = Counter(upgrade_slots)
    pilot_counts = Counter(pilot_slots)
    for slot in upgrade_slots:
        if upgrade_counts[slot] > pilot_counts[slot]:
            return False
    return True


def name_filter(value: list, test_case: str) -> bool:
    """Returns True if the test case falls in the value.  If the value is an empty list, we assume no restriction."""
    if value:
        if test_case not in value:
            return False
    return True


def multiple_name_filter(value: list, test_cases):
    if value:
        return any([name_filter(value, test_case) for test_case in test_cases])
    return True
