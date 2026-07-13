from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="WMS AI Recommendation Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductSnapshot(BaseModel):
    product_id: int
    product_name: str | None = None
    category: str | None = None
    price: int | None = None


class LocationCandidate(BaseModel):
    location_id: int
    location_name: str | None = None
    zone: str | None = None
    same_product_stock: int = 0
    total_location_stock: int = 0
    recent_product_outbound_qty: int = 0
    recent_product_inbound_qty: int = 0
    unresolved_shortage_qty: int = 0
    unresolved_shortage_count: int = 0


class InboundLocationRequest(BaseModel):
    product: ProductSnapshot
    inbound_qty: int = Field(ge=1)
    candidates: list[LocationCandidate]


class LocationRecommendation(BaseModel):
    location_id: int
    location_name: str | None = None
    zone: str | None = None
    confidence: float
    score: float
    reason: str
    alternatives: list[dict] = []


class JsonStandardScaler:
    def __init__(self, payload):
        import numpy as np

        self.mean_ = np.array(payload["mean"], dtype=np.float32)
        self.scale_ = np.array(payload["scale"], dtype=np.float32)
        self.scale_ = np.where(self.scale_ == 0, 1.0, self.scale_)

    def transform(self, values):
        import numpy as np

        values = np.asarray(values, dtype=np.float32)
        return (values - self.mean_) / self.scale_

    def inverse_transform(self, values):
        import numpy as np

        values = np.asarray(values, dtype=np.float32)
        return (values * self.scale_) + self.mean_


class NumpyLSTMRegressor:
    def __init__(self, model_path: Path):
        import numpy as np

        with np.load(model_path) as archive:
            self.weights = {
                key: archive[key].astype(np.float32, copy=False)
                for key in archive.files
            }

        self.layer_count = sum(
            key.startswith("lstm.weight_ih_l") for key in self.weights
        )

    @staticmethod
    def _sigmoid(values):
        import numpy as np

        return 1.0 / (1.0 + np.exp(-np.clip(values, -60.0, 60.0)))

    def predict(self, sequence):
        import numpy as np

        layer_input = np.asarray(sequence, dtype=np.float32)

        for layer_index in range(self.layer_count):
            weight_ih = self.weights[f"lstm.weight_ih_l{layer_index}"]
            weight_hh = self.weights[f"lstm.weight_hh_l{layer_index}"]
            bias = (
                self.weights[f"lstm.bias_ih_l{layer_index}"]
                + self.weights[f"lstm.bias_hh_l{layer_index}"]
            )
            hidden_size = weight_hh.shape[1]
            hidden = np.zeros(hidden_size, dtype=np.float32)
            cell = np.zeros(hidden_size, dtype=np.float32)
            outputs = []

            for step in layer_input:
                gates = (weight_ih @ step) + (weight_hh @ hidden) + bias
                input_gate, forget_gate, candidate, output_gate = np.split(gates, 4)
                input_gate = self._sigmoid(input_gate)
                forget_gate = self._sigmoid(forget_gate)
                candidate = np.tanh(candidate)
                output_gate = self._sigmoid(output_gate)
                cell = (forget_gate * cell) + (input_gate * candidate)
                hidden = output_gate * np.tanh(cell)
                outputs.append(hidden)

            layer_input = np.stack(outputs)

        dense = self.weights["fc.0.weight"] @ layer_input[-1]
        dense = np.maximum(dense + self.weights["fc.0.bias"], 0)
        output = (self.weights["fc.2.weight"] @ dense) + self.weights["fc.2.bias"]
        return output.reshape(1, 1)


class InboundForecastModel:
    _bundle = None

    @classmethod
    def forecast_product(cls, product_id: int):
        bundle = cls._load_bundle()
        df = bundle["training_frame"]
        product_frame = df[df["product_id"] == product_id].sort_values("date_ts").copy()

        if product_frame.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Inbound training history for product_id {product_id} was not found.",
            )
        if len(product_frame) < bundle["window_size"]:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Product {product_id} has only {len(product_frame)} history rows. "
                    f"At least {bundle['window_size']} rows are required."
                ),
            )

        try:
            import numpy as np
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Inbound forecast dependency is not installed: {exc.name}",
            ) from exc

        features = bundle["features"]
        seq = product_frame[features].tail(bundle["window_size"]).to_numpy(dtype=np.float32)
        x_scaled = bundle["scaler_X"].transform(seq)
        pred_scaled = bundle["model"].predict(x_scaled)

        pred_qty = float(bundle["scaler_y"].inverse_transform(pred_scaled)[0][0])
        last_row = product_frame.iloc[-1]
        based_on_date = last_row["date_ts"].date()
        target_date = based_on_date + timedelta(days=1)

        basis = {
            "model": "inbound_product_lstm",
            "model_input_days": bundle["window_size"],
            "target": bundle["target"],
            "metrics": bundle["metrics"],
            "based_on_date": based_on_date.isoformat(),
            "target_date": target_date.isoformat(),
            "device": str(bundle["device"]),
            "features": {
                "current_stock_qty": float(last_row.get("current_stock_qty", 0)),
                "prev_inbound_qty": float(last_row.get("prev_inbound_qty", 0)),
                "prev_outbound_qty": float(last_row.get("prev_outbound_qty", 0)),
                "avg7_inbound_qty": float(last_row.get("avg7_inbound_qty", 0)),
                "avg7_outbound_qty": float(last_row.get("avg7_outbound_qty", 0)),
                "avg7_shortage_qty": float(last_row.get("avg7_shortage_qty", 0)),
                "shortage_qty": float(last_row.get("shortage_qty", 0)),
                "shortage_count": float(last_row.get("shortage_count", 0)),
            },
            "notes": [
                "Prediction uses the trained inbound LSTM model for the selected product.",
                "The input sequence is built from the latest product-level inbound, outbound, stock, and shortage history.",
            ],
        }

        return {
            "product_id": product_id,
            "predicted_qty": max(0, int(np.rint(pred_qty))),
            "predicted_qty_raw": pred_qty,
            "target_date": target_date.isoformat(),
            "based_on_date": based_on_date.isoformat(),
            "device": str(bundle["device"]),
            "basis": basis,
        }

    @classmethod
    def _load_bundle(cls):
        if cls._bundle is not None:
            return cls._bundle

        try:
            import json
            import pandas as pd
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Inbound forecast dependency is not installed: {exc.name}",
            ) from exc

        backend_root = Path(__file__).resolve().parent
        model_dir = backend_root / "ml" / "inbound_forecast"
        metadata_path = model_dir / "metadata.json"
        model_path = model_dir / "model.npz"
        scaler_x_path = model_dir / "scaler_X.json"
        scaler_y_path = model_dir / "scaler_y.json"
        training_frame_path = model_dir / "training_frame.csv"

        missing = [
            str(path)
            for path in (metadata_path, model_path, scaler_x_path, scaler_y_path, training_frame_path)
            if not path.exists()
        ]
        if missing:
            raise HTTPException(
                status_code=503,
                detail=f"Inbound forecast artifact is missing: {', '.join(missing)}",
            )

        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)
        with scaler_x_path.open("r", encoding="utf-8") as file:
            scaler_x_payload = json.load(file)
        with scaler_y_path.open("r", encoding="utf-8") as file:
            scaler_y_payload = json.load(file)

        model = NumpyLSTMRegressor(model_path)

        training_frame = pd.read_csv(training_frame_path)
        if "date_ts" in training_frame.columns:
            training_frame["date_ts"] = pd.to_datetime(training_frame["date_ts"])
        else:
            training_frame["date_ts"] = pd.to_datetime(training_frame["date"])

        missing_features = [
            feature for feature in metadata["features"] if feature not in training_frame.columns
        ]
        if missing_features:
            raise HTTPException(
                status_code=422,
                detail=f"Inbound training frame is missing features: {', '.join(missing_features)}",
            )

        cls._bundle = {
            "features": metadata["features"],
            "window_size": int(metadata["window_size"]),
            "target": metadata.get("target", "next_day_inbound_qty"),
            "metrics": metadata.get("metrics", {}),
            "device": "cpu",
            "model": model,
            "scaler_X": JsonStandardScaler(scaler_x_payload),
            "scaler_y": JsonStandardScaler(scaler_y_payload),
            "training_frame": training_frame,
        }
        return cls._bundle


class OutboundForecastModel:
    _bundle = None

    @classmethod
    def forecast_today(cls):
        bundle = cls._load_bundle()
        df = cls._load_feature_frame(bundle["features"])
        target_date = date.today()
        based_on_date = df["date"].max().date()
        prediction_frame = cls._build_prediction_frame(
            df,
            bundle["features"],
            bundle["window_size"],
            target_date,
        )

        try:
            import numpy as np
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Forecast dependency is not installed: {exc.name}",
            ) from exc

        x_scaled = bundle["scaler_X"].transform(prediction_frame[bundle["features"]])
        pred_scaled = bundle["model"].predict(x_scaled)

        pred_qty = float(bundle["scaler_y"].inverse_transform(pred_scaled)[0][0])
        last_row = df.iloc[-1]
        basis = {
            "model": "outbound_daily_lstm",
            "model_input_days": bundle["window_size"],
            "target_date": target_date.isoformat(),
            "based_on_date": based_on_date.isoformat(),
            "device": str(bundle["device"]),
            "features": {
                "weekday_num": int(target_date.weekday()),
                "month": int(target_date.month),
                "day": int(target_date.day),
                "is_weekend": 1 if target_date.weekday() >= 5 else 0,
                "is_holiday": int(prediction_frame.iloc[-1].get("is_holiday", 0)),
                "event": int(prediction_frame.iloc[-1].get("event", 0)),
                "promo": int(prediction_frame.iloc[-1].get("promo", 0)),
                "prev_qty": float(prediction_frame.iloc[-1].get("prev_qty", 0)),
                "avg7_qty": float(prediction_frame.iloc[-1].get("avg7_qty", 0)),
                "top_sku_ratio": float(prediction_frame.iloc[-1].get("top_sku_ratio", 0)),
                "heavy_item_ratio": float(prediction_frame.iloc[-1].get("heavy_item_ratio", 0)),
                "cold_chain_ratio": float(prediction_frame.iloc[-1].get("cold_chain_ratio", 0)),
            },
            "source": {
                "last_recorded_outbound_qty": int(last_row.get("outbound_qty", 0)),
                "last_recorded_date": based_on_date.isoformat(),
            },
            "notes": [
                "Prediction uses the saved LSTM model and the latest available outbound feature history.",
                "Calendar values are generated for today; rolling/category ratios are carried from recent history.",
            ],
        }

        return {
            "predicted_qty": max(0, int(np.rint(pred_qty))),
            "predicted_qty_raw": pred_qty,
            "target_date": target_date.isoformat(),
            "based_on_date": based_on_date.isoformat(),
            "device": str(bundle["device"]),
            "basis": basis,
        }

    @classmethod
    def _load_bundle(cls):
        if cls._bundle is not None:
            return cls._bundle

        try:
            import json
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Forecast dependency is not installed: {exc.name}",
            ) from exc

        backend_root = Path(__file__).resolve().parent
        model_dir = backend_root / "ml" / "outbound_forecast"
        metadata_path = model_dir / "metadata.json"
        model_path = model_dir / "model.npz"
        scaler_x_path = model_dir / "scaler_X.json"
        scaler_y_path = model_dir / "scaler_y.json"

        missing = [
            str(path)
            for path in (metadata_path, model_path, scaler_x_path, scaler_y_path)
            if not path.exists()
        ]
        if missing:
            raise HTTPException(
                status_code=503,
                detail=f"Forecast artifact is missing: {', '.join(missing)}",
            )

        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)
        with scaler_x_path.open("r", encoding="utf-8") as file:
            scaler_x_payload = json.load(file)
        with scaler_y_path.open("r", encoding="utf-8") as file:
            scaler_y_payload = json.load(file)

        cls._bundle = {
            "features": metadata["features"],
            "window_size": int(metadata["window_size"]),
            "device": "cpu",
            "model": NumpyLSTMRegressor(model_path),
            "scaler_X": JsonStandardScaler(scaler_x_payload),
            "scaler_y": JsonStandardScaler(scaler_y_payload),
        }
        return cls._bundle

    @staticmethod
    def _load_feature_frame(features):
        try:
            import pandas as pd
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Forecast dependency is not installed: {exc.name}",
            ) from exc

        backend_root = Path(__file__).resolve().parent
        project_root = backend_root.parent
        candidates = [
            project_root / "korean_ecommerce_outbound_2022_2025_with_categories.csv",
            backend_root / "data" / "korean_ecommerce_outbound_2022_2025_with_categories.csv",
        ]
        data_path = next((path for path in candidates if path.exists()), None)
        if data_path is None:
            raise HTTPException(status_code=503, detail="Forecast source CSV was not found.")

        df = pd.read_csv(data_path)
        if "date" not in df.columns:
            raise HTTPException(status_code=422, detail="Forecast source CSV must include a date column.")

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        if "weekday_num" in features and "weekday_num" not in df.columns:
            df["weekday_num"] = df["date"].dt.weekday
        if "month" in features and "month" not in df.columns:
            df["month"] = df["date"].dt.month
        if "day" in features and "day" not in df.columns:
            df["day"] = df["date"].dt.day

        missing_features = [feature for feature in features if feature not in df.columns]
        if missing_features:
            raise HTTPException(
                status_code=422,
                detail=f"Forecast source CSV is missing features: {', '.join(missing_features)}",
            )

        return df

    @staticmethod
    def _build_prediction_frame(df, features, window_size, target_date):
        if len(df) < window_size:
            raise HTTPException(
                status_code=422,
                detail=f"At least {window_size} feature rows are required for forecasting.",
            )

        import pandas as pd

        frame = df.tail(window_size).copy()
        if target_date <= df["date"].max().date():
            frame = df[df["date"].dt.date <= target_date].tail(window_size).copy()
            if len(frame) == window_size:
                return frame

        last = df.iloc[-1].copy()
        forecast_row = last.copy()
        forecast_row["date"] = pd.Timestamp(target_date)
        forecast_row["weekday_num"] = target_date.weekday()
        forecast_row["month"] = target_date.month
        forecast_row["day"] = target_date.day
        forecast_row["is_weekend"] = 1 if target_date.weekday() >= 5 else 0
        forecast_row["is_holiday"] = 0
        forecast_row["event"] = 0
        forecast_row["promo"] = 0
        forecast_row["prev_qty"] = last.get("outbound_qty", last.get("prev_qty", 0))

        return pd.concat([df.tail(window_size - 1), forecast_row.to_frame().T], ignore_index=True)


def score_candidate(candidate: LocationCandidate):
    score = 0.0
    reasons = []

    if candidate.same_product_stock > 0:
        score += 40.0
        reasons.append("same product already stocked")

    if candidate.unresolved_shortage_qty > 0:
        shortage_score = min(35.0, candidate.unresolved_shortage_qty * 1.5)
        score += shortage_score
        reasons.append("unresolved shortage exists")

    if candidate.unresolved_shortage_count > 0:
        score += min(10.0, candidate.unresolved_shortage_count * 2.5)

    if candidate.recent_product_outbound_qty > 0:
        outbound_score = min(25.0, candidate.recent_product_outbound_qty * 0.25)
        score += outbound_score
        reasons.append("recent outbound demand")

    if candidate.recent_product_inbound_qty > 0:
        score += min(8.0, candidate.recent_product_inbound_qty * 0.05)

    stock_penalty = min(25.0, candidate.total_location_stock * 0.03)
    score -= stock_penalty
    if stock_penalty >= 8:
        reasons.append("location stock is relatively high")

    if not reasons:
        reasons.append("lowest-risk available location")

    return round(score, 4), ", ".join(reasons)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/forecast/outbound/today")
async def forecast_outbound_today():
    return OutboundForecastModel.forecast_today()


@app.get("/forecast/inbound")
async def forecast_inbound(product_id: int):
    return InboundForecastModel.forecast_product(product_id)


def recommend_location(request: InboundLocationRequest):
    if not request.candidates:
        raise HTTPException(status_code=422, detail="No candidate locations were supplied.")

    scored = []
    for candidate in request.candidates:
        score, reason = score_candidate(candidate)
        scored.append(
            {
                "location_id": candidate.location_id,
                "location_name": candidate.location_name,
                "zone": candidate.zone,
                "score": score,
                "reason": reason,
            }
        )

    scored.sort(key=lambda item: (-item["score"], item["location_id"]))
    best = scored[0]
    top_score = best["score"]
    second_score = scored[1]["score"] if len(scored) > 1 else top_score - 10
    confidence = max(0.5, min(0.99, 0.65 + ((top_score - second_score) / 100)))

    return {
        **best,
        "confidence": round(confidence, 2),
        "alternatives": scored[1:4],
    }


@app.post("/recommend/inbound-location", response_model=LocationRecommendation)
async def recommend_inbound_location(request: InboundLocationRequest):
    return recommend_location(request)
