# CampusShield Render Deployment

This repo is prepared for deploying the ML web service on Render:

1. `campusshield-ml-api` (`ml.api:app`)

## Files Added for Deployment

- `render.yaml`
- `requirements-ml.txt`
- `requirements-backend.txt`
- `runtime.txt`

## Before You Deploy

1. Ensure model artifacts are committed:
   - `model.pkl`
   - `vectorizer.pkl`
2. Push latest code to GitHub.

## Deploy with Blueprint

1. In Render, choose **New +** -> **Blueprint**.
2. Connect this GitHub repo.
3. Render will detect `render.yaml` and create both services.

## Required Environment Variables

- `MODEL_VERSION` (optional, default `tfidf-logreg-v1`)
- `SCAM_THRESHOLD` (optional, default `0.70`)

## Health Checks

- ML API: `GET /health`
## Quick Verification

```bash
curl https://<ml-service>.onrender.com/health
curl -X POST https://<ml-service>.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Pay registration fee to confirm internship"}'
```
