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
        "name": "Known company official domain",
        "company": "tcs",
        "text": "Apply for internship at https://www.tcs.com/careers",
    },
    {
        "name": "Known company free-hosting impersonation",
        "company": "tcs",
        "text": "Apply now at https://tcs-careers.netlify.app",
    },
    {
        "name": "Known company personal email + suspicious link",
        "company": "infosys",
        "text": "Upload documents at https://infosys-jobs.github.io contact hr.infosys@gmail.com",
    },
    {
        "name": "Unknown startup legit-looking domain",
        "company": "Acme Labs",
        "text": "Join us at https://acmelabs.in/careers contact hiring@acmelabs.in",
    },
    {
        "name": "Unknown startup mismatched domain",
        "company": "Acme Labs",
        "text": "Acme Labs hiring: https://quick-jobs-board.com/register",
    },
    {
        "name": "Urgent fee language with free hosting",
        "company": "wipro",
        "text": "Pay 2500 fee now and confirm at https://wipro-hiring.weebly.com",
    },
    {
        "name": "MSME official domain",
        "company": "msme",
        "text": "Official update available at https://msme.gov.in",
    },
    {
        "name": "MSME fake-looking typo domain",
        "company": "msme",
        "text": "Register immediately at https://msrne-support.com",
    },
    {
        "name": "No URL with personal recruiter mail",
        "company": "ibm",
        "text": "Send your CV to ibm.recruitment.team@hotmail.com for immediate joining",
    },
    {
        "name": "No company provided, generic posting",
        "company": None,
        "text": "Internship opportunity in Chennai. Apply by sharing resume.",
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

