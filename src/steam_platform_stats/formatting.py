from datetime import UTC, datetime


def format_minutes(minutes: int, *, for_table: bool = False) -> str:
    if for_table:
        return f"{minutes / 60:7.1f}h"
    return f"{minutes / 60:.1f}h"


def format_time_ago(timestamp: int) -> str:
    now = datetime.now(UTC)
    last_played = datetime.fromtimestamp(timestamp, tz=UTC)
    diff = now - last_played

    if diff.days == 0:
        if diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    if diff.days == 1:
        return "yesterday"
    if diff.days < 7:
        return f"{diff.days} days ago"
    if diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    if diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    years = diff.days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"
