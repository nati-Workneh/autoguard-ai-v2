"""Schema package for the AutoGuard AI V2 production API."""

from __future__ import annotations

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
