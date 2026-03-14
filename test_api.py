#!/usr/bin/env python3
"""
Quick test script for InterviewPrepAI API.
Run with: python test_api.py
"""
import sys

try:
    import requests
except ImportError:
    print("Run: pip install requests")
    sys.exit(1)

BASE = "http://127.0.0.1:8000"

def main():
    # 1. Health check
    print("1. Testing /health...")
    r = requests.get(f"{BASE}/health", timeout=10)
    r.raise_for_status()
    print(f"   OK: {r.json()}")

    # 2. Generate study guide (JSON only, no PDF)
    print("\n2. Testing POST /generate-study-guide (may take 1–2 min)...")
    payload = {"role": "Data Scientist", "years_experience": 2.5}
    r = requests.post(
        f"{BASE}/generate-study-guide",
        params={"include_pdf": False},
        json=payload,
        timeout=180,
    )
    r.raise_for_status()
    data = r.json()
    doc = data.get("document", {})
    print(f"   OK: Status {r.status_code}")
    print(f"   Overview: {doc.get('study_guide', {}).get('overview', {}).get('user_profile_summary', 'N/A')[:80]}...")
    print(f"   Topics: {len(doc.get('study_guide', {}).get('topic_deep_dives', []))}")

    # 3. Download PDF
    print("\n3. Testing POST /download-study-guide-pdf...")
    r = requests.post(
        f"{BASE}/download-study-guide-pdf",
        json=payload,
        timeout=180,
    )
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
        out_path = "study_guide_test.pdf"
        with open(out_path, "wb") as f:
            f.write(r.content)
        print(f"   OK: PDF saved to {out_path} ({len(r.content):,} bytes)")
    else:
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")

    print("\nDone.")

if __name__ == "__main__":
    main()
