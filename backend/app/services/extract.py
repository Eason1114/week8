import re
from dataclasses import dataclass

# Optional leading bullet: "-", "*", "•", or a numbered list marker like "1." / "2)".
_BULLET_PREFIX = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")
# Markdown task list checkbox, e.g. "[ ] Buy milk" or "[x] Buy milk".
_CHECKBOX = re.compile(r"^\[([ xX])\]\s*(.*)$")
# Known action keywords, with or without a trailing colon.
_KEYWORD_PREFIX = re.compile(r"^(todo|action|fixme|follow[- ]?up)\b:?\s*", re.IGNORECASE)
_TRAILING_BANGS = re.compile(r"(!+)\s*$")


@dataclass(frozen=True)
class ActionItem:
    text: str
    keyword: str | None
    urgent: bool
    already_completed: bool


def _parse_line(raw_line: str) -> ActionItem | None:
    line = raw_line.strip()
    if not line:
        return None

    line = _BULLET_PREFIX.sub("", line, count=1)

    checkbox_match = _CHECKBOX.match(line)
    is_checkbox = checkbox_match is not None
    already_completed = False
    if checkbox_match:
        already_completed = checkbox_match.group(1).lower() == "x"
        line = checkbox_match.group(2).strip()
        if not line:
            return None

    keyword_match = _KEYWORD_PREFIX.match(line)
    keyword = keyword_match.group(1).lower().replace(" ", "-") if keyword_match else None

    urgent = bool(_TRAILING_BANGS.search(line))

    is_actionable = keyword is not None or urgent or is_checkbox
    if not is_actionable:
        return None

    return ActionItem(text=line, keyword=keyword, urgent=urgent, already_completed=already_completed)


def extract_action_items_detailed(text: str) -> list[ActionItem]:
    """Parse `text` line-by-line into structured, deduplicated action items.

    Recognizes: TODO:/ACTION:/FIXME:/FOLLOW-UP: keyword prefixes (case
    insensitive, colon optional), markdown checkboxes (`- [ ]` / `- [x]`),
    and lines ending in `!` as an urgency signal. Already-checked-off
    checkbox items are parsed (so callers can inspect them) but are not
    themselves open action items unless they also carry a keyword/urgency.
    """
    seen: set[str] = set()
    results: list[ActionItem] = []
    for raw_line in text.splitlines():
        item = _parse_line(raw_line)
        if item is None or item.already_completed:
            continue
        if item.text in seen:
            continue
        seen.add(item.text)
        results.append(item)
    return results


def extract_action_items(text: str) -> list[str]:
    return [item.text for item in extract_action_items_detailed(text)]
