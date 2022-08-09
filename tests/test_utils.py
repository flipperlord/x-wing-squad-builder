import pytest

from x_wing_squad_builder.utils import (contains_number, process_part, prettify_name,
                                        gui_text_encode, gui_text_decode,
                                        get_pilot_name_from_list_item_text, get_upgrade_name_from_list_item_text, get_upgrade_slot_from_list_item_text)


def test_contains_number():
    test_case_1 = "hey6wh0p"
    assert contains_number(test_case_1) is True

    test_case_1 = "yoyoyoyo"
    assert contains_number(test_case_1) is False

    test_case_1 = "%&!@#"
    assert contains_number(test_case_1) is False


def test_gui_text_decode():
    test_case = "^hey%yo^"
    assert gui_text_decode(test_case) == "\"hey/yo\""

    test_case = "hey yo!"
    assert gui_text_decode(test_case) == test_case


def test_gui_text_encode():
    test_case = "\"hey/yo\""
    assert gui_text_encode(test_case) == "^hey%yo^"

    test_case = "hey yo!"
    assert gui_text_encode(test_case) == test_case


def test_process_part():
    test_case = "tn-3465yaboi"
    assert process_part(test_case, '-') == 'TN-3465YABOI'

    test_case = "weare!the-people"
    assert process_part(test_case, "!") == 'Weare!The-people'
    assert process_part(test_case, "-") == 'Weare!the-People'

    test_case = "weare-the-people"
    assert process_part(test_case, "-") == 'Weare-THE-People'
    assert process_part(test_case, "?") == 'Weare-the-people'

    test_case = "bo-katan"
    assert process_part(test_case, "-") == "Bo-Katan"


def test_prettify_name():
    test_case = "this be tn-3645 ^null^"
    assert prettify_name(test_case) == "This Be TN-3645 \"Null\""


@pytest.mark.parametrize(
    "list_item_text, expected", [
        pytest.param("Collision Detector (6)", "collision detector"),
    ]
)
def test_get_upgrade_name_from_list_item_text(list_item_text, expected):
    extracted_name = get_upgrade_name_from_list_item_text(list_item_text)
    assert extracted_name == expected
