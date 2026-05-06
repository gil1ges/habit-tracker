import re


LOGIN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,18}[A-Za-z0-9]$")
DATE_RE = re.compile(r"\b\d{1,2}([./-])\d{1,2}\1\d{2}(?:\d{2})?\b")
LOG_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>[A-Z]+) "
    r"user=(?P<user>\S+) "
    r"action=(?P<action>\S+) "
    r"ip=(?P<ip>(?:\d{1,3}\.){3}\d{1,3})$"
)
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
)
PASSWORD_SPECIAL_RE = re.compile(r"[!@#$%^&*]")


def validate_login(login: str) -> bool:
    return bool(LOGIN_RE.fullmatch(login))


def find_dates(text: str) -> list[str]:
    return [match.group(0) for match in DATE_RE.finditer(text)]


def parse_log(log: str) -> dict:
    match = LOG_RE.fullmatch(log.strip())
    if match is None:
        raise ValueError("Unsupported log format.")
    return match.groupdict()


def validate_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and bool(PASSWORD_SPECIAL_RE.search(password))
    )


def validate_email_domain(email: str, domains: list[str]) -> bool:
    if not EMAIL_RE.fullmatch(email):
        return False

    allowed_domains = {domain.lower() for domain in domains}
    email_domain = email.rsplit("@", maxsplit=1)[-1].lower()
    return email_domain in allowed_domains


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) != 11 or digits[0] not in {"7", "8"}:
        raise ValueError("Unsupported phone format.")
    return f"+7{digits[1:]}"
