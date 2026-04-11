# Corti Python API Example

Quick Python example showing how to use Corti's fact extraction API. Built this to test out their API endpoints.

## What it does

Extracts structured medical facts from clinical text (like referral letters or consultation notes) using Corti's AI.

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env-example` to `.env` and add your credentials:

```
CORTI_TENANT_NAME=your-tenant
CORTI_CLIENT_ID=your-client-id
CORTI_CLIENT_SECRET=your-secret
CORTI_ENVIRONMENT=eu
```

## Usage

Run the test script:

```bash
python test_detailed.py
```

It loads the sample orthopedic letter from `Sample/` and sends it to Corti's fact extraction endpoint.

## Files

- `corti_client.py` - API client with OAuth2 auth and fact extraction
- `test_detailed.py` - Test script that extracts facts from sample letter
- `extraction_script.js` - Reference implementation from Corti docs
- `Sample/Orthopedic Referral Letter.txt` - Sample medical text

## Note

Current test credentials return 401 on fact extraction endpoint. The token has `audience: "account"` but the API needs `audience: "capioswe"`. Code works fine, just need proper credentials with API access permissions.

## API Endpoint

```
POST https://api.eu.corti.app/v2/facts/extract
{
  "context": [{"type": "text", "text": "medical text here..."}],
  "outputLanguage": "en-US"
}
```

Response includes extracted facts with confidence scores and usage info.

---

Built for testing Corti API integration. May expand later if I get proper API access.
