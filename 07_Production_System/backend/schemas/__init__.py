"""Schema package wrapper for the frozen backend contracts.

This package preserves the existing `backend.schemas` import surface while
adding new schema modules under `backend/schemas/`.
"""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_SCHEMAS_PATH = Path(__file__).resolve().parents[1] / "schemas.py"
_LEGACY_SPEC = spec_from_file_location("backend._legacy_schemas", _LEGACY_SCHEMAS_PATH)
if _LEGACY_SPEC is None or _LEGACY_SPEC.loader is None:  # pragma: no cover - import-time guard
    raise ImportError(f"Could not load legacy schemas module from {_LEGACY_SCHEMAS_PATH}")

_legacy_module = module_from_spec(_LEGACY_SPEC)
sys.modules[_LEGACY_SPEC.name] = _legacy_module
_LEGACY_SPEC.loader.exec_module(_legacy_module)

for _name in dir(_legacy_module):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_legacy_module, _name)

from .city_mapper import CityLookupRequest, CityLookupResponse
from .quick_predict import (
    QuickPredictMetadata,
    QuickPredictPrediction,
    QuickPredictRequest,
    QuickPredictResponse,
    QuickPredictRiskDriver,
    QuickPredictVehicle,
)
from .vehicle_lookup import VehicleLookupRequest, VehicleLookupResponse
from .quick_predict_v2 import (
    QuickPredictV2Metadata,
    QuickPredictV2PremiumImpact,
    QuickPredictV2Prediction,
    QuickPredictV2Request,
    QuickPredictV2Response,
    QuickPredictV2RiskDriver,
    QuickPredictV2Vehicle,
    VehicleOwnership,
)

__all__ = [name for name in globals() if not name.startswith("_")]
