"""Sprint 7 FastAPI app for AutoGuard AI."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.feature_builder import (
    FeatureBuilder,
    FeatureBuilderError,
    IncompletePayloadError,
    InvalidDriverInputError,
    MissingCityMappingError,
    MissingVehicleLookupError,
)
from backend.feature_builder_v2 import (
    FeatureBuilderV2,
    FeatureBuilderV2Error,
    InvalidDriverInputV2Error,
    InvalidOwnershipError,
    MissingVehicleLookupV2Error,
)
from backend.predictor import ArtifactLoadError, AutoGuardPredictor, PredictionContractError
from backend.predictor_v2 import ArtifactLoadErrorV2, AutoGuardPredictorV2
from backend.schemas.quick_predict import (
    QuickPredictMetadata,
    QuickPredictPrediction,
    QuickPredictPremiumImpact,
    QuickPredictRequest,
    QuickPredictResponse,
    QuickPredictRiskDriver,
    QuickPredictVehicle,
)
from backend.schemas.quick_predict_v2 import (
    QuickPredictV2Metadata,
    QuickPredictV2PremiumImpact,
    QuickPredictV2Prediction,
    QuickPredictV2Request,
    QuickPredictV2Response,
    QuickPredictV2RiskDriver,
    QuickPredictV2Vehicle,
)
from backend.schemas.vehicle_lookup import VehicleLookupRequest, VehicleLookupResponse
from backend.schemas import FormContractResponse, HealthResponse, PredictionRequest, PredictionResponse
from backend.services.city_mapper import CityLookupError, CityMapper, CityNotFoundError, InvalidCityError
from backend.services.quick_predict import QuickPredictService
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
FRONTEND_DIR = PROJECT_ROOT / "07_Production_System" / "frontend" / "static"
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # V1 -- legacy/archive serving path (random_forest.joblib). Kept fully
    # functional but no longer the active path the frontend targets.
    predictor = AutoGuardPredictor()
    vehicle_lookup_service = VehicleLookupService()
    city_mapper = CityMapper()
    feature_builder = FeatureBuilder()
    quick_predict_service = QuickPredictService(
        vehicle_lookup_service=vehicle_lookup_service,
        city_mapper=city_mapper,
        feature_builder=feature_builder,
        predictor=predictor,
    )

    # V2 -- active production serving path (model_v2.pkl, Sprint 10.6 freeze).
    predictor_v2 = AutoGuardPredictorV2()
    feature_builder_v2 = FeatureBuilderV2()
    quick_predict_service_v2 = QuickPredictServiceV2(
        vehicle_lookup_service=vehicle_lookup_service,
        feature_builder=feature_builder_v2,
        predictor=predictor_v2,
    )

    app.state.predictor = predictor
    app.state.vehicle_lookup_service = vehicle_lookup_service
    app.state.city_mapper = city_mapper
    app.state.feature_builder = feature_builder
    app.state.quick_predict_service = quick_predict_service

    app.state.predictor_v2 = predictor_v2
    app.state.feature_builder_v2 = feature_builder_v2
    app.state.quick_predict_service_v2 = quick_predict_service_v2
    yield
    app.state.predictor = None
    app.state.vehicle_lookup_service = None
    app.state.city_mapper = None
    app.state.feature_builder = None
    app.state.quick_predict_service = None
    app.state.predictor_v2 = None
    app.state.feature_builder_v2 = None
    app.state.quick_predict_service_v2 = None


app = FastAPI(
    title="AutoGuard AI - Insurance Underwriting Assistant",
    version="sprint_10_7_v2_production_v1",
    lifespan=lifespan,
)


@app.exception_handler(PredictionContractError)
async def prediction_contract_handler(request: Request, exc: PredictionContractError) -> JSONResponse:
    logger.warning("prediction_contract_error path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("request_validation_error path=%s detail=%s", request.url.path, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(ArtifactLoadError)
async def artifact_load_handler(request: Request, exc: ArtifactLoadError) -> JSONResponse:
    logger.exception("artifact_load_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


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


@app.exception_handler(InvalidCityError)
async def invalid_city_handler(request: Request, exc: InvalidCityError) -> JSONResponse:
    logger.warning("invalid_city path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(CityNotFoundError)
async def city_not_found_handler(request: Request, exc: CityNotFoundError) -> JSONResponse:
    logger.warning("city_not_found path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(CityLookupError)
async def city_lookup_error_handler(request: Request, exc: CityLookupError) -> JSONResponse:
    logger.exception("city_lookup_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(InvalidDriverInputError)
async def invalid_driver_input_handler(request: Request, exc: InvalidDriverInputError) -> JSONResponse:
    logger.warning("invalid_driver_input path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(IncompletePayloadError)
async def incomplete_payload_handler(request: Request, exc: IncompletePayloadError) -> JSONResponse:
    logger.warning("incomplete_payload path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(MissingVehicleLookupError)
async def missing_vehicle_lookup_handler(request: Request, exc: MissingVehicleLookupError) -> JSONResponse:
    logger.exception("missing_vehicle_lookup path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(MissingCityMappingError)
async def missing_city_mapping_handler(request: Request, exc: MissingCityMappingError) -> JSONResponse:
    logger.exception("missing_city_mapping path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(FeatureBuilderError)
async def feature_builder_error_handler(request: Request, exc: FeatureBuilderError) -> JSONResponse:
    logger.exception("feature_builder_error path=%s", request.url.path)
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


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """V1 (legacy) health check. See /api/v2/health for the active production model."""
    predictor: AutoGuardPredictor | None = getattr(app.state, "predictor", None)
    model_loaded = predictor is not None and predictor.model is not None
    preprocessing_loaded = predictor is not None and predictor.preprocessing_loaded
    status = "ok" if (model_loaded and preprocessing_loaded) else "degraded"
    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        preprocessing_loaded=preprocessing_loaded,
        model_name=predictor.model_name if predictor else "Random Forest",
        model_version=predictor.model_version if predictor else "unavailable",
    )


@app.get("/api/v2/health")
def health_v2() -> dict[str, object]:
    """Health check for the active V2 production model (model_v2.pkl)."""
    predictor_v2: AutoGuardPredictorV2 | None = getattr(app.state, "predictor_v2", None)
    model_loaded = predictor_v2 is not None and predictor_v2.model_loaded
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "model_name": predictor_v2.model_name if predictor_v2 else "unavailable",
        "model_version": predictor_v2.model_version if predictor_v2 else "unavailable",
    }


@app.get("/api/form-contract", response_model=FormContractResponse, deprecated=True)
def form_contract() -> FormContractResponse:
    """Legacy V1 form contract. Not used by the active V2 frontend."""
    predictor: AutoGuardPredictor = app.state.predictor
    return predictor.form_contract()


@app.post("/api/predict", response_model=PredictionResponse, deprecated=True)
def predict(payload: PredictionRequest) -> PredictionResponse:
    """Legacy V1 prediction endpoint (random_forest.joblib). Kept for archive/backward compatibility."""
    predictor: AutoGuardPredictor = app.state.predictor
    return predictor.predict(payload)


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


@app.get("/api/city-options", response_model=list[str], deprecated=True)
def city_options() -> list[str]:
    """Legacy V1 city options. The V2 model does not use city/location features."""
    city_mapper: CityMapper = app.state.city_mapper
    return list(city_mapper.canonical_cities())


@app.post("/api/quick-predict", response_model=QuickPredictResponse, deprecated=True)
def quick_predict(payload: QuickPredictRequest) -> QuickPredictResponse:
    """Legacy V1 quick-predict (random_forest.joblib). Use /api/v2/quick-predict instead."""
    quick_predict_service: QuickPredictService = app.state.quick_predict_service
    result = quick_predict_service.quick_predict(
        license_plate=payload.license_plate,
        driver_age=payload.driver_age,
        policy_tenure=payload.policy_tenure,
        city=payload.city,
    )
    return QuickPredictResponse(
        vehicle=QuickPredictVehicle(
            manufacturer=result.vehicle.manufacturer,
            commercial_model=result.vehicle.commercial_model,
            production_year=result.vehicle.production_year,
        ),
        prediction=QuickPredictPrediction(
            claim_probability=result.prediction.claim_probability,
            risk_level=result.prediction.risk_level,
            recommendation=result.prediction.recommendation,
        ),
        premium_impact=QuickPredictPremiumImpact(
            direction=result.premium_impact.direction,
            min_percent=result.premium_impact.min_percent,
            max_percent=result.premium_impact.max_percent,
            estimated_percent=result.premium_impact.estimated_percent,
            summary=result.premium_impact.summary,
        ),
        top_risk_drivers=[
            QuickPredictRiskDriver(
                title=driver.title,
                direction=driver.direction,
                detail=driver.detail,
            )
            for driver in result.prediction.top_risk_drivers
        ],
        metadata=QuickPredictMetadata(
            model_version=result.prediction.model_version,
            prediction_timestamp=result.prediction.prediction_timestamp,
        ),
    )


@app.post("/api/v2/quick-predict", response_model=QuickPredictV2Response)
def quick_predict_v2(payload: QuickPredictV2Request) -> QuickPredictV2Response:
    """Active V2 quick-predict endpoint, served by model_v2.pkl."""
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
    )


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
