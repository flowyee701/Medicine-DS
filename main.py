from fastapi import FastAPI
import pandas as pd
import json

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")

app = FastAPI()


@app.get("/")
def read_root():
    return 'Hello'


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/heart/{heart_rate_min}_{heart_rate_max}")
def filter_hr(heart_rate_min : int, heart_rate_max : int | None = None):
    res = data[data['heart_rate'].between(heart_rate_min, heart_rate_max)].to_json(force_ascii=False)
    return json.dumps(json.loads(res), indent=4)