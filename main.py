from openrisk.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline("examples/sample_input.csv")
    print(result)
