"""Orchestration service for the Sprint 8.8 quick-predict endpoint."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from backend.feature_builder import DriverInputs, FeatureBuilder
from backend.predictor import AutoGuardPredictor, PredictionResponse
from backend.schemas import PredictionRequest
from backend.services.city_mapper import CityMapper
from backend.services.premium_impact import PremiumImpactEstimate, estimate_premium_impact
from backend.services.vehicle_lookup import VehicleLookupRecord, VehicleLookupService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class QuickPredictResult:
    """Internal quick-predict result before API serialization."""

    vehicle: VehicleLookupRecord
    prediction: PredictionResponse
    premium_impact: PremiumImpactEstimate


class QuickPredictService:
    """Coordinate lookup, enrichment, payload assembly, and frozen prediction."""

    def __init__(
        self,
        *,
        vehicle_lookup_service: VehicleLookupService,
        city_mapper: CityMapper,
        feature_builder: FeatureBuilder,
        predictor: AutoGuardPredictor,
    ) -> None:
        self.vehicle_lookup_service = vehicle_lookup_service
        self.city_mapper = city_mapper
        self.feature_builder = feature_builder
        self.predictor = predictor

    def quick_predict(
        self,
        *,
        license_plate: str,
        driver_age: float,
        policy_tenure: float,
        city: str,
        policy_id: str | None = None,
    ) -> QuickPredictResult:
        """Run the full approved quick-predict flow in one call."""

        logger.info("quick_predict.started city=%s plate=%s", city, self._mask_license_plate(license_plate))

        try:
            vehicle_record = self.vehicle_lookup_service.lookup_vehicle(license_plate)
        except Exception:
            logger.exception(
                "quick_predict.vehicle_lookup_failed city=%s plate=%s",
                city,
                self._mask_license_plate(license_plate),
            )
            raise

        try:
            city_record = self.city_mapper.resolve_city(city)
        except Exception:
            logger.exception(
                "quick_predict.city_mapper_failed city=%s plate=%s",
                city,
                self._mask_license_plate(license_plate),
            )
            raise

        try:
            payload = self.feature_builder.build_model_payload(
                driver_inputs=DriverInputs(
                    driver_age=driver_age,
                    policy_tenure=policy_tenure,
                    city_of_residence=city,
                    license_plate=license_plate,
                ),
                vehicle_lookup=vehicle_record,
                city_lookup=city_record,
                policy_id=policy_id,
            )
        except Exception:
            logger.exception(
                "quick_predict.feature_builder_failed city=%s plate=%s driver_age=%s policy_tenure=%s",
                city,
                self._mask_license_plate(license_plate),
                driver_age,
                policy_tenure,
            )
            raise

        try:
            prediction = self.predictor.predict(PredictionRequest(**payload))
        except Exception:
            logger.exception(
                "quick_predict.predictor_failed city=%s plate=%s",
                city,
                self._mask_license_plate(license_plate),
            )
            raise

        premium_impact = estimate_premium_impact(
            risk_level=prediction.risk_level,
            claim_probability=prediction.claim_probability,
            low_cutoff=self.predictor.low_cutoff,
            high_cutoff=self.predictor.high_cutoff,
        )

        logger.info(
            "quick_predict.completed city=%s plate=%s risk=%s probability=%.4f premium_impact=%s",
            city,
            self._mask_license_plate(license_plate),
            prediction.risk_level,
            prediction.claim_probability,
            premium_impact.direction,
        )
        return QuickPredictResult(vehicle=vehicle_record, prediction=prediction, premium_impact=premium_impact)

    @staticmethod
    def _mask_license_plate(license_plate: str) -> str:
        digits = "".join(character for character in str(license_plate) if character.isdigit())
        if len(digits) <= 4:
            return digits or "unknown"
        return f"{digits[:2]}***{digits[-2:]}"
