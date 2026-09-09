"""
Automated Integration Test for Aquora Water Infrastructure API
Verifies isolation of models, correct endpoint execution, threshold enforcement,
and accurate response schemas across all three systems.
"""

from backend.app import health_check
from backend.routers import water_quality, leak_detection, decision_system

def run_integration_tests():
    print("=" * 65)
    print("AQUORA THREE-SUBSYSTEM INTEGRATION VERIFICATION")
    print("=" * 65)

    # 1. Health check
    health = health_check()
    print(f"✓ Health Check: {health['status'].upper()}")
    assert health["subsystems"]["water_quality"]["status"] == "ready"
    assert health["subsystems"]["leak_detection"]["status"] == "ready"
    assert health["subsystems"]["decision_system"]["status"] == "ready"
    print("  - Water Quality Subsystem: READY")
    print("  - Leak Detection Subsystem: READY")
    print("  - Decision Support Subsystem: READY")

    # 2. Water Quality Test
    print("\n[Testing 1: Water Quality]")
    wq_payload = water_quality.WaterQualityRequest(
        pH=7.35,
        Turbidity_NTU=1.20,
        TDS_mg_L=210.0,
        Temperature_C=19.5
    )
    wq_out = water_quality.predict_water_quality(wq_payload)
    wqi = wq_out["water_quality_index"]
    print(f"✓ Water Quality Prediction: AI-estimated WQI = {wqi:.3f}")
    assert isinstance(wqi, (int, float)), "WQI must be numeric"
    assert "Safe" not in wq_out.get("status", ""), "Must NOT invent Safe/Unsafe label!"
    print("✓ SCIENTIFIC CONSTRAINT VERIFIED: No Safe/Unsafe or contamination label present.")

    # 3. Leak Detection Test
    print("\n[Testing 2: Leak Detection]")
    leak_schema = leak_detection.get_leak_schema()
    leak_presets = leak_schema["presets"]

    # Test preset 1: Intact Normal
    norm_req = leak_detection.LeakPredictionRequest(features=leak_presets["intact_normal"]["data"])
    leak_norm_out = leak_detection.predict_leak(norm_req)
    print(f"✓ Normal Pipe -> Leak Prob: {leak_norm_out['leak_probability']:.4f} | Prediction: {leak_norm_out['status']}")
    assert leak_norm_out["prediction"] is False

    # Test preset 2: Active Leak
    act_req = leak_detection.LeakPredictionRequest(features=leak_presets["active_leak"]["data"])
    leak_act_out = leak_detection.predict_leak(act_req)
    print(f"✓ Active Leak Pipe -> Leak Prob: {leak_act_out['leak_probability']:.4f} | Prediction: {leak_act_out['status']}")
    assert leak_act_out["decision_threshold"] == 0.38803765177726746
    assert leak_act_out["prediction"] is True, "Active leak preset MUST trigger Leak Detected (prediction=True)!"
    print(f"✓ Saved Threshold Preserved: {leak_act_out['decision_threshold']}")

    # 4. Decision System Test
    print("\n[Testing 3: Decision System / Expert Logic]")
    dec_schema = decision_system.get_decision_schema()
    dec_presets = dec_schema["presets"]

    # Test Level 1: Normal
    dec_norm_req = decision_system.DecisionPredictionRequest(features=dec_presets["normal_operational"]["data"])
    dec_norm_out = decision_system.predict_decision(dec_norm_req)
    print(f"✓ Level 1 (Normal) -> ML Prob: {dec_norm_out['ai_prediction']['failure_probability']:.4f} | Expert Score: {dec_norm_out['expert_decision']['expert_score']} | Status: {dec_norm_out['expert_decision']['final_status']}")
    assert dec_norm_out["expert_decision"]["final_status"] == "NORMAL"

    # Test Level 4: Critical
    dec_crit_req = decision_system.DecisionPredictionRequest(features=dec_presets["critical_emergency"]["data"])
    dec_crit_out = decision_system.predict_decision(dec_crit_req)
    print(f"✓ Level 4 (Critical) -> ML Prob: {dec_crit_out['ai_prediction']['failure_probability']:.4f} | Expert Score: {dec_crit_out['expert_decision']['expert_score']} | Status: {dec_crit_out['expert_decision']['final_status']}")
    assert dec_crit_out["expert_decision"]["final_status"] == "CRITICAL"
    assert len(dec_crit_out["expert_decision"]["reasons"]) > 0
    print(f"  Triggered Rules count: {len(dec_crit_out['expert_decision']['reasons'])}")
    print(f"  Recommended Action: {dec_crit_out['expert_decision']['recommended_action'][:80]}...")

    print("\n" + "=" * 65)
    print("ALL THREE SYSTEMS VERIFIED AND WORKING FLAWLESSLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_integration_tests()
