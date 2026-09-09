"""
Aquora 4-Sensor Water-Quality Inference

Input order:
    pH, Turbidity_NTU, TDS_mg_L, Temperature_C

Output:
    numeric Water_Quality_Index estimate

Important:
    This model estimates the dataset's Water_Quality_Index.
    It does not contain a Safe/Unsafe or contamination threshold.
"""

import argparse
import joblib
import pandas as pd

MODEL_PATH = "aquora_water_quality_ann_4sensor.joblib"
FEATURES = ["pH", "Turbidity_NTU", "TDS_mg_L", "Temperature_C"]

def predict_wqi(pH, turbidity_ntu, tds_mg_l, temperature_c):
    model = joblib.load(MODEL_PATH)

    x = pd.DataFrame([{
        "pH": pH,
        "Turbidity_NTU": turbidity_ntu,
        "TDS_mg_L": tds_mg_l,
        "Temperature_C": temperature_c,
    }], columns=FEATURES)

    prediction = float(model.predict(x)[0])
    return prediction

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ph", type=float, required=True)
    parser.add_argument("--turbidity", type=float, required=True)
    parser.add_argument("--tds", type=float, required=True)
    parser.add_argument("--temperature", type=float, required=True)
    args = parser.parse_args()

    wqi = predict_wqi(
        args.ph,
        args.turbidity,
        args.tds,
        args.temperature
    )

    print(f"Water_Quality_Index={wqi:.6f}")
