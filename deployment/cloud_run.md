# Deploying EcoGuardian on Google Cloud Run

This guide shows how to deploy the EcoGuardian multi-agent backend + Streamlit UI as a cloud service using **Google Cloud Run**.

---

## 🚀 1. Prerequisites

Before you deploy, make sure you have:

- A Google Cloud project
- Billing enabled
- Permissions to deploy Cloud Run services
- Google Cloud SDK installed locally
- Docker installed (optional but recommended)

Login:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 🧱 2. Build Container Image

From the root of your eco_guardian project, run:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ecoguardian
```

---

## 🚀 3. Deploy to Cloud Run

```bash
gcloud run deploy ecoguardian   --image gcr.io/YOUR_PROJECT_ID/ecoguardian   --platform managed   --region us-central1   --allow-unauthenticated   --memory 1Gi   --timeout 600
```

---

## 🔐 4. Set Environment Variables

Cloud Run → Edit Service → Variables:

```
GEMINI_API_KEY = your_key_here
```

Alternatively:

```bash
gcloud run services update ecoguardian   --update-env-vars GEMINI_API_KEY=your_key_here
```

---

## 🔗 5. Access Public URL

Cloud Run provides a URL like:

```
https://ecoguardian-xxxxx-run.app
```

---
