import re
import uuid
import datetime
from typing import Optional
from dateutil import parser


def _escape_text(text: Optional[str]) -> str:
    """Escapes special characters in text values per RFC 5545."""
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace(';', r'\;')
    text = text.replace(',', r'\,')
    text = text.replace('\r\n', r'\n').replace('\r', r'\n').replace('\n', r'\n')
    return text


def _fold_line(line: str) -> str:
    """Folds lines exceeding 75 octets according to RFC 5545."""
    if len(line.encode('utf-8')) <= 75:
        return line

    parts = []
    curr = ""
    curr_bytes = 0
    max_bytes = 75

    for ch in line:
        ch_bytes = len(ch.encode('utf-8'))
        if curr_bytes + ch_bytes > max_bytes and curr:
            parts.append(curr)
            curr = " " + ch
            curr_bytes = 1 + ch_bytes
        else:
            curr += ch
            curr_bytes += ch_bytes

    if curr:
        parts.append(curr)

    return "\r\n".join(parts)


def generate_ics(
    title: str,
    date_str: Optional[str] = None,
    time_str: Optional[str] = None,
    location: Optional[str] = None,
    description: str = "",
    all_day: bool = False
) -> str:
    """
    Generate an iCalendar (.ics) string for a notice event.
    - Timezone: Asia/Kolkata
    - All-day and timed event support
    - Line folding and RFC 5545 compliance
    """
    # 1. Determine base date
    base_date = datetime.date(2026, 11, 22)
    if date_str:
        try:
            parsed = parser.parse(date_str, fuzzy=True, dayfirst=True)
            base_date = parsed.date()
        except Exception:
            pass

    # 2. Determine if timed or all-day
    is_timed = False
    start_dt = None
    end_dt = None

    if not all_day and time_str:
        # Check for range: e.g. "10:00 AM to 1:00 PM" or "10:00 - 13:00"
        parts = re.split(r'\s*(?:to|-|–)\s*', time_str, flags=re.IGNORECASE)
        try:
            if len(parts) >= 2:
                # Parse start time
                t1 = parser.parse(parts[0].strip(), fuzzy=True).time()
                start_dt = datetime.datetime.combine(base_date, t1)
                try:
                    t2 = parser.parse(parts[1].strip(), fuzzy=True).time()
                    end_dt = datetime.datetime.combine(base_date, t2)
                    if end_dt <= start_dt:
                        end_dt = start_dt + datetime.timedelta(hours=1)
                except Exception:
                    end_dt = start_dt + datetime.timedelta(hours=1)
                is_timed = True
            else:
                t1 = parser.parse(parts[0].strip(), fuzzy=True).time()
                start_dt = datetime.datetime.combine(base_date, t1)
                end_dt = start_dt + datetime.timedelta(hours=1)
                is_timed = True
        except Exception:
            is_timed = False

    # 3. Build iCalendar components
    dtstamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    event_uid = f"{uuid.uuid4()}@noticepilot"

    raw_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NoticePilot//College Notice Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Kolkata",
        "X-LIC-LOCATION:Asia/Kolkata",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0530",
        "TZOFFSETTO:+0530",
        "TZNAME:IST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VEVENT",
        f"UID:{event_uid}",
        f"DTSTAMP:{dtstamp}",
        f"SUMMARY:{_escape_text(title or 'College Notice Event')}",
    ]

    if location:
        raw_lines.append(f"LOCATION:{_escape_text(location)}")

    if description:
        raw_lines.append(f"DESCRIPTION:{_escape_text(description)}")

    if is_timed and start_dt and end_dt:
        start_str = start_dt.strftime("%Y%m%dT%H%M%S")
        end_str = end_dt.strftime("%Y%m%dT%H%M%S")
        raw_lines.append(f"DTSTART;TZID=Asia/Kolkata:{start_str}")
        raw_lines.append(f"DTEND;TZID=Asia/Kolkata:{end_str}")
    else:
        # All-day event (non-inclusive end date is start_date + 1 day)
        start_val = base_date.strftime("%Y%m%d")
        end_val = (base_date + datetime.timedelta(days=1)).strftime("%Y%m%d")
        raw_lines.append(f"DTSTART;VALUE=DATE:{start_val}")
        raw_lines.append(f"DTEND;VALUE=DATE:{end_val}")

    raw_lines.append("STATUS:CONFIRMED")
    raw_lines.append("END:VEVENT")
    raw_lines.append("END:VCALENDAR")

    # 4. Fold lines and join with CRLF
    folded_lines = [_fold_line(line) for line in raw_lines]
    return "\r\n".join(folded_lines) + "\r\n"
