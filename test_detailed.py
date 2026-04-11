#!/usr/bin/env python3
"""Test script for Corti fact extraction endpoint."""

from corti_client import CortiClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

print("=" * 70)
print("🔬 CORTI FACT EXTRACTION TEST")
print("=" * 70)

# Initialize client
client = CortiClient()

# Step 1: Authenticate
print("\n1️⃣  Authenticating...")
try:
    token = client.authenticate()
    print(f"   ✅ Token obtained: {token[:40]}...")

    # Decode JWT to see claims (without verifying signature)
    import base64
    parts = token.split('.')
    if len(parts) >= 2:
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        claims = json.loads(decoded)
        print(f"\n   📋 Token Claims:")
        print(f"      - Issuer: {claims.get('iss', 'N/A')}")
        print(f"      - Subject: {claims.get('sub', 'N/A')}")
        print(f"      - Audience: {claims.get('aud', 'N/A')}")
        print(f"      - Client ID: {claims.get('client_id', 'N/A')}")

except Exception as e:
    print(f"   ❌ Authentication failed: {e}")
    exit(1)

# Step 2: Load the orthopedic referral letter
print("\n2️⃣  Loading medical text...")
try:
    letter_path = os.path.join(os.path.dirname(__file__), "Sample", "Orthopedic Referral Letter.txt")
    with open(letter_path, 'r') as f:
        medical_text = f.read()

    # Show preview
    preview = medical_text[:200].replace('\n', ' ')
    print(f"   ✅ Loaded {len(medical_text)} characters")
    print(f"   📄 Preview: {preview}...")

except Exception as e:
    print(f"   ❌ Failed to load letter: {e}")
    exit(1)

# Step 3: Extract facts
print("\n3️⃣  Calling fact extraction API...")
print(f"   🌐 Endpoint: {client.api_url}/facts/extract")

try:
    response = client.extract_facts(medical_text, output_language="en-US")

    print(f"   ✅ API call successful!")

    # Display results
    print("\n" + "=" * 70)
    print("📊 EXTRACTION RESULTS")
    print("=" * 70)

    # Credits consumed
    if 'usageInfo' in response:
        credits = response['usageInfo'].get('creditsConsumed', 'N/A')
        print(f"\n💰 Credits Consumed: {credits}")

    # Extracted facts
    if 'facts' in response:
        facts = response['facts']
        print(f"\n📋 Extracted Facts ({len(facts)} total):\n")

        for i, fact in enumerate(facts, 1):
            print(f"   {i}. {fact}")
            if i >= 20:  # Limit display to first 20 facts
                remaining = len(facts) - 20
                if remaining > 0:
                    print(f"   ... and {remaining} more facts")
                break
    else:
        print("\n⚠️  No 'facts' field in response")

    # Full response (for debugging)
    print("\n" + "=" * 70)
    print("🔧 RAW API RESPONSE")
    print("=" * 70)
    print(json.dumps(response, indent=2))

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)

except Exception as e:
    print(f"   ❌ Fact extraction failed!")
    print(f"\n   Error Type: {type(e).__name__}")
    print(f"   Error Message: {str(e)}")

    # Try to get more details from the response
    if hasattr(e, 'response'):
        print(f"\n   HTTP Status: {e.response.status_code}")
        print(f"   Response Headers: {dict(e.response.headers)}")
        print(f"\n   Response Body:")
        try:
            print(json.dumps(e.response.json(), indent=2))
        except:
            print(e.response.text)

    print("\n" + "=" * 70)
    print("❌ TEST FAILED")
    print("=" * 70)
    exit(1)
