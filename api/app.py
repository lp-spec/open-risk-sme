from fastapi import FastAPI, UploadFile
import pandas as pd
from openrisk.pipeline import run_pipeline

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile):
    df = pd.read_csv(file.file)
    df = df.rename(columns=str.lower)
    result = run_pipeline(df)
    return result
