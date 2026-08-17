"""FastAPI app for AutoGuard AI: serves the V2 production model (model_v2.pkl)."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.feature_builder_v2 import (
    FeatureBuilderV2,
    FeatureBuilderV2Error,
    InvalidDriverInputV2Error,
    InvalidOwnershipError,
    MissingVehicleLookupV2Error,
)
from backend.input_domain import FIELD_LABELS_HE
from backend.predictor_v2 import ArtifactLoadErrorV2, AutoGuardPredictorV2
from backend.schemas.quick_predict_v2 import (
    QuickPredictV2DomainWarning,
    QuickPredictV2DomainWarningField,
    QuickPredictV2Metadata,
    QuickPredictV2PremiumImpact,
    QuickPredictV2Prediction,
    QuickPredictV2Request,
    QuickPredictV2Response,
    QuickPredictV2RiskDriver,
    QuickPredictV2Vehicle,
)
from backend.schemas.vehicle_lookup import VehicleLookupRequest, VehicleLookupResponse
from backend.services.quick_predict_v2 import QuickPredictServiceV2
from backend.services.vehicle_lookup import (
    InvalidLicensePlateError,
    VehicleLookupError,
    VehicleLookupService,
    VehicleLookupTimeoutError,
    VehicleLookupUpstreamError,
    VehicleNotFoundError,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "06_Production_Interface" / "frontend" / "static"
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor_v2 = AutoGuardPredictorV2()
    vehicle_lookup_service = VehicleLookupService()
    feature_builder_v2 = FeatureBuilderV2()
    quick_predict_service_v2 = QuickPredictServiceV2(
        vehicle_lookup_service=vehicle_lookup_service,
        feature_builder=feature_builder_v2,
        predictor=predictor_v2,
    )

    app.state.predictor_v2 = predictor_v2
    app.state.vehicle_lookup_service = vehicle_lookup_service
    app.state.feature_builder_v2 = feature_builder_v2
    app.state.quick_predict_service_v2 = quick_predict_service_v2
    yield
    app.state.predictor_v2 = None
    app.state.vehicle_lookup_service = None
    app.state.feature_builder_v2 = None
    app.state.quick_predict_service_v2 = None


app = FastAPI(
    title="AutoGuard AI - Insurance Underwriting Assistant",
    version="v2_production",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("request_validation_error path=%s detail=%s", request.url.path, exc.errors())
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": exc.errors()}))


@app.exception_handler(InvalidLicensePlateError)
async def invalid_license_plate_handler(request: Request, exc: InvalidLicensePlateError) -> JSONResponse:
    logger.warning("invalid_license_plate path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(VehicleNotFoundError)
async def vehicle_not_found_handler(request: Request, exc: VehicleNotFoundError) -> JSONResponse:
    logger.warning("vehicle_not_found path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(VehicleLookupTimeoutError)
async def vehicle_lookup_timeout_handler(request: Request, exc: VehicleLookupTimeoutError) -> JSONResponse:
    logger.warning("vehicle_lookup_timeout path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=504, content={"detail": str(exc)})


@app.exception_handler(VehicleLookupUpstreamError)
async def vehicle_lookup_upstream_handler(request: Request, exc: VehicleLookupUpstreamError) -> JSONResponse:
    logger.warning("vehicle_lookup_upstream_error path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(VehicleLookupError)
async def vehicle_lookup_error_handler(request: Request, exc: VehicleLookupError) -> JSONResponse:
    logger.exception("vehicle_lookup_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(InvalidOwnershipError)
async def invalid_ownership_handler(request: Request, exc: InvalidOwnershipError) -> JSONResponse:
    logger.warning("invalid_ownership path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(InvalidDriverInputV2Error)
async def invalid_driver_input_v2_handler(request: Request, exc: InvalidDriverInputV2Error) -> JSONResponse:
    logger.warning("invalid_driver_input_v2 path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(MissingVehicleLookupV2Error)
async def missing_vehicle_lookup_v2_handler(request: Request, exc: MissingVehicleLookupV2Error) -> JSONResponse:
    logger.exception("missing_vehicle_lookup_v2 path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(FeatureBuilderV2Error)
async def feature_builder_v2_error_handler(request: Request, exc: FeatureBuilderV2Error) -> JSONResponse:
    logger.exception("feature_builder_v2_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ArtifactLoadErrorV2)
async def artifact_load_v2_handler(request: Request, exc: ArtifactLoadErrorV2) -> JSONResponse:
    logger.exception("artifact_load_error_v2 path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/api/v2/health")
def health_v2() -> dict[str, object]:
    """Health check for the production model (model_v2.pkl)."""
    predictor_v2: AutoGuardPredictorV2 | None = getattr(app.state, "predictor_v2", None)
    model_loaded = predictor_v2 is not None and predictor_v2.model_loaded
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "model_name": predictor_v2.model_name if predictor_v2 else "unavailable",
        "model_version": predictor_v2.model_version if predictor_v2 else "unavailable",
    }


@app.post("/api/vehicle-lookup", response_model=VehicleLookupResponse)
def vehicle_lookup(payload: VehicleLookupRequest) -> VehicleLookupResponse:
    vehicle_lookup_service: VehicleLookupService = app.state.vehicle_lookup_service
    record = vehicle_lookup_service.lookup_vehicle(payload.license_plate)
    return VehicleLookupResponse(
        manufacturer=record.manufacturer,
        commercial_model=record.commercial_model,
        production_year=record.production_year,
        age_of_car=record.age_of_car,
        fuel_type_raw=record.fuel_type_raw,
    )


@app.post("/api/v2/quick-predict", response_model=QuickPredictV2Response)
def quick_predict_v2(payload: QuickPredictV2Request) -> QuickPredictV2Response:
    """Quick-predict endpoint, served by model_v2.pkl."""
    quick_predict_service_v2: QuickPredictServiceV2 = app.state.quick_predict_service_v2
    result = quick_predict_service_v2.quick_predict(
        license_plate=payload.license_plate,
        age=payload.age,
        driving_experience_years=payload.driving_experience_years,
        past_accidents=payload.past_accidents,
        speeding_violations=payload.speeding_violations,
        duis=payload.duis,
        annual_mileage=payload.annual_mileage,
        vehicle_ownership=payload.vehicle_ownership,
    )

    domain_warning = None
    if result.domain_warning_fields:
        field_summaries = ", ".join(
            f"{FIELD_LABELS_HE.get(f.field, f.field)}={f.value:g} (0-{f.supported_max:g})"
            for f in result.domain_warning_fields
        )
        domain_warning = QuickPredictV2DomainWarning(
            message=(
                "One or more inputs fall outside the range the model was trained on "
                f"({field_summaries}); treat this estimate as unreliable."
            ),
            fields=[
                QuickPredictV2DomainWarningField(
                    field=f.field,
                    value=f.value,
                    supported_min=f.supported_min,
                    supported_max=f.supported_max,
                )
                for f in result.domain_warning_fields
            ],
        )

    return QuickPredictV2Response(
        vehicle=QuickPredictV2Vehicle(
            manufacturer=result.vehicle.manufacturer,
            commercial_model=result.vehicle.commercial_model,
            production_year=result.vehicle.production_year,
            vehicle_year_category=result.vehicle_year_category,
        ),
        prediction=QuickPredictV2Prediction(
            claim_probability=result.prediction.claim_probability,
            risk_level=result.prediction.risk_level,
            recommendation=result.prediction.recommendation,
            business_action=result.prediction.business_action,
            business_threshold=result.prediction.business_threshold,
            policy_version=result.prediction.policy_version,
        ),
        premium_impact=QuickPredictV2PremiumImpact(
            direction=result.premium_impact.direction,
            min_percent=result.premium_impact.min_percent,
            max_percent=result.premium_impact.max_percent,
            estimated_percent=result.premium_impact.estimated_percent,
            summary=result.premium_impact.summary,
        ),
        top_risk_drivers=[
            QuickPredictV2RiskDriver(
                title=driver.title,
                direction=driver.direction,
                detail=driver.detail,
            )
            for driver in result.prediction.top_risk_drivers
        ],
        metadata=QuickPredictV2Metadata(
            model_version=result.prediction.model_version,
            model_name=result.prediction.model_name,
            prediction_timestamp=result.prediction.prediction_timestamp,
        ),
        input_domain_warning=domain_warning,
    )


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
