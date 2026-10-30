import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    contents = await file.read()

    data_dir = Path(file.filename or "").suffix.lower()
    if data_dir != '.csv':
        logger.warning("Extension not .csv")
        raise HTTPException(status_code=400, detail="Extension not .csv")

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError,pd.errors.ParserError,UnicodeDecodeError) as error:
        logger.warning("Cannot read CSV: %s", error)
        raise HTTPException(status_code=400, detail="Cannot read the uploaded CSV")

    dataset = storage.save(df, file.filename)
    logger.info("Stored dataset: id=%s, filename=%s", dataset, file.filename)

    return DatasetInfo(
        id=dataset,
        filename=file.filename or "",
        rows=len(df),
        columns=len(df.columns),
        column_names=df.columns.tolist(),
    )

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=2, ge=1)):
    """Return up to limit rows from a stored dataset."""
    dataset = storage.get(dataset_id)

    if dataset is None:
        logger.warning("Dataset not found: %s", dataset_id)
        raise HTTPException( status_code=404, detail="Dataset not found")

    records = json.loads(dataset.head(limit).to_json(orient="records"))


    logger.info("Retrieved dataset: id=%s, returned_rows=%s",len(records), dataset_id)

    return {"id": dataset_id, "data": records, "total_rows": len(dataset)}
