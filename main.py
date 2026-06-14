import math
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

DATA_PATH = Path("data/processed/cleaned_ecg_dataset.csv")
SUBMISSIONS_PATH = Path("data/processed/user_submissions.csv")

app = FastAPI(title="ECG Dataset API", version="1.0")


@lru_cache(maxsize=1)
def load_data():
    return pd.read_csv(DATA_PATH)


def clean_nan(records):
    for row in records:
        for key, value in row.items():
            if isinstance(value, float) and math.isnan(value):
                row[key] = None
    return records


class ECGRecord(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: int = Field(..., ge=0, le=1)
    heart_rate: float
    rr_mean: float
    pr_interval: float
    qrs_duration: float
    qt_interval: float
    qtc_bazett: float
    p_axis: float
    qrs_axis: float
    t_axis: float
    p_duration: float
    abnormal_flag: Optional[int] = None
    scp_codes: Optional[str] = None


@app.get("/")
def root():
    return {"message": "ECG Dataset API", "docs": "/docs"}


@app.get("/records")
def get_records(
    min_age: int = Query(0, ge=0, le=120),
    max_age: int = Query(120, ge=0, le=120),
    min_hr: float = Query(0),
    max_hr: float = Query(500),
    abnormal: Optional[int] = Query(None, ge=0, le=1),
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    df = load_data()

    mask = df["age"].between(min_age, max_age) & df["heart_rate"].between(min_hr, max_hr)
    if abnormal is not None:
        mask &= df["abnormal_flag"] == abnormal

    filtered = df[mask]
    total = len(filtered)
    page = filtered.iloc[offset:offset + limit]
    records = clean_nan(page.to_dict(orient="records"))

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "count": len(records),
        "records": records,
    }


@app.post("/records", status_code=201)
def create_record(record: ECGRecord):
    row = record.model_dump()
    row["created_at"] = datetime.now().isoformat(timespec="seconds")

    new_row = pd.DataFrame([row])
    if SUBMISSIONS_PATH.exists():
        new_row.to_csv(SUBMISSIONS_PATH, mode="a", header=False, index=False)
    else:
        new_row.to_csv(SUBMISSIONS_PATH, index=False)

    return {"message": "record created", "record": row}


@app.get("/submissions")
def get_submissions():
    if not SUBMISSIONS_PATH.exists():
        return {"total": 0, "records": []}
    df = pd.read_csv(SUBMISSIONS_PATH)
    records = clean_nan(df.to_dict(orient="records"))
    return {"total": len(records), "records": records}
