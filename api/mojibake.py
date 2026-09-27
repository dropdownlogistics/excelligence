"""Repair mojibake: UTF-8 text that was decoded as Windows-1252 somewhere upstream.

The registry workbook holds text that was pasted in already garbled, e.g. an em dash "—" stored
as "â€”", or "→" stored as "â†’". The exporter wrote that faithfully, so the JSON carried it too
(186 fields in 90 entries, found 2026-09-27). This module fixes it three ways:

    python api/mojibake.py --fix excelligence.json    # repair a file in place, text-level (formatting untouched)
    python api/mojibake.py --check FILE [FILE ...]    # exit 1 if any mojibake remains
    from mojibake import repair                       # the exporter repairs every string it writes

A garbled run is re-encoded as Windows-1252 and decoded as UTF-8. It's replaced only if that
round trip succeeds and gives back real non-ASCII text, so correct text is never touched.
"""

import re
import sys
from pathlib import Path

# A UTF-8 lead byte read as cp1252 (Â..ô), followed by 1-3 continuation bytes read as cp1252.
_CONT = "\u0080-¿ŒœŠšŸŽžƒˆ˜–—‘-‚“-„†-•…‰‹›€™"
RUN = re.compile(f"[Â-ô][{_CONT}]{{1,3}}")


def _fix(m):
    s = m.group(0)
    try:
        out = s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    return out if out and all(ord(c) > 127 for c in out) else s


def repair_str(s):
    return RUN.sub(_fix, s) if isinstance(s, str) else s


def repair(obj):
    """Repair every string in a JSON-shaped object (dicts, lists, strings)."""
    if isinstance(obj, dict):
        return {k: repair(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [repair(v) for v in obj]
    return repair_str(obj)


# excelligence.json is pure ASCII: every non-ASCII character is written as a \uXXXX escape, so the
# garbling hides inside runs of escapes ("â†’" for "→"). Repair those runs too.
ESC_RUN = re.compile(r"(?:\\u[0-9a-fA-F]{4})+")


def _unescape(run):
    return "".join(chr(int(run[i + 2:i + 6], 16)) for i in range(0, len(run), 6))


def _escape(s, like):
    upper = any(c in "ABCDEF" for c in like[2:6])
    return "".join(("\\u%04X" if upper else "\\u%04x") % ord(c) for c in s)


def _fix_escaped(m):
    raw = m.group(0)
    fixed = RUN.sub(_fix, _unescape(raw))
    return raw if fixed == _unescape(raw) else _escape(fixed, raw)


def repair_text(text):
    """Repair a file's text in place: raw garbled runs and escaped ones. Formatting is untouched."""
    return ESC_RUN.sub(_fix_escaped, RUN.sub(_fix, text))


def find(text):
    """Garbled runs that would be repaired, as (offset, garbled, fixed): raw and escaped."""
    hits = [(m.start(), m.group(0), _fix(m)) for m in RUN.finditer(text) if _fix(m) != m.group(0)]
    hits += [(m.start(), _unescape(m.group(0)), RUN.sub(_fix, _unescape(m.group(0))))
             for m in ESC_RUN.finditer(text) if _fix_escaped(m) != m.group(0)]
    return hits


def main(argv):
    if len(argv) >= 2 and argv[0] == "--fix":
        p = Path(argv[1])
        raw = p.read_bytes().decode("utf-8")
        hits = find(raw)
        p.write_bytes(repair_text(raw).encode("utf-8"))
        print(f"{p}: repaired {len(hits)} garbled runs; {len(find(p.read_bytes().decode('utf-8')))} remain")
        return 0
    if len(argv) >= 2 and argv[0] == "--check":
        bad = 0
        for f in argv[1:]:
            hits = find(Path(f).read_bytes().decode("utf-8", errors="replace"))
            for off, g, fx in hits[:5]:
                print(f"{f}: offset {off}: {ascii(g)} should be {ascii(fx)}")
            bad += len(hits)
        print(f"mojibake: {bad} garbled runs")
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
