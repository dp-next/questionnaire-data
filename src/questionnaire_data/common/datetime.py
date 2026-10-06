from datetime import UTC, datetime


def get_current() -> str:
    """Get current datetime as a string."""
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
