from pathlib import Path
from typing import Any

import pandas as pd


def load_csv(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def save_csv(df: pd.DataFrame, path: str | Path, **kwargs: Any) -> None:
    df.to_csv(path, index=False, **kwargs)


def read_uploaded_file(uploaded_file: Any) -> pd.DataFrame | None:
    name = getattr(uploaded_file, "name", "").lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        if name.endswith((".xls", ".xlsx")):
            return pd.read_excel(uploaded_file)
    except Exception:
        return None
    return None
