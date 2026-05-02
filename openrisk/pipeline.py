from openrisk.ingestion.loader import load_data
from openrisk.normalization.standardize import normalize
from openrisk.scoring.risk import compute_risk
from openrisk.reporting.generator import generate_report

def run_pipeline(file_path):
    df = load_data(file_path)
    df = normalize(df)
    metrics = compute_risk(df)
    return generate_report(metrics)
