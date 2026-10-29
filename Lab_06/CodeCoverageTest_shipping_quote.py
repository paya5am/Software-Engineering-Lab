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


def test_invalid_shipments_type_raises():
    with pytest.raises(ValueError):
        process_shipments("not a list", 10.0)


def test_air_express_heavy_package():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "air",
            "express_priority": True,
            "packages": [{"weight_kg": 40}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 912.5
    assert result["status"] == "CLEARED"


def test_rejections_trigger_flagged_review():
    shipments = [
        {"manifest_approved": False, "mode": "ground",
         "packages": [{"weight_kg": 5}]},
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


def test_pressure_stable():
    assert monitor_container_pressures([[15.0, 16.0], [20.0]]) == "STABLE"
