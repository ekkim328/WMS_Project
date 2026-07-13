"""Export trained PyTorch models and sklearn scalers for lightweight inference."""

import json
from pathlib import Path

import joblib
import numpy as np
import torch


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def export_model(model_dir: Path) -> None:
    state_dict = torch.load(model_dir / "model.pt", map_location="cpu")
    weights = {
        key: tensor.detach().cpu().numpy().astype(np.float32)
        for key, tensor in state_dict.items()
    }
    np.savez_compressed(model_dir / "model.npz", **weights)


def export_scaler(source: Path, destination: Path) -> None:
    scaler = joblib.load(source)
    destination.write_text(
        json.dumps(
            {
                "mean": np.asarray(scaler.mean_, dtype=float).tolist(),
                "scale": np.asarray(scaler.scale_, dtype=float).tolist(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    inbound_dir = BACKEND_ROOT / "ml" / "inbound_forecast"
    outbound_dir = BACKEND_ROOT / "ml" / "outbound_forecast"

    export_model(inbound_dir)
    export_model(outbound_dir)
    export_scaler(outbound_dir / "scaler_X.pkl", outbound_dir / "scaler_X.json")
    export_scaler(outbound_dir / "scaler_y.pkl", outbound_dir / "scaler_y.json")


if __name__ == "__main__":
    main()
