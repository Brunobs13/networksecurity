import os
import sys

import pandas as pd
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

load_dotenv()

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

templates = Jinja2Templates(directory="./templates")


def _build_allowed_origins() -> list[str]:
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]


def _run_training_pipeline() -> None:
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        logging.info("Training pipeline execution completed.")
    except Exception as e:
        logging.exception("Training pipeline failed.")
        raise NetworkSecurityException(e, sys)


def create_app() -> FastAPI:
    app = FastAPI(title="Network Security API", version="1.0.0")

    origins = _build_allowed_origins()
    allow_credentials = "*" not in origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["authentication"])
    async def index() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    @app.get("/health", tags=["monitoring"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/train", tags=["training"])
    async def train_route(background_tasks: BackgroundTasks) -> Response:
        try:
            background_tasks.add_task(_run_training_pipeline)
            return Response("Training job accepted and running in background.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # Backward-compatible trigger for environments already calling GET /train.
    @app.get("/train", tags=["training"])
    async def train_route_get(background_tasks: BackgroundTasks) -> Response:
        return await train_route(background_tasks)

    @app.post("/predict", tags=["prediction"])
    async def predict_route(request: Request, file: UploadFile = File(...)):
        try:
            df = await run_in_threadpool(pd.read_csv, file.file)
            preprocessor = load_object("final_model/preprocessor.pkl")
            final_model = load_object("final_model/model.pkl")

            network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
            y_pred = network_model.predict(df)

            df["predicted_column"] = y_pred
            os.makedirs("prediction_output", exist_ok=True)
            df.to_csv("prediction_output/output.csv", index=False)

            table_html = df.to_html(classes="table table-striped")
            return templates.TemplateResponse(
                "table.html",
                {"request": request, "table": table_html},
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    return app


app = create_app()

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)
