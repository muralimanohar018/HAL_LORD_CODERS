"""
Manual test cases for CampusShield cybersecurity + ML integration.
Run:
python backend/cybersecurity/test_cases.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make backend package importable when executed as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from cybersecurity.campusshield_engine import analyze_message


TEST_CASES = [
    {
        "name": "TCS official careers page",
        "company": "tcs",
        "text": (
            "TCS is hiring graduate trainees for 2026. "
            "Apply through https://www.tcs.com/careers and use your college email."
        ),
    },
    {
        "name": "TCS impersonation on free hosting",
        "company": "tcs",
        "text": (
            "Final shortlist released. Upload Aadhaar and pay onboarding fee today at "
            "https://tcs-careers-verify.netlify.app."
        ),
    },
    {
        "name": "Infosys impersonation + personal recruiter email",
        "company": "infosys",
        "text": (
            "Infosys HR team: complete verification immediately at https://infosys-jobs.github.io "
            "and send screenshot to hr.infosys@outlook.com."
        ),
    },
    {
        "name": "Unknown startup with brand-matching domain",
        "company": "Acme Labs",
        "text": (
            "Acme Labs is hiring backend interns in Bengaluru. "
            "Apply at https://acmelabs.in/careers or contact hiring@acmelabs.in."
        ),
    },
    {
        "name": "Unknown startup routed to unrelated job board",
        "company": "Acme Labs",
        "text": (
            "Acme Labs immediate joining. Confirm interest here: "
            "https://quick-jobs-board.com/register-now."
        ),
    },
    {
        "name": "Wipro training-fee scam pattern",
        "company": "wipro",
        "text": (
            "Wipro selected candidates must pay Rs 2500 for mandatory training kit by 6 PM. "
            "Submit payment proof at https://wipro-hiring.weebly.com."
        ),
    },
    {
        "name": "MSME official government portal",
        "company": "msme",
        "text": (
            "For MSME scheme circulars and announcements, check the official portal "
            "https://msme.gov.in."
        ),
    },
    {
        "name": "MSME typo-domain phishing attempt",
        "company": "msme",
        "text": (
            "Complete urgent MSME subsidy registration in 30 minutes at "
            "https://msrne-support.com to avoid cancellation."
        ),
    },
    {
        "name": "IBM role shared only via personal email",
        "company": "ibm",
        "text": (
            "IBM project opening in Hyderabad. Share resume and PAN card copy to "
            "ibm.recruitment.team@hotmail.com for quick offer letter."
        ),
    },
    {
        "name": "Generic campus internship message",
        "company": None,
        "text": (
            "Software internship opportunity in Chennai for final-year students. "
            "Send resume to official placement cell for screening."
        ),
    },
    {
        "name": "Capgemini spoofed sub-brand domain",
        "company": "capgemini",
        "text": (
            "Capgemini onboarding portal is live. Verify account at "
            "https://capgemini-careers-offer.github.io/login."
        ),
    },
    {
        "name": "Accenture official domain with corporate email",
        "company": "accenture",
        "text": (
            "Accenture referral drive for 2026 batch. Details at https://www.accenture.com/in-en/careers "
            "and queries to recruiter@accenture.com."
        ),
    },
]


def run_tests() -> None:
    for idx, case in enumerate(TEST_CASES, start=1):
        result = analyze_message(text=case["text"], company=case["company"])
        print(f"\n[{idx}] {case['name']}")
        print(f"Company: {case['company']}")
        print(f"Input: {case['text']}")
        print("Output:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_tests()
