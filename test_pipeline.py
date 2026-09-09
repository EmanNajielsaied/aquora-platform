import json
import joblib
import pandas as pd
import numpy as np

def run_tests():
    print("==================================================")
    print("POWERGUARD PIPELINE AUTOMATED VERIFICATION")
    print("==================================================")

    # 1. Load Schema & Thresholds
    with open("input_schema.json", "r") as f:
        schema = json.load(f)
    with open("thresholds.json", "r") as f:
        thresholds = json.load(f)

    all_features = schema["features"]
    cat_features = schema["categorical_features"]
    cat_values = schema["categorical_values"]
    xgb_threshold = thresholds["XGBoost"]

    print(f"✓ Total features in schema: {len(all_features)} (Numeric: {len(schema['numeric_features'])}, Categorical: {len(cat_features)})")
    print(f"✓ XGBoost Threshold: {xgb_threshold}")

    assert len(all_features) == 54, f"Expected 54 features, got {len(all_features)}"
    assert len(cat_features) == 5, f"Expected 5 categorical features, got {len(cat_features)}"
    assert xgb_threshold == 0.65, f"Expected 0.65 threshold, got {xgb_threshold}"

    # 2. Load Model Artifacts
    preprocessor = joblib.load("preprocessor.pkl")
    model = joblib.load("xgboost_model.pkl")

    print(f"✓ Preprocessor loaded: {type(preprocessor).__name__}")
    print(f"✓ XGBoost model loaded: {type(model).__name__}")

    # 3. Create Sample 1-row DataFrame matching schema
    sample = {}
    for feat in all_features:
        if feat in cat_features:
            sample[feat] = cat_values[feat][0]
        else:
            sample[feat] = 0.0

    df_in = pd.DataFrame([sample])[all_features]
    print(f"✓ Input DataFrame created with shape: {df_in.shape}")

    # 4. Transform via preprocessor
    X_trans = preprocessor.transform(df_in)
    print(f"✓ Transformed data shape: {X_trans.shape}")

    assert X_trans.shape == (1, 71), f"Expected shape (1, 71), got {X_trans.shape}"
    print("✓ VERIFIED: Preprocessor correctly maps 54 raw features -> 71 transformed features!")

    # 5. Execute XGBoost Prediction
    probs = model.predict_proba(X_trans)
    failure_prob = float(probs[0][1])
    is_failure = failure_prob >= xgb_threshold

    print(f"✓ Sample Prediction Probabilities: Class 0: {probs[0][0]:.4f}, Class 1 (Failure): {failure_prob:.4f}")
    print(f"✓ Threshold Comparison ({xgb_threshold}): Result = {'FAILURE EXPECTED' if is_failure else 'NORMAL OPERATION'}")

    print("\n==================================================")
    print("ALL PIPELINE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
