#!/usr/bin/env python3
"""Fail if registry drift comes back.

excelligence.json is the single source of truth. Pages fetch it at load; they
must not carry their own copy of it, and every entry id they mention must
exist in it.

Checks every .html / .js file in the repo:
  1. EMBEDDED  - a literal that looks like an entries array or entry table:
                 10+ records of the form  id:'FRM-0001', name:...  or
                 'FRM-0001':{name:...}
  2. UNKNOWN   - an entry id (FRM-/PTN-/ARC-/... + 4 digits; families taken
                 from the registry's own entry types) that is not in
                 excelligence.json
  3. LEARN     - a /learn/<slug>/ link whose folder (learn/<slug>/index.html)
                 does not exist, or a /learn/ link built at runtime
                 (/learn/${...}) that cannot be checked

Usage:  python tools/check_registry.py [--root PATH]
Exit:   0 = clean, 1 = findings, 2 = registry unreadable.
Python stdlib only.
"""
import argparse
import json
import os
import re
import sys

EMBED_THRESHOLD = 10
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".vercel"}
EXTS = (".html", ".htm", ".js", ".mjs")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="repo root (default: parent of tools/)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    try:
        with open(os.path.join(root, "excelligence.json"), encoding="utf-8") as f:
            reg = json.load(f)
        ids = {e["id"] for e in reg["entries"]}
        families = sorted({e["type"] for e in reg["entries"]} | {i.split("-")[0] for i in ids})
    except Exception as exc:  # a gate that cannot run must refuse, not pass
        print(f"check_registry: cannot read excelligence.json: {exc}")
        return 2

    fam = "|".join(map(re.escape, families))
    id_re = re.compile(r"(?<![A-Za-z0-9_-])(?:%s)-\d{4}(?![0-9])" % fam)
    embed_res = [
        # {id:'FRM-0001', name:...}  /  {"id":"FRM-0001","name":...}  (not entry_id:)
        re.compile(r"(?<![A-Za-z0-9_$])[\"']?id[\"']?\s*:\s*[\"'](?:%s)-\d{4}[\"']\s*,\s*[\"']?name[\"']?\s*:" % fam),
        # 'FRM-0001':{name:...}
        re.compile(r"[\"'](?:%s)-\d{4}[\"']\s*:\s*\{\s*[\"']?name[\"']?\s*:" % fam),
    ]
    learn_re = re.compile(r"/learn/([A-Za-z0-9_.-]+)/")
    learn_dyn_re = re.compile(r"/learn/\$\{")

    findings = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if not fn.lower().endswith(EXTS):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError as exc:
                findings.append((rel, 0, "UNREADABLE", str(exc)))
                continue
            scanned += 1

            embedded = sum(len(r.findall(text)) for r in embed_res)
            if embedded >= EMBED_THRESHOLD:
                first = min(m.start() for r in embed_res for m in [r.search(text)] if m)
                findings.append((rel, text.count("\n", 0, first) + 1, "EMBEDDED",
                                 f"{embedded} embedded entry records; fetch /excelligence.json instead"))

            for lineno, line in enumerate(text.splitlines(), 1):
                unknown = sorted({m.group(0) for m in id_re.finditer(line)} - ids)
                for u in unknown:
                    findings.append((rel, lineno, "UNKNOWN", f"{u} is not in excelligence.json"))
                for m in learn_re.finditer(line):
                    slug = m.group(1)
                    if not os.path.isfile(os.path.join(root, "learn", slug, "index.html")):
                        findings.append((rel, lineno, "LEARN", f"/learn/{slug}/ has no learn/{slug}/index.html"))
                if learn_dyn_re.search(line):
                    findings.append((rel, lineno, "LEARN", "runtime-built /learn/${...}/ link cannot be verified"))

    # MOJIBAKE: garbled text (UTF-8 read as Windows-1252) in the registry. The workbook carries it,
    # and api/mojibake.py repairs it on export; this makes sure it never comes back.
    sys.path.insert(0, os.path.join(root, "api"))
    try:
        from mojibake import find as find_mojibake
        with open(os.path.join(root, "excelligence.json"), encoding="utf-8") as f:
            reg_text = f.read()
        for off, garbled, fixed in find_mojibake(reg_text):
            findings.append(("excelligence.json", reg_text.count("\n", 0, off) + 1, "MOJIBAKE",
                             f"{ascii(garbled)} should be {ascii(fixed)}; run python api/mojibake.py --fix excelligence.json"))
    except ImportError as exc:  # a gate that cannot run must refuse, not pass
        findings.append(("api/mojibake.py", 0, "UNREADABLE", f"mojibake check unavailable: {exc}"))

    for rel, lineno, kind, msg in findings:
        print(f"{rel}:{lineno}: {kind}: {msg}")
    kinds = {}
    for _, _, k, _ in findings:
        kinds[k] = kinds.get(k, 0) + 1
    summary = ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())) or "none"
    print(f"check_registry: {scanned} files, {len(ids)} registry ids, findings: {summary}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
