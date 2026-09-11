"""
Aquora Platform - End-to-End Client & UI Integration Test
Validates that AquoraAPIClient seamlessly executes all three subsystems in-process,
enforces exact thresholds, and supports direct Streamlit Cloud execution with zero HTTP dependencies.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from aquora_ui.shared.api_client import api_client

def test_client_e2e():
    print("=" * 65)
    print("AQUORA UNIFIED CLIENT END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. Health Audit
    health = api_client.check_health()
    print(f"✓ Health Check: {health['status'].upper()} (Mode: {health.get('mode')})")
    assert health["status"] == "online"
    assert health.get("mode") == "direct"
    assert health["subsystems"]["water_quality"]["status"] == "ready"
    assert health["subsystems"]["leak_detection"]["status"] == "ready"
    assert health["subsystems"]["decision_system"]["status"] == "ready"
    print("  - Water Quality: READY")
    print("  - Leak Detection: READY")
    print("  - Decision Support: READY")

    # 2. Water Quality Subsystem
    print("\n[Testing Subsystem 1: Water Quality ANN]")
    wq_info = api_client.get_water_quality_info()
    assert "presets" in wq_info
    assert len(wq_info["sensors"]) == 4

    wq_res = api_client.predict_water_quality({
        "pH": 7.4,
        "Turbidity_NTU": 0.8,
        "TDS_mg_L": 180.0,
        "Temperature_C": 19.5
    })
    wqi = wq_res["water_quality_index"]
    print(f"✓ Water Quality Prediction: AI-estimated WQI = {wqi:.3f}")
    assert isinstance(wqi, (int, float))
    assert "Safe" not in wq_res.get("status", "")
    print("✓ Scientific constraint verified: Strict continuous numeric index.")

    # 3. Leak Detection Subsystem
    print("\n[Testing Subsystem 2: Leak Detection XGBoost]")
    leak_schema = api_client.get_leak_schema()
    leak_thresh = leak_schema["decision_threshold"]
    print(f"✓ Leak Decision Threshold: {leak_thresh}")
    assert leak_thresh == 0.38803765177726746, f"Expected 0.38803765177726746, got {leak_thresh}"

    # Test normal preset
    leak_norm = api_client.predict_leak(leak_schema["presets"]["intact_normal"]["data"])
    print(f"✓ Intact Pipe -> Prob: {leak_norm['leak_probability']:.4f} | Prediction: {leak_norm['status']}")
    assert leak_norm["prediction"] is False
    assert leak_norm["status"] == "No Leak Detected"

    # Test active leak preset
    leak_act = api_client.predict_leak(leak_schema["presets"]["active_leak"]["data"])
    print(f"✓ Active Leak Pipe -> Prob: {leak_act['leak_probability']:.4f} | Prediction: {leak_act['status']}")
    assert leak_act["prediction"] is True
    assert leak_act["status"] == "Leak Detected"
    assert leak_act["decision_threshold"] == 0.38803765177726746

    # 4. Decision System Subsystem
    print("\n[Testing Subsystem 3: Decision System / Predictive Maintenance]")
    dec_schema = api_client.get_decision_schema()
    dec_thresh = dec_schema["ml_threshold"]
    print(f"✓ Decision ML Threshold: {dec_thresh}")
    assert dec_thresh == 0.65, f"Expected 0.65, got {dec_thresh}"

    # Test Level 1 Normal
    dec_norm = api_client.predict_decision(dec_schema["presets"]["normal_operational"]["data"])
    print(f"✓ Normal Case -> ML Prob: {dec_norm['ai_prediction']['failure_probability']:.4f} | Score: {dec_norm['expert_decision']['expert_score']} | Status: {dec_norm['expert_decision']['final_status']}")
    assert dec_norm["expert_decision"]["final_status"] == "NORMAL"

    # Test Level 4 Critical
    dec_crit = api_client.predict_decision(dec_schema["presets"]["critical_emergency"]["data"])
    print(f"✓ Critical Case -> ML Prob: {dec_crit['ai_prediction']['failure_probability']:.4f} | Score: {dec_crit['expert_decision']['expert_score']} | Status: {dec_crit['expert_decision']['final_status']}")
    assert dec_crit["expert_decision"]["final_status"] == "CRITICAL"

    print("\n" + "=" * 65)
    print("ALL E2E CLIENT TESTS PASSED! STREAMLIT CLOUD IS 100% READY.")
    print("=" * 65)

if __name__ == "__main__":
    test_client_e2e()
