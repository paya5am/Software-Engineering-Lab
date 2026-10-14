"""Booking ledger for gym fitness classes.

Books members into classes up to a per-class capacity limit, handles
cancellations, and exports the current rosters to a JSON file.
"""

import glob
import json
import os

DEFAULT_EXPORT_FILE = "gym_schedule.json"
GUEST_PROMPT = "How many walk-in guests for HIIT? (Enter for 1): "

CLASS_CAPACITY = {"Yoga": 3, "HIIT": 2, "Spin": 4}
ROSTERS = {}


def book_class(member_id, class_name, attendance_log=None):
    """Book one member into a class.

    Returns True if the member was booked, False if the class is unknown
    or already full.
    """
    if attendance_log is None:
        attendance_log = []
    if class_name not in CLASS_CAPACITY:
        print("Unknown class:", class_name)
        return False
    ROSTERS.setdefault(class_name, [])
    if len(ROSTERS[class_name]) >= CLASS_CAPACITY[class_name]:
        print("Class full:", class_name)
        return False
    ROSTERS[class_name].append(member_id)
    attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Remove a member from a class roster.

    Returns True if a booking was removed, False if there was nothing
    to cancel.
    """
    try:
        ROSTERS[class_name].remove(member_id)
    except (KeyError, ValueError):
        print("Nothing to cancel:", member_id, "in", class_name)
        return False
    return True


def set_capacity(class_name, seats):
    """Set the seat limit for a class.

    Rejects non-integer or negative seat counts and returns False.
    """
    if not isinstance(seats, int) or isinstance(seats, bool) or seats < 0:
        print("Invalid capacity for", class_name, ":", seats)
        return False
    CLASS_CAPACITY[class_name] = seats
    return True


def add_members(class_name, count):
    """Book up to count guests into a class.

    Stops as soon as a booking is refused and returns the number added.
    """
    added = 0
    for index in range(count):
        if not book_class(f"GUEST-{index}", class_name):
            break
        added += 1
    return added


def export_roster(file_path=DEFAULT_EXPORT_FILE):
    """Write the current rosters to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(ROSTERS, handle, indent=2)


def clear_old_exports(prefix="old_"):
    """Delete previously exported roster files matching the prefix.

    Returns the number of files removed.
    """
    removed = 0
    for path in glob.glob(f"{prefix}*.json"):
        os.remove(path)
        removed += 1
    return removed


def read_guest_count(prompt, default=1):
    """Read a non-negative guest count from the user.

    Falls back to default on empty, non-numeric or negative input.
    """
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        print("Not a whole number, using default:", default)
        return default
    if value < 0:
        print("Count cannot be negative, using default:", default)
        return default
    return value


def show_rosters():
    """Print every class roster."""
    for class_name, members in ROSTERS.items():
        print(class_name, ":", ", ".join(str(member) for member in members))


def main():
    """Run a short demonstration of the booking ledger."""
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class("55", "HIIT")
    book_class("M5", "Pilates")
    set_capacity("Spin", -2)
    add_members("Spin", 3)
    cancel_booking("M9", "Boxing")
    guests = read_guest_count(GUEST_PROMPT)
    add_members("HIIT", guests)
    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()
