import dateutil


def format_datetime_natural(iso_str: str) -> str:
    """
    Converts ISO 8601 datetime string into a natural format like:
    "October 26, 2025 at 3:30 PM"
    """
    try:
        dt = dateutil.parser.isoparse(iso_str)
        return dt.strftime("%B %-d, %Y at %-I:%M %p")
    except Exception:
        return iso_str