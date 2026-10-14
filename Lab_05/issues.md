# Lab 5: Static Code Analysis — Issues Found and Fixed

Program: `gym_system.py` (Fitness Club Class Booking Ledger)

Tools: Pylint 3.x, Flake8, Bandit, on Python 3.9.6 in a virtual environment.

Line numbers refer to the original file as committed in `f5426c6`, matching
the reports in `reports/before/`.

## Baseline vs final

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.60/10 | 10.00/10 |
| Bandit | 1 High severity | 0 issues |
| Flake8 | 10 violations | 0 violations |

## Issue table

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| B605 `start_process_with_a_shell` | Security (High, Bandit) | 36 | `os.system("rm -f " + prefix + "*.json")` builds a shell command by string concatenation. Any shell metacharacter reaching `prefix` is executed by the shell, giving command injection (CWE-78). | Dropped the shell entirely. Match files with `glob.glob(f"{prefix}*.json")` and delete each with `os.remove`, so no shell ever parses the string. Returns the count removed. |
| Off-by-one in capacity check | Logic bug (not tool-detected) | 11 | `len(rosters[class_name]) > class_capacity.get(class_name, 0)` compares the roster length *before* insertion with strict `>`, so every class accepts one member beyond its limit. Yoga (capacity 3) held 4; HIIT (capacity 2) held 3. | Changed the comparison to `>=`, so the seat is refused once the roster has already reached capacity. |
| Unknown class silently created and booked | Logic bug (not tool-detected) | 9–11 | `rosters.setdefault`-style creation plus `.get(class_name, 0)` meant booking into a class that was never configured (`Pilates`) created an empty roster, then the `>` comparison let one member in anyway. | Added an explicit membership test against `CLASS_CAPACITY`; unknown classes are reported and refused before any roster is created. |
| Unhandled `ValueError` on user input | Logic bug / crash (not tool-detected) | 52–53 | `int(n)` is called directly on raw `input()`. Any non-numeric entry (e.g. `aaaab`) raises an uncaught `ValueError` and the program dies with a traceback. | Extracted `read_guest_count()`, which strips the input, falls back to the default on empty input, catches `ValueError` for non-numeric input, and rejects negative counts — all with a message instead of a crash. |
| W0102 `dangerous-default-value` | Bug (Pylint) | 8 | `attendance_log=[]` as a default argument is evaluated once at function definition, so the same list is shared and silently accumulates across every call for the life of the process. | Default changed to `None`, with `if attendance_log is None: attendance_log = []` inside the function, giving each call a fresh list. |
| W0702 / E722 bare `except` | Bug (Pylint + Flake8) | 21 | `except:` catches everything including `KeyboardInterrupt` and `SystemExit`, hiding real failures and making the program impossible to interrupt cleanly. | Narrowed to `except (KeyError, ValueError)` — `KeyError` for a class with no roster, `ValueError` for a member not on the roster — and returned a boolean result. |
| W1514 / R1732 unsafe file handling | Bug (Pylint) | 32 | `open(file, "w")` is never closed and specifies no encoding, so the file relies on garbage collection to flush and on the platform's default encoding. | Rewrote as `with open(file_path, "w", encoding="utf-8") as handle:`, which closes deterministically and fixes the encoding. |
| No early exit when class is full | Logic bug (not tool-detected) | 28–29 | `addMembers` loops `count` times regardless of outcome. Entering 500 guests printed "Class full" roughly 500 times after the second seat was taken. | `add_members` now breaks on the first refused booking and returns the number actually added. |
| C0103 `invalid-name` | Convention (Pylint) | 27 | `addMembers` is camelCase, violating PEP 8 snake_case for functions. | Renamed to `add_members` and updated both call sites in `main`. |
| C0114 / C0116 missing docstrings | Convention (Pylint) | 1, 8, 18, 24, 27, 31, 38, 42 | No module docstring and no docstring on any of the seven functions. | Added a module docstring and a docstring to every function describing behaviour and return value. |
| C0209 `consider-using-f-string` | Convention (Pylint) | 15 | `"%s -> %s" % (member_id, class_name)` uses legacy percent formatting. | Replaced with the f-string `f"{member_id} -> {class_name}"`. |
| C0206 `consider-using-dict-items` | Convention (Pylint) | 39 | Iterates dict keys and re-indexes `rosters[c]` on each pass instead of unpacking directly. | Rewrote as `for class_name, members in ROSTERS.items():`. |
| E302 / E305 blank line violations | Style (Flake8) | 8, 18, 24, 27, 31, 35, 38, 42, 58 | Nine occurrences of one blank line where PEP 8 requires two between top-level definitions, plus one after the final definition. | Inserted two blank lines between every top-level definition and before the module-level entry point. |
| `set_capacity` accepts nonsensical values | Logic bug (not tool-detected) | 24–25, 49 | `set_capacity("Spin", -2)` is stored without validation, making the class permanently unbookable while reporting "Class full" — misleading, since the real fault is the configuration. | `set_capacity` now rejects non-integer and negative seat counts, reports the bad value and returns `False`, leaving the previous capacity intact. |
| `main()` executed at import | Design (not tool-detected) | 58 | `main()` is called unconditionally at module level, so merely importing the module runs the whole booking demo and writes to disk. | Guarded with `if __name__ == "__main__": main()`. |

## Behaviour changes after the fixes

The corrected program deliberately produces different output from the original,
because the original output was wrong. Yoga now stops at three members instead of
four. `Pilates` is refused as an unknown class rather than being created on the
fly. Spin's invalid `-2` capacity is rejected, so Spin keeps its configured
capacity of 4 and receives all three guests, where previously it received none.
HIIT stops at two. Non-numeric and negative guest counts fall back to the default
with a message instead of raising.

One further change worth noting: `book_class(55, "HIIT")` passed an integer member
ID among otherwise string IDs, which is a type inconsistency visible in the JSON
export. It is now `book_class("55", "HIIT")`.

## Verification

All three tools were rerun against the fixed file; the results are in
`reports/after/`. The program was also run manually with empty input, a valid
count, a non-numeric string, a count far above capacity, and a negative count.
None produced a traceback, and the JSON export was confirmed to write correctly.
