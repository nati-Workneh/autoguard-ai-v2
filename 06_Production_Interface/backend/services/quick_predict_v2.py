"""Orchestration service for the V2 quick-predict endpoint."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from backend.feature_builder_v2 import DriverInputsV2, FeatureBuilderV2
from backend.predictor_v2 import AutoGuardPredictorV2, PredictionResultV2
from backend.services.premium_impact import PremiumImpactEstimate, estimate_premium_impact
from backend.services.vehicle_lookup import VehicleLookupRecord, VehicleLookupService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class QuickPredictV2Result:
    """Internal V2 quick-predict result before API serialization."""

    vehicle: VehicleLookupRecord
    vehicle_year_category: str
    prediction: PredictionResultV2
    premium_impact: PremiumImpactEstimate


class QuickPredictServiceV2:
    """Coordinate vehicle lookup, V2 feature assembly, and model_v2 prediction."""

    def __init__(
        self,
        *,
        vehicle_lookup_service: VehicleLookupService,
        feature_builder: FeatureBuilderV2,
        predictor: AutoGuardPredictorV2,
    ) -> None:
        self.vehicle_lookup_service = vehicle_lookup_service
        self.feature_builder = feature_builder
        self.predictor = predictor

    def quick_predict(
        self,
        *,
        license_plate: str,
        age: int,
        driving_experience_years: int,
        past_accidents: int,
        speeding_violations: int,
        duis: int,
        annual_mileage: float,
        vehicle_ownership: str,
    ) -> QuickPredictV2Result:
        """Run the full V2 quick-predict flow against model_v2.pkl."""

        logger.info("quick_predict_v2.started plate=%s", self._mask_license_plate(license_plate))

        try:
            vehicle_record = self.vehicle_lookup_service.lookup_vehicle(license_plate)
        except Exception:
            logger.exception(
                "quick_predict_v2.vehicle_lookup_failed plate=%s",
                self._mask_license_plate(license_plate),
            )
            raise

        try:
            model_frame = self.feature_builder.build_model_frame(
                driver_inputs=DriverInputsV2(
                    age_years=age,
                    driving_experience_years=driving_experience_years,
                    past_accidents=past_accidents,
                    speeding_violations=speeding_violations,
                    duis=duis,
                    annual_mileage=annual_mileage,
                    vehicle_ownership=vehicle_ownership,
                ),
                vehicle_lookup=vehicle_record,
            )
        except Exception:
            logger.exception(
                "quick_predict_v2.feature_builder_failed plate=%s vehicle_ownership=%s",
                self._mask_license_plate(license_plate),
                vehicle_ownership,
            )
            raise

        try:
            prediction = self.predictor.predict(model_frame)
        except Exception:
            logger.exception(
                "quick_predict_v2.predictor_failed plate=%s",
                self._mask_license_plate(license_plate),
            )
            raise

        premium_impact = estimate_premium_impact(
            risk_level=prediction.risk_level,
            claim_probability=prediction.claim_probability,
            low_cutoff=self.predictor.low_cutoff,
            high_cutoff=self.predictor.high_cutoff,
        )

        vehicle_year_category = str(model_frame.iloc[0]["VEHICLE_YEAR"])

        logger.info(
            "quick_predict_v2.completed plate=%s risk=%s probability=%.4f model_version=%s",
            self._mask_license_plate(license_plate),
            prediction.risk_level,
            prediction.claim_probability,
            prediction.model_version,
        )
        return QuickPredictV2Result(
            vehicle=vehicle_record,
            vehicle_year_category=vehicle_year_category,
            prediction=prediction,
            premium_impact=premium_impact,
        )

    @staticmethod
    def _mask_license_plate(license_plate: str) -> str:
        digits = "".join(character for character in str(license_plate) if character.isdigit())
        if len(digits) <= 4:
            return digits or "unknown"
        return f"{digits[:2]}***{digits[-2:]}"
