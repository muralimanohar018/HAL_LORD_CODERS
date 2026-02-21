"""
Unit tests for key cybersecurity rule behavior.
Run:
python -m unittest backend.cybersecurity.tests.test_security_rules -v
"""

from __future__ import annotations

import unittest
import warnings
from unittest.mock import patch

from backend.cybersecurity.domain_checker import get_company_verification_status
from backend.cybersecurity.email_analyzer import analyze_emails
from backend.cybersecurity.risk_aggregator import analyze_security

# Some whois backends can leak socket warnings in restricted environments.
warnings.filterwarnings("ignore", category=ResourceWarning)


class CyberSecurityRuleTests(unittest.TestCase):
    def test_personal_email_provider_warning(self) -> None:
        text = "Please send your CV to hr.recruitment.team@gmail.com for interview details."
        warnings = analyze_emails(text)
        self.assertIn("Recruiter is using a personal email domain", warnings)

    @patch(
        "backend.cybersecurity.risk_aggregator.analyze_domain_age",
        return_value="Safe: domain age appears legitimate",
    )
    def test_verified_official_domain_stays_clean(self, _mock_age: object) -> None:
        text = "Apply through official portal https://www.tcs.com/careers for the graduate role."
        result = analyze_security(text=text, company="tcs")
        self.assertEqual(result["company_verification_status"], "verified")
        self.assertEqual(result["domain_warnings"], [])
        # WHOIS network failures for verified official domains should not be penalized.
        self.assertEqual(result["whois_warnings"], [])

    @patch(
        "backend.cybersecurity.risk_aggregator.analyze_domain_age",
        return_value="Safe: domain age appears legitimate",
    )
    def test_free_hosting_domain_is_flagged(self, _mock_age: object) -> None:
        text = "Use https://tcs-careers-verify.netlify.app to complete onboarding."
        result = analyze_security(text=text, company="tcs")
        self.assertIn("Website hosted on free hosting platform", result["domain_warnings"])
        self.assertIn(
            "Website domain does not match official company domain",
            result["domain_warnings"],
        )

    @patch(
        "backend.cybersecurity.risk_aggregator.analyze_domain_age",
        return_value="Safe: domain age appears legitimate",
    )
    def test_sensitive_document_request_is_flagged(self, _mock_age: object) -> None:
        text = (
            "Quick offer letter confirmed. Share PAN card copy and Aadhaar details "
            "immediately on this email."
        )
        result = analyze_security(text=text, company="ibm")
        self.assertIn(
            "Sensitive personal/financial document request detected",
            result["behavior_warnings"],
        )
        self.assertIn(
            "Urgent or shortcut hiring language detected",
            result["behavior_warnings"],
        )
        self.assertGreaterEqual(result["security_risk_score"], 40)

    @patch(
        "backend.cybersecurity.risk_aggregator.analyze_domain_age",
        return_value="Safe: domain age appears legitimate",
    )
    def test_unknown_company_is_unverified_not_auto_fake(self, _mock_age: object) -> None:
        status = get_company_verification_status("acme labs")
        self.assertEqual(status, "unverified")

        text = "Acme Labs hiring backend interns. Apply at https://acmelabs.in/careers."
        result = analyze_security(text=text, company="acme labs")
        self.assertEqual(result["company_verification_status"], "unverified")
        # No forced fake-warning just because company isn't in whitelist.
        self.assertNotIn(
            "Website domain does not match official company domain",
            result["domain_warnings"],
        )


if __name__ == "__main__":
    unittest.main()
