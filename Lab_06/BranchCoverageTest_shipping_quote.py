import pytest
from shipping_quote import process_shipments, monitor_container_pressures


def test_single_ground_shipment():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "express_priority": False,
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"


def test_non_list_shipments_raises():
    with pytest.raises(ValueError):
        process_shipments("not a list", 10.0)


def test_negative_handling_fee_raises():
    with pytest.raises(ValueError):
        process_shipments([], -1.0)


def test_empty_list_is_no_cargo():
    result = process_shipments([], 10.0)
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_unapproved_and_missing_manifest_skipped():
    shipments = [
        {"manifest_approved": False, "packages": [{"weight_kg": 5}]},
        {"packages": [{"weight_kg": 5}]},
    ]
    result = process_shipments(shipments, 10.0)
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_default_mode_is_ground():
    shipments = [{"manifest_approved": True, "packages": [{"weight_kg": 2}]}]
    result = process_shipments(shipments, 1.0)
    assert result["total_quote"] == 9.0


def test_air_normal_weight():
    shipments = [{"manifest_approved": True, "mode": "air",
                  "packages": [{"weight_kg": 10}]}]
    result = process_shipments(shipments, 0.0)
    assert result["total_quote"] == 120.0


def test_weight_exactly_30_is_not_heavy():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 30}]}]
    assert process_shipments(shipments, 0.0)["total_quote"] == 120.0


def test_weight_31_is_heavy():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 31}]}]
    assert process_shipments(shipments, 0.0)["total_quote"] == 186.0


def test_air_express_heavy_package():
    shipments = [{"manifest_approved": True, "mode": "air",
                  "express_priority": True, "packages": [{"weight_kg": 40}]}]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 912.5


def test_ground_express_multiplier():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "express_priority": True, "packages": [{"weight_kg": 10}]}]
    assert process_shipments(shipments, 20.0)["total_quote"] == 75.0


def test_hazmat_not_fragile_adds_surcharge():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 10},
                               {"weight_kg": 2, "is_hazmat": True}]}]
    result = process_shipments(shipments, 10.0)
    assert result == {"total_quote": 100.0, "status": "CLEARED"}


def test_hazmat_fragile_zeroes_shipment_and_gives_no_cargo():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "is_fragile": True,
                  "packages": [{"weight_kg": 5, "is_hazmat": True}]}]
    result = process_shipments(shipments, 10.0)
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_unknown_mode_rejected():
    shipments = [{"manifest_approved": True, "mode": "sea",
                  "packages": [{"weight_kg": 5}]}]
    result = process_shipments(shipments, 10.0)
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_exactly_three_rejections_still_cleared():
    shipments = [{"manifest_approved": True, "mode": "ground",
                  "packages": [{"weight_kg": 0}, {"weight_kg": 0},
                               {"weight_kg": -1}, {"weight_kg": 5}]}]
    result = process_shipments(shipments, 0.0)
    assert result == {"total_quote": 20.0, "status": "CLEARED"}


def test_four_rejections_flagged_review():
    shipments = [
        {"manifest_approved": True, "mode": "sea"},
        {"manifest_approved": True, "mode": "rail"},
        {"manifest_approved": True, "mode": "ground", "is_fragile": True,
         "packages": [{"weight_kg": 0}, {"weight_kg": 5, "is_hazmat": True}]},
    ]
    result = process_shipments(shipments, 5.0)
    assert result == {"total_quote": 0.0, "status": "FLAGGED_REVIEW"}


def test_pressure_no_data():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_pressure_leak_detected():
    assert monitor_container_pressures([[15.0, 13.0, 12.0]]) == "LEAK_DETECTED"


def test_pressure_streak_resets_on_normal_reading():
    assert monitor_container_pressures([[13.0, 15.0, 13.0]]) == "STABLE"


def test_pressure_exactly_14_is_not_low():
    assert monitor_container_pressures([[14.0, 14.0]]) == "STABLE"


def test_pressure_streak_resets_between_containers():
    assert monitor_container_pressures([[13.0], [13.0]]) == "STABLE"
