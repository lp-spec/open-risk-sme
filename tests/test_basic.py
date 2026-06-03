from openrisk.pipeline import run_pipeline

def test_pipeline():
    result = run_pipeline("examples/sample_input.csv")
    assert "risk_level" in result
    
