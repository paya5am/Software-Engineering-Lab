import json
import math  # FIX: needed to reject nan/inf values


def calculate_dimensional_weight(dimensions_str):
    # FIX: reject None and any non-string input
    if not isinstance(dimensions_str, str):
        return None
    dims = dimensions_str.split('x')
    # FIX: must have exactly 3 parts (LxWxH)
    if len(dims) != 3:
        return None
    # FIX: reject parts that are not numbers (empty, letters, etc.)
    try:
        length, width, height = (float(d) for d in dims)
    except ValueError:
        return None
    # FIX: reject nan, inf, zero and negative sizes
    if not all(math.isfinite(v) and v > 0 for v in (length, width, height)):
        return None
    result = round((length * width * height) / 5000.0, 2)
    # FIX: huge sizes can overflow to inf
    if not math.isfinite(result):
        return None
    return result


def format_tracking_label(raw_code):
    # FIX: reject None, non-strings, and codes too short to have a prefix + number
    if not isinstance(raw_code, str) or len(raw_code) < 2:
        return None
    prefix = raw_code[0]
    digits = raw_code[1:]
    # FIX: prefix must be a letter, the rest must be plain digits (no signs, spaces, symbols)
    if not prefix.isalpha() or not (digits.isascii() and digits.isdigit()):
        return None
    try:
        tracking_num = int(digits)
    except ValueError:
        return None
    return f"{prefix.upper()}-{tracking_num:06d}"


def parse_package_manifest(json_payload):
    # FIX: reject None and non-string input
    if not isinstance(json_payload, str):
        return None
    # FIX: reject invalid JSON (and absurdly deep nesting)
    try:
        data = json.loads(json_payload)
    except (ValueError, RecursionError):
        return None
    # FIX: JSON must be an object with a "weight" key
    if not isinstance(data, dict) or "weight" not in data:
        return None
    weight = data["weight"]
    # FIX: weight must be a real number (bool is not allowed)
    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        return None
    try:
        weight = float(weight)
    except OverflowError:
        return None
    # FIX: reject nan, inf and negative weights
    if not math.isfinite(weight) or weight < 0:
        return None
    return weight


def main():
    print("==== Running calculate_dimensional_weight ====")
    dims_input = input("Enter dimensions LxWxH in cm (e.g. 20x30x10): ")
    dim_weight = calculate_dimensional_weight(dims_input)
    # FIX: report invalid input instead of crashing
    if dim_weight is None:
        print("Invalid dimensions")
    else:
        print("Dimensional Weight (kg):", dim_weight)

    print("\n==== Running format_tracking_label ====")
    code_input = input("Enter raw code (e.g. E123): ")
    label = format_tracking_label(code_input)
    if label is None:
        print("Invalid tracking code")
    else:
        print("Formatted Label:", label)

    print("\n==== Running parse_package_manifest ====")
    json_input = input('Enter manifest JSON (e.g. {"weight": 12.5}): ')
    weight = parse_package_manifest(json_input)
    if weight is None:
        print("Invalid manifest")
    else:
        print("Manifest Weight:", weight)


if __name__ == "__main__":
    main()
