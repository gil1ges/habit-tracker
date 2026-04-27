import pytest

from utils.validators import (
    find_dates,
    normalize_phone,
    parse_log,
    validate_email_domain,
    validate_login,
    validate_password,
)


@pytest.mark.parametrize(
    ("login", "expected"),
    [
        ("Alice_1", True),
        ("user99", True),
        ("1alice", False),
        ("ab_cd", True),
        ("ab", False),
        ("user_", False),
        ("name-with-dash", False),
        ("averyveryverylongusername", False),
    ],
)
def test_validate_login(login, expected):
    assert validate_login(login) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Meeting dates: 1.2.24 and 10-12-2025.", ["1.2.24", "10-12-2025"]),
        ("Use 05/06/2024 or 7/8/24.", ["05/06/2024", "7/8/24"]),
        ("No dates here.", []),
    ],
)
def test_find_dates(text, expected):
    assert find_dates(text) == expected


@pytest.mark.parametrize(
    ("log_line", "expected"),
    [
        (
            "2024-02-10 14:23:01 INFO user=ada action=login ip=192.168.1.15",
            {
                "date": "2024-02-10",
                "time": "14:23:01",
                "level": "INFO",
                "user": "ada",
                "action": "login",
                "ip": "192.168.1.15",
            },
        ),
        (
            "2025-01-01 00:00:59 ERROR user=bob action=logout ip=10.0.0.7",
            {
                "date": "2025-01-01",
                "time": "00:00:59",
                "level": "ERROR",
                "user": "bob",
                "action": "logout",
                "ip": "10.0.0.7",
            },
        ),
    ],
)
def test_parse_log(log_line, expected):
    assert parse_log(log_line) == expected


@pytest.mark.parametrize("invalid_log", ["broken log", "2024-02-10 INFO user=ada"])
def test_parse_log_invalid(invalid_log):
    with pytest.raises(ValueError):
        parse_log(invalid_log)


@pytest.mark.parametrize(
    ("password", "expected"),
    [
        ("Strong1!", True),
        ("NoDigits!!", False),
        ("noupper1!", False),
        ("NOLOWER1!", False),
        ("Short1!", False),
        ("NoSpecial1", False),
    ],
)
def test_validate_password(password, expected):
    assert validate_password(password) is expected


@pytest.mark.parametrize(
    ("email", "domains", "expected"),
    [
        ("ada@example.com", ["example.com", "mail.com"], True),
        ("Ada@Example.com", ["example.com"], True),
        ("ada@example.org", ["example.com"], False),
        ("invalid-email", ["example.com"], False),
    ],
)
def test_validate_email_domain(email, domains, expected):
    assert validate_email_domain(email, domains) is expected


@pytest.mark.parametrize(
    ("phone", "expected"),
    [
        ("89991234567", "+79991234567"),
        ("8(999)123-45-67", "+79991234567"),
        ("+7 999 123 45 67", "+79991234567"),
    ],
)
def test_normalize_phone(phone, expected):
    assert normalize_phone(phone) == expected


@pytest.mark.parametrize("phone", ["12345", "+1 999 123 45 67"])
def test_normalize_phone_invalid(phone):
    with pytest.raises(ValueError):
        normalize_phone(phone)
