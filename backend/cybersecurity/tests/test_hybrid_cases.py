"""
Integration-style hybrid risk test cases.
Run:
python -m unittest backend.cybersecurity.tests.test_hybrid_cases -v
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.cybersecurity.campusshield_engine import analyze_message


class HybridCaseTests(unittest.TestCase):
    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.10)
    def test_official_company_message_low_risk(self, _mock_ml: object, _mock_age: object) -> None:
        text = (
            "TCS is hiring graduate trainees. Apply through https://www.tcs.com/careers "
            "using your college email."
        )
        result = analyze_message(text, company="tcs")
        self.assertEqual(result["final_risk_level"], "LOW")
        self.assertEqual(result["security"]["security_risk_score"], 0)

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.10)
    def test_impersonation_with_fee_and_aadhaar_high_risk(
        self, _mock_ml: object, _mock_age: object
    ) -> None:
        text = (
            "Final shortlist. Upload Aadhaar and pay onboarding fee today at "
            "https://tcs-careers-verify.netlify.app."
        )
        result = analyze_message(text, company="tcs")
        self.assertEqual(result["final_risk_level"], "HIGH")
        self.assertGreaterEqual(result["security"]["security_risk_score"], 60)

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.10)
    def test_unknown_startup_legit_domain_low_risk(self, _mock_ml: object, _mock_age: object) -> None:
        text = "Acme Labs is hiring interns. Apply at https://acmelabs.in/careers."
        result = analyze_message(text, company="Acme Labs")
        self.assertEqual(result["security"]["company_verification_status"], "unverified")
        self.assertEqual(result["final_risk_level"], "LOW")

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.10)
    def test_unknown_startup_mismatch_medium_risk(self, _mock_ml: object, _mock_age: object) -> None:
        text = "Acme Labs immediate joining. Confirm here: https://quick-jobs-board.com/register"
        result = analyze_message(text, company="Acme Labs")
        self.assertEqual(result["final_risk_level"], "MEDIUM")
        self.assertGreaterEqual(result["security"]["security_risk_score"], 30)

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.10)
    def test_personal_email_plus_sensitive_docs_high_risk(
        self, _mock_ml: object, _mock_age: object
    ) -> None:
        text = (
            "IBM opening. Share PAN card copy to ibm.recruitment.team@hotmail.com "
            "for quick offer letter."
        )
        result = analyze_message(text, company="ibm")
        self.assertEqual(result["final_risk_level"], "HIGH")
        self.assertIn(
            "Recruiter is using a personal email domain",
            result["security"]["email_warnings"],
        )

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.90)
    def test_ml_only_high_risk(self, _mock_ml: object, _mock_age: object) -> None:
        text = "Campus internship notice with no links and no suspicious behavior."
        result = analyze_message(text, company=None)
        self.assertEqual(result["security"]["security_risk_score"], 0)
        self.assertEqual(result["final_risk_level"], "HIGH")

    @patch("backend.cybersecurity.risk_aggregator.analyze_domain_age", return_value="Safe: domain age appears legitimate")
    @patch("backend.cybersecurity.campusshield_engine.predict_scam", return_value=0.70)
    def test_ml_only_medium_risk(self, _mock_ml: object, _mock_age: object) -> None:
        text = "General hiring update with no links."
        result = analyze_message(text, company=None)
        self.assertEqual(result["security"]["security_risk_score"], 0)
        self.assertEqual(result["final_risk_level"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()

