import re
import uuid
import datetime
from typing import List, Optional, Tuple
from dateutil import parser
from app.models import ExtractedInfo, EvidenceSnippet, TaskItem

# Common headers to ignore when identifying notice titles
IGNORE_TITLE_PATTERNS = [
    r'^(?:circular|notice|announcement|invitation|memorandum|memo|office\s+order)$',
    r'^(?:college|university|institute|department|school|faculty)\s+of\b',
    r'^(?:ref\s*(?:no|num)?|date|to|from)\s*[:\-]',
    r'^(?:urgent|important\s+notice|attention|all\s+students|to\s+all\s+students)\b',
]

def _is_ignorable_title_line(line: str) -> bool:
    clean = line.strip().lower()
    if not clean or len(clean) < 3:
        return True
    for pat in IGNORE_TITLE_PATTERNS:
        if re.search(pat, clean):
            return True
    return False

def extract_title(text: str) -> Tuple[Optional[str], Optional[EvidenceSnippet]]:
    """
    Extract title looking for Subject:, Re:, quoted titles, or first meaningful line.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None, None

    # 1. Look for Subject: / Sub: / Re:
    for line in lines:
        match = re.search(r'^(?:subject|sub|re)\s*[:\-]\s*(.+)$', line, re.IGNORECASE)
        if match:
            title = match.group(1).strip().strip('"\'')
            if title:
                return title, EvidenceSnippet(field="title", snippet=line, confidence=0.95)

    # 2. Look for quoted title in the first 5 lines
    for line in lines[:5]:
        quoted_match = re.search(r'["\']([^"\']{4,80})["\']', line)
        if quoted_match:
            title = quoted_match.group(1).strip()
            if not _is_ignorable_title_line(title):
                return title, EvidenceSnippet(field="title", snippet=line, confidence=0.85)

    # 3. Look for first meaningful line
    for line in lines:
        if not _is_ignorable_title_line(line):
            # Check length to ensure it's a heading rather than a paragraph
            if len(line) <= 100:
                clean_title = re.sub(r'^(?:subject|sub|re)\s*[:\-]\s*', '', line, flags=re.IGNORECASE).strip().strip('"\'')
                return clean_title, EvidenceSnippet(field="title", snippet=line, confidence=0.70)

    # Fallback to first line if nothing else found
    fallback = lines[0][:80].strip()
    return fallback, EvidenceSnippet(field="title", snippet=lines[0], confidence=0.50)


def _check_numeric_date_ambiguity(date_str: str) -> bool:
    """
    Checks if a numeric date string (e.g. 01/02/2026 or 05-06-2026) is ambiguous between DD/MM and MM/DD.
    """
    m = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', date_str)
    if m:
        d1, d2 = int(m.group(1)), int(m.group(2))
        if 1 <= d1 <= 12 and 1 <= d2 <= 12 and d1 != d2:
            return True
    return False


def _parse_to_iso_date(date_str: str, default_year: Optional[int] = None) -> Optional[str]:
    """
    Parses a raw date string to YYYY-MM-DD using dateutil.
    Dynamically defaults to current year if year is omitted.
    """
    try:
        # Default dayfirst=True for Indian / UK college notices
        year = default_year if default_year is not None else datetime.date.today().year
        default_dt = datetime.datetime(year, 1, 1)
        parsed = parser.parse(date_str, dayfirst=True, default=default_dt, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except (parser.ParserError, ValueError, OverflowError, TypeError):
        return None


def extract_dates(text: str) -> Tuple[Optional[str], Optional[EvidenceSnippet], Optional[str], Optional[EvidenceSnippet], List[str]]:
    """
    Extract event date and registration deadline with evidence and uncertainty tracking.
    """
    uncertain_fields = []
    event_date = None
    event_date_evidence = None
    reg_deadline = None
    reg_deadline_evidence = None

    reg_deadline_keywords = [
        r'register\s+by',
        r'registration\s+deadline',
        r'last\s+date\s+(?:to\s+register|for\s+registration|of\s+registration|of\s+submission|to\s+submit|to\s+apply|for\s+submission)',
        r'deadline\s+for\s+registration',
        r'registration\s+closes',
        r'deadline\s*:\s*',
        r'last\s+date\s*:\s*',
        r'apply\s+by',
        r'submit\s+by',
        r'submission\s+deadline',
    ]
    reg_pattern = re.compile(r'(' + '|'.join(reg_deadline_keywords) + r')', re.IGNORECASE)

    event_specific_keywords = [
        r'date\s+of\s+(?:the\s+)?(?:lecture|event|workshop|webinar|seminar|session|exam|examination|contest|hackathon|presentation|commencement|conference)',
        r'event\s+date',
        r'examination\s+period',
        r'date\s+of\s+commencement',
        r'held\s+on',
        r'scheduled\s+on',
        r'takes?\s+place\s+on',
        r'conducted\s+on',
        r'organized\s+on',
        r'commencing\s+on',
    ]
    event_specific_pattern = re.compile(r'(' + '|'.join(event_specific_keywords) + r')', re.IGNORECASE)

    event_date_keywords = event_specific_keywords + [
        r'date\s*:\s*',
        r'dated\s*:\s*',
    ]
    event_pattern = re.compile(r'(' + '|'.join(event_date_keywords) + r')', re.IGNORECASE)

    # Date match regexes
    # 1. Numeric: 25/11/2026 or 25-11-2026
    # 2. Words: 25th November 2026, 25 Nov 2026, Nov 25, 2026, November 25 2026
    raw_date_pattern = re.compile(
        r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]*[\s,]+(?:\d{4}|\d{2})\b|'
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?[\s,]+(?:\d{4}|\d{2})\b|'
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b)',
        re.IGNORECASE
    )

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # First pass: Look for registration deadline
    for line in lines:
        if reg_pattern.search(line):
            date_match = raw_date_pattern.search(line)
            if date_match:
                raw_d = date_match.group(1)
                iso_d = _parse_to_iso_date(raw_d)
                if iso_d and not reg_deadline:
                    reg_deadline = iso_d
                    is_ambiguous = _check_numeric_date_ambiguity(raw_d)
                    conf = 0.65 if is_ambiguous else 0.95
                    reg_deadline_evidence = EvidenceSnippet(
                        field="registration_deadline",
                        snippet=line,
                        confidence=conf
                    )
                    if is_ambiguous:
                        uncertain_fields.append("registration_deadline")
                    break

    # Second pass: Look for event date with SPECIFIC event keywords (e.g. date of lecture, held on)
    for line in lines:
        if reg_deadline_evidence and line == reg_deadline_evidence.snippet:
            continue
        if event_specific_pattern.search(line):
            date_match = raw_date_pattern.search(line)
            if date_match:
                raw_d = date_match.group(1)
                iso_d = _parse_to_iso_date(raw_d)
                if iso_d and not event_date:
                    event_date = iso_d
                    is_ambiguous = _check_numeric_date_ambiguity(raw_d)
                    conf = 0.65 if is_ambiguous else 0.95
                    event_date_evidence = EvidenceSnippet(
                        field="date",
                        snippet=line,
                        confidence=conf
                    )
                    if is_ambiguous:
                        uncertain_fields.append("date")
                    break

    # Third pass: Look for event date with general keywords (e.g. Date: 15th Dec)
    if not event_date:
        for idx, line in enumerate(lines):
            if reg_deadline_evidence and line == reg_deadline_evidence.snippet:
                continue
            if event_pattern.search(line):
                date_match = raw_date_pattern.search(line)
                if date_match:
                    raw_d = date_match.group(1)
                    iso_d = _parse_to_iso_date(raw_d)
                    if iso_d:
                        # If this is on header lines (idx <= 2) and there is another date below, check if there's a better one
                        has_later_date = any(raw_date_pattern.search(l) for l in lines[idx+1:] if not (reg_deadline_evidence and l == reg_deadline_evidence.snippet))
                        if idx <= 2 and has_later_date:
                            continue
                        event_date = iso_d
                        is_ambiguous = _check_numeric_date_ambiguity(raw_d)
                        conf = 0.65 if is_ambiguous else 0.95
                        event_date_evidence = EvidenceSnippet(
                            field="date",
                            snippet=line,
                            confidence=conf
                        )
                        if is_ambiguous:
                            uncertain_fields.append("date")
                        break

    # Fourth pass: Any remaining date in the text
    if not event_date:
        for line in lines:
            if reg_deadline_evidence and line == reg_deadline_evidence.snippet:
                continue
            date_match = raw_date_pattern.search(line)
            if date_match:
                raw_d = date_match.group(1)
                iso_d = _parse_to_iso_date(raw_d)
                if iso_d and iso_d != reg_deadline:
                    event_date = iso_d
                    is_ambiguous = _check_numeric_date_ambiguity(raw_d)
                    conf = 0.60 if is_ambiguous else 0.80
                    event_date_evidence = EvidenceSnippet(
                        field="date",
                        snippet=line,
                        confidence=conf
                    )
                    if is_ambiguous:
                        uncertain_fields.append("date")
                    break

    return event_date, event_date_evidence, reg_deadline, reg_deadline_evidence, uncertain_fields


def extract_time(text: str) -> Tuple[Optional[str], Optional[EvidenceSnippet]]:
    """
    Extract time (e.g. 10:00 AM, 10:00 AM to 1:00 PM, 2:30 PM, 14:00).
    """
    time_range_pat = re.compile(
        r'\b((?:[01]?\d|2[0-3]):[0-5]\d\s*(?:AM|PM|am|pm)?\s*(?:to|-|–)\s*(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:AM|PM|am|pm)?)\b',
        re.IGNORECASE
    )
    time_range_words_pat = re.compile(
        r'\b((?:[01]?\d|2[0-3])\s*(?:AM|PM|am|pm)\s*(?:to|-|–)\s*(?:[01]?\d|2[0-3])\s*(?:AM|PM|am|pm))\b',
        re.IGNORECASE
    )
    single_time_pat = re.compile(
        r'\b((?:[01]?\d|2[0-3]):[0-5]\d\s*(?:AM|PM|am|pm))\b',
        re.IGNORECASE
    )
    single_hour_pat = re.compile(
        r'\b((?:1[0-2]|[1-9])\s*(?:AM|PM|am|pm))\b',
        re.IGNORECASE
    )
    mil_time_pat = re.compile(
        r'\b((?:[01]\d|2[0-3]):[0-5]\d)\s*(?:hrs|hours|IST)?\b',
        re.IGNORECASE
    )

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # First check lines with Time: / Timing:
    for line in lines:
        if re.search(r'(?:time|timing|timings)\s*[:\-]', line, re.IGNORECASE):
            for pat in [time_range_pat, time_range_words_pat, single_time_pat, single_hour_pat, mil_time_pat]:
                m = pat.search(line)
                if m:
                    return m.group(1).strip(), EvidenceSnippet(field="time", snippet=line, confidence=0.95)
            # If line has "Time: 10:00 onwards" or similar
            time_after = re.search(r'(?:time|timing|timings)\s*[:\-]\s*([^\n,;]+)', line, re.IGNORECASE)
            if time_after:
                cleaned = time_after.group(1).strip()
                if any(char.isdigit() for char in cleaned):
                    return cleaned, EvidenceSnippet(field="time", snippet=line, confidence=0.85)

    # Check for general time patterns in lines
    for line in lines:
        for pat in [time_range_pat, time_range_words_pat, single_time_pat, single_hour_pat]:
            m = pat.search(line)
            if m:
                # Exclude lines that are purely dates
                val = m.group(1).strip()
                return val, EvidenceSnippet(field="time", snippet=line, confidence=0.80)

    return None, None


def extract_location(text: str) -> Tuple[Optional[str], Optional[EvidenceSnippet]]:
    """
    Extract venue / location. Looks for Venue:, Location:, Place:, or 'in/at [room/hall]'.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # 1. Explicit Venue / Location / Place / Platform / Mode label
    explicit_pat = re.compile(r'^(?:venue|location|place|platform|mode)\s*[:\-]\s*(.+)$', re.IGNORECASE)
    for line in lines:
        m = explicit_pat.search(line)
        if m:
            loc = m.group(1).strip().strip('.')
            if loc and len(loc) >= 3:
                return loc, EvidenceSnippet(field="location", snippet=line, confidence=0.95)

    # 2. In-line Venue: pattern
    inline_pat = re.compile(r'(?:venue|location|place|platform|mode)\s*[:\-]\s*([^\n\r,;]+)', re.IGNORECASE)
    for line in lines:
        m = inline_pat.search(line)
        if m:
            loc = m.group(1).strip().strip('.')
            if loc and len(loc) >= 3:
                return loc, EvidenceSnippet(field="location", snippet=line, confidence=0.90)

    # 3. Contextual patterns: at [Venue] or in [Room/Hall/Audi] or online platform
    room_pat = re.compile(
        r'\b(?:at|in|via|on)\s+(?:the\s+)?((?:[A-Z][A-Za-z0-9\s]{0,35}\s+)?(?:Auditorium|Audi|Seminar\s+Hall|Conference\s+Hall|Hall(?:\s+[-–]?[A-Z0-9]+)?|Room(?:\s+[-–]?[A-Z0-9]+)?|Lab(?:\s+[-–]?[A-Z0-9]+)?|Grounds?|Campus|Building|Centre|Center|Library|Google\s+Meet|Zoom|MS\s+Teams|Microsoft\s+Teams|Webex))\b'
    )
    for line in lines:
        m = room_pat.search(line)
        if m:
            loc = m.group(1).strip().strip('.')
            # Avoid generic matches
            if loc.lower() not in ['college', 'university', 'campus', 'advance', 'the earliest', 'time']:
                return loc, EvidenceSnippet(field="location", snippet=line, confidence=0.75)

    return None, None


def extract_requirements(text: str) -> Tuple[List[str], List[EvidenceSnippet]]:
    """
    Extract requirements (e.g. Bring ID card, Laptop mandatory, prerequisites).
    """
    req_keywords = [
        r'\bbring\b',
        r'\brequired\b',
        r'\bmust\b',
        r'\bmandatory\b',
        r'\bcarry\b',
        r'\bstudents\s+are\s+required\b',
        r'\bprerequisites?\b',
        r'\beligibility\b',
        r'\bparticipants\s+must\b',
    ]
    pattern = re.compile(r'(' + '|'.join(req_keywords) + r')', re.IGNORECASE)

    requirements = []
    evidence = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    in_req_section = False
    for line in lines:
        # Check section header
        if re.search(r'^(?:requirements?|prerequisites?|instructions?|rules?|students\s+are\s+required\s+to)\s*[:\-]?$', line, re.IGNORECASE) or re.search(r'required\s+to\s*:', line, re.IGNORECASE):
            in_req_section = True
            continue

        if in_req_section:
            if re.search(r'^(?:contact|venue|date|time|schedule|about|email|phone)\s*[:\-]', line, re.IGNORECASE):
                in_req_section = False
            elif line.startswith(('-', '*', '•')) or re.match(r'^\d+[\.\)]', line):
                clean_item = re.sub(r'^(?:[-*•]|\d+[\.\)])\s*', '', line).strip()
                clean_item = re.sub(r'^[.\-\s]+', '', clean_item).strip()
                if clean_item and len(clean_item) > 3:
                    requirements.append(clean_item)
                    evidence.append(EvidenceSnippet(field="requirements", snippet=line, confidence=0.90))
                    continue
            elif line.endswith(':'):
                in_req_section = False

        if not in_req_section and pattern.search(line):
            if line.strip().endswith(':'):
                in_req_section = True
                continue
            clean_item = re.sub(r'^(?:[-*•]|\d+[\.\)])\s*', '', line).strip()
            clean_item = re.sub(r'^[.\-\s]+', '', clean_item).strip()
            # Exclude lines that are purely contacts or headings
            if len(clean_item) > 5 and not re.search(r'^(?:contact|venue|date|time|email|phone)\s*[:\-]', clean_item, re.IGNORECASE):
                if clean_item not in requirements:
                    requirements.append(clean_item)
                    evidence.append(EvidenceSnippet(field="requirements", snippet=line, confidence=0.85))

    return requirements, evidence


def extract_contacts(text: str) -> Tuple[List[str], List[EvidenceSnippet]]:
    """
    Extract contact info: email addresses, phone numbers, contact lines.
    """
    contacts = []
    evidence = []

    # 1. Email addresses
    email_pat = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    for m in email_pat.finditer(text):
        email = m.group(0).strip()
        if email not in contacts:
            contacts.append(email)
            evidence.append(EvidenceSnippet(field="contact_info", snippet=email, confidence=0.95))

    # 2. Phone numbers (Indian mobile numbers, landlines with std codes)
    phone_pat = re.compile(r'(?:\+91[\s-]?)?[6789]\d{9}\b|\b\d{3,5}[-\s]\d{6,8}\b')
    for m in phone_pat.finditer(text):
        phone = m.group(0).strip()
        if phone not in contacts:
            contacts.append(phone)
            evidence.append(EvidenceSnippet(field="contact_info", snippet=phone, confidence=0.90))

    # 3. Explicit Contact / Queries / Coordinator lines
    contact_line_pat = re.compile(r'^(?:contact|queries|coordinator|coordinators|inquiries|convenor|convener)\s*[:\-]\s*(.+)$', re.IGNORECASE)
    for line in text.splitlines():
        line_s = line.strip()
        m = contact_line_pat.search(line_s)
        if m:
            detail = m.group(1).strip()
            if detail and detail not in contacts:
                contacts.append(detail)
                evidence.append(EvidenceSnippet(field="contact_info", snippet=line_s, confidence=0.90))

    return contacts, evidence


def extract_action_items(text: str) -> Tuple[List[str], List[EvidenceSnippet]]:
    """
    Extract imperative action items (Register at, Submit, Attend, Download, Pay, etc.).
    """
    action_verbs = [
        'register', 'submit', 'attend', 'download', 'pay', 'upload',
        'fill', 'join', 'apply', 'collect', 'carry', 'bring',
        'report', 'send', 'verify', 'complete', 'confirm',
        'clear', 'check', 'enroll', 'contact', 'meet'
    ]
    verb_regex = r'\b(?:' + '|'.join(action_verbs) + r')\b'

    action_items = []
    evidence = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        # Check if line starts with bullet or number
        m_bullet = re.match(r'^(?:[-*•]|\d+[\.\)])\s*(.+)$', line)
        candidate = m_bullet.group(1).strip() if m_bullet else line
        candidate = re.sub(r'^[.\-\s]+', '', candidate).strip()

        # Exclude headers, contact, or location lines
        if re.search(r'^(?:venue|location|date|time|contact|subject|ref)\s*[:\-]', candidate, re.IGNORECASE):
            continue

        words = candidate.split()
        if not words:
            continue

        first_word = words[0].lower().strip('.,:;()[]')
        # Check if first word is an action verb or second word if first is adverb/helper
        is_action = first_word in action_verbs
        if not is_action and len(words) > 1 and words[1].lower().strip('.,:;()[]') in action_verbs:
            is_action = True

        # Also check imperative phrases like "Please submit...", "Students must register...", "Last date to pay..."
        if not is_action:
            if re.search(r'\b(?:please|kindly|must|should|advised\s+to|requested\s+to|required\s+to|last\s+date\s+to|deadline\s+to)\s+(?:' + '|'.join(action_verbs) + r')\b', candidate, re.IGNORECASE):
                is_action = True

        if is_action and len(candidate) > 8:
            if candidate not in action_items:
                action_items.append(candidate)
                evidence.append(EvidenceSnippet(field="action_items", snippet=line, confidence=0.85))

    return action_items, evidence


def extract_from_notice(text: str) -> ExtractedInfo:
    """
    Main extraction function for parsing college notices deterministically using regex.
    """
    if not text or not text.strip():
        return ExtractedInfo()

    # Normalize literal \n or \r if payload string was passed with escaped backslashes
    if '\\n' in text and '\n' not in text:
        text = text.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\r', '\n')

    evidence_list: List[EvidenceSnippet] = []
    uncertain_fields_set = set()

    # Title
    title, title_evidence = extract_title(text)
    if title_evidence:
        evidence_list.append(title_evidence)
        if title_evidence.confidence < 0.70:
            uncertain_fields_set.add("title")

    # Dates
    event_date, date_ev, reg_deadline, reg_ev, date_uncertain = extract_dates(text)
    if date_ev:
        evidence_list.append(date_ev)
    if reg_ev:
        evidence_list.append(reg_ev)
    for f in date_uncertain:
        uncertain_fields_set.add(f)

    # Time
    time_str, time_ev = extract_time(text)
    if time_ev:
        evidence_list.append(time_ev)
        if time_ev.confidence < 0.70:
            uncertain_fields_set.add("time")

    # Location
    location_str, loc_ev = extract_location(text)
    if loc_ev:
        evidence_list.append(loc_ev)
        if loc_ev.confidence < 0.70:
            uncertain_fields_set.add("location")

    # Requirements
    requirements, req_evs = extract_requirements(text)
    evidence_list.extend(req_evs)

    # Contact Info
    contacts, contact_evs = extract_contacts(text)
    evidence_list.extend(contact_evs)

    # Action Items
    action_items, action_evs = extract_action_items(text)
    evidence_list.extend(action_evs)

    return ExtractedInfo(
        title=title,
        date=event_date,
        time=time_str,
        location=location_str,
        registration_deadline=reg_deadline,
        requirements=requirements,
        contact_info=contacts,
        action_items=action_items,
        evidence=evidence_list,
        uncertain_fields=list(uncertain_fields_set)
    )


def _calculate_priority(deadline_str: Optional[str], default_priority: str = "medium") -> str:
    """
    Calculate priority dynamically relative to today:
    - overdue or within 3 days = high
    - within 7 days = medium
    - else low
    """
    if not deadline_str:
        return default_priority
    try:
        parsed_dt = parser.parse(deadline_str, fuzzy=True, dayfirst=True)
        today = datetime.date.today()
        diff_days = (parsed_dt.date() - today).days
        if diff_days <= 3:
            return "high"
        elif diff_days <= 7:
            return "medium"
        else:
            return "low"
    except (parser.ParserError, ValueError, OverflowError, TypeError):
        return default_priority


def generate_tasks(extracted_info: ExtractedInfo) -> List[TaskItem]:
    """
    Generate actionable tasks from extracted notice info.
    - If registration deadline, high-priority 'Register for [event]'
    - If event date, medium-priority 'Attend [event]'
    - Action item tasks with priority based on dynamic deadline proximity
    """
    tasks: List[TaskItem] = []
    event_title = extracted_info.title or "Event"

    # 1. Registration deadline task
    if extracted_info.registration_deadline:
        reg_prio = _calculate_priority(extracted_info.registration_deadline, default_priority="high")
        priority = reg_prio
        tasks.append(
            TaskItem(
                id=str(uuid.uuid4()),
                name=f"Register for {event_title}",
                deadline=extracted_info.registration_deadline,
                priority=priority,
                completed=False,
                description=f"Complete registration for {event_title} before {extracted_info.registration_deadline}"
            )
        )

    # 2. Attend event task
    if extracted_info.date:
        attend_prio = _calculate_priority(extracted_info.date, default_priority="medium")
        desc = f"Attend {event_title} on {extracted_info.date}"
        if extracted_info.time:
            desc += f" at {extracted_info.time}"
        if extracted_info.location:
            desc += f" in {extracted_info.location}"
        tasks.append(
            TaskItem(
                id=str(uuid.uuid4()),
                name=f"Attend {event_title}",
                deadline=extracted_info.date,
                priority=attend_prio,
                completed=False,
                description=desc
            )
        )

    # 3. Action items tasks
    for item in extracted_info.action_items:
        item_lower = item.lower()

        # Avoid redundant duplicate tasks
        if "register" in item_lower and extracted_info.registration_deadline and any("Register for" in t.name for t in tasks):
            continue
        if "attend" in item_lower and extracted_info.date and any("Attend " in t.name for t in tasks):
            continue

        item_deadline = None
        # Check if action item relates to registration deadline or event date
        if any(kw in item_lower for kw in ["submit", "pay", "fee", "upload", "fill", "apply"]):
            item_deadline = extracted_info.registration_deadline or extracted_info.date
        elif any(kw in item_lower for kw in ["bring", "carry", "collect", "verify", "report"]):
            item_deadline = extracted_info.date or extracted_info.registration_deadline

        item_priority = _calculate_priority(item_deadline, default_priority="medium")

        tasks.append(
            TaskItem(
                id=str(uuid.uuid4()),
                name=item[:80],
                deadline=item_deadline,
                priority=item_priority,
                completed=False,
                description=item
            )
        )

    return tasks


def generate_summary(extracted_info: ExtractedInfo) -> str:
    """
    Generate a clean text summary listing event name, date, time, location, and key action items.
    """
    lines = []
    lines.append("Notice Summary:")
    lines.append(f"- Event: {extracted_info.title or 'Not specified'}")
    lines.append(f"- Date: {extracted_info.date or 'Not specified'}")
    if extracted_info.time:
        lines.append(f"- Time: {extracted_info.time}")
    if extracted_info.location:
        lines.append(f"- Location: {extracted_info.location}")
    if extracted_info.registration_deadline:
        lines.append(f"- Registration Deadline: {extracted_info.registration_deadline}")

    if extracted_info.action_items:
        lines.append("\nKey Action Items:")
        for action in extracted_info.action_items:
            lines.append(f"- {action}")

    if extracted_info.requirements:
        lines.append("\nRequirements:")
        for req in extracted_info.requirements:
            lines.append(f"- {req}")

    if extracted_info.contact_info:
        lines.append("\nContact Info:")
        for contact in extracted_info.contact_info:
            lines.append(f"- {contact}")

    return "\n".join(lines)

