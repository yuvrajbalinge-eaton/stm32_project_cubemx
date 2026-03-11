import os
import re
import argparse
from collections import Counter

# Extensions to scan
EXTS = {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx"}

# Minimal feature patterns per standard
PATTERNS = {
    "c89": [],
    "c99": [
        (r"\brestrict\b", "restrict"),
        (r"#\s*include\s*<stdint.h>", "stdint.h"),
        (r"#\s*include\s*<stdbool.h>", "stdbool.h"),
    ],
    "c11": [
        (r"\b_Atomic\b", "_Atomic"),
        (r"\b_Static_assert\b", "_Static_assert"),
    ],
    "c17": [],  # C17 added no major new tokens
    "c++11": [
        (r"\bnullptr\b", "nullptr"),
        (r"\bconstexpr\b", "constexpr"),
        (r"\benum class\b", "enum class"),
        (r"\bauto\s+[A-Za-z_]\w*\s*=", "auto variable"),
    ],
    "c++14": [
        (r"\bdecltype\s*\(\s*auto\s*\)", "decltype(auto)"),
    ],
    "c++17": [
        (r"\bif constexpr\b", "if constexpr"),
        (r"\bstd::optional\b", "std::optional"),
        (r"\bstd::variant\b", "std::variant"),
    ],
    "c++20": [
        (r"\brequires\b", "requires"),
        (r"<=>", "spaceship operator"),
    ],
}

ORDER = ["c89", "c99", "c11", "c17", "c++11", "c++14", "c++17", "c++20"]


def collect_files(root):
    src = []
    for dp, _, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in EXTS:
                src.append(os.path.join(dp, f))
    return src


def scan_file(path):
    try:
        text = open(path, "r", errors="ignore").read()
    except:
        return Counter()

    res = Counter()
    for std, pats in PATTERNS.items():
        for pat, _name in pats:
            res[std] += len(re.findall(pat, text))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".")
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    print(f"\nScanning folder: {root}\n")

    files = collect_files(root)
    if not files:
        print("❌ No C/C++ source files found.")
        return

    print(f"Found {len(files)} source files.\n")

    totals = Counter()
    for f in files:
        totals.update(scan_file(f))

    print("========= STANDARD USAGE =========\n")

    total_hits = sum(totals.values())

    if total_hits == 0:
        print("No specific features detected. Likely uses C89/C90 or C++03.")
    else:
        for s in ORDER:
            pct = (totals[s] / total_hits * 100) if total_hits else 0
            print(f"{s:>6}: {totals[s]:4d} hits | {pct:5.1f}%")

    print("\nSuggested minimum standard:", end=" ")

    for s in reversed(ORDER):
        if totals[s] > 0:
            print(s)
            break
    else:
        print("C89/C++03")

    print("\nDone.\n")


if __name__ == "__main__":
    main()