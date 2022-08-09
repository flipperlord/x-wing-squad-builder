from collections import Counter

from typing import List


def bool_string_filter(test_case: str) -> bool:
    """returns false if False string, otherwise True"""
    if test_case == "False":
        return False
    return True


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


def actions_filter(restricted_actions: list, pilot_actions):
    """
    returns true if a pilot action is equal to one of the restricted actions,
    if the restricted_actions list is empty, we assume no restriction.
    """
    if restricted_actions:
        for action in pilot_actions:
            for r_action in restricted_actions:
                if action == r_action:
                    return True
        return False
    return True


def statistics_filter_simple(restricted_statistic: dict, test_statistic: dict):
    """
    this is for simple statistics such as attacks, agility, and hull

    restricted_statistic is of the form:
    {
        'low': <low val>,
        'high': <high val>
    }

    test_statistic is of the form:
    {
        '<statistic name>': <statistic value>
    }
    """
    low = restricted_statistic.get('low')
    high = restricted_statistic.get('high')
    if low is None:
        low = 0
    if high is None:
        high = 100
    statistic_name = list(test_statistic.keys())[0]
    test_val = test_statistic[statistic_name]
    if test_val is None:
        test_val = 0
    if test_val in range(low, high):
        return True
    return False


def statistics_filter_adv(restricted_statistic: dict, test_statistic: dict):
    """
    this is for complex statistics such as shield, force, energy, and charge

    restricted_statistic is of the form:
    {
        '<statistic name>': {
            'low': <low val>,
            'high': <high val>
        },
        'charge': {
            'low': <low val>,
            'high': <high val>
        },
        'decharge': {
            'low': <low val>,
            'high': <high val>
        },
    }

    test_statistic is of the form:
    {
        '<statistic name>': <statistic value>,
        'recharge':  <recharge value>,
        'decharge': <decharge value>
    }
    """

    tests = []
    for k, v in restricted_statistic.items():
        test_val = test_statistic.get(k)
        valid = statistics_filter_simple(v, {k: test_val})
        tests.append(valid)
    return all(tests)


def limit_filter(restriction: dict, arr: List[str]):
    """
    Determines if a given upgrade has been equipped more than its limit

    restriction is of the form:
    {
        '<upgrade name>': <limit val>
    }

    arr is of the form:
    [<upgrade name>, <upgrade name>, <upgrade name>, ...]
    """

    name_counts = Counter(arr)
    restricted_name = list(restriction.keys())[0]
    restricted_val = list(restriction.values())[0]
    if restricted_val == 0:
        return True
    if name_counts[restricted_name] >= restricted_val:
        return False
    return True
