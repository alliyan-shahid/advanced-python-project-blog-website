# Deployment Guide

## Local Deployment with Docker

### Prerequisites
- Docker installed on your machine
- Environment variables set in `.env` file

### Steps

1. **Copy `.env.example` to `.env` and update values:**
   ```bash
   cp .env.example .env
   ```

2. **Build Docker image:**
   ```bash
   docker build -t blog-with-users:latest .
   ```

3. **Run container:**
   ```bash
   docker run -p 8080:8080 \
     -e FLASK_KEY="your-secret-key" \
     -e DB_URI="your-db-uri" \
     -e SENDER_EMAIL="your-email@gmail.com" \
     -e SENDER_PASSWORD="your-app-password" \
     -e RECIPIENT_EMAIL="recipient@example.com" \
     blog-with-users:latest
   ```

## Cloud Build Deployment to Google Cloud Run

### Prerequisites
1. Google Cloud Project with billing enabled
2. Cloud Build and Cloud Run APIs enabled
3. Artifact Registry created (named `cloud-run-source-deploy`)
4. Service account with required permissions

### Setup Steps

1. **Install Google Cloud SDK:**
   ```bash
   # Download from https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize and authenticate:**
   ```bash
   gcloud init
   gcloud auth login
   gcloud config set project YOUR-PROJECT-ID
   ```

3. **Create Artifact Registry (if not exists):**
   ```bash
   gcloud artifacts repositories create cloud-run-source-deploy \
     --repository-format=docker \
     --location=asia-south1
   ```

4. **Update `cloudbuild.yaml` substitutions:**
   - Replace `_FLASK_KEY` with your actual secret key
   - Replace `_DB_URI` with your PostgreSQL connection string
   - Replace `_SENDER_EMAIL`, `_SENDER_PASSWORD`, `_RECIPIENT_EMAIL`

5. **Deploy using Cloud Build:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

6. **Monitor deployment:**
   ```bash
   gcloud builds log --stream LATEST-BUILD-ID
   ```

7. **View deployed service:**
   ```bash
   gcloud run services describe blog-with-users --region asia-south1
   ```

## Important Notes

### Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`:
   ```
   .env
   .env.local
   ```

2. **Use Cloud Secrets for sensitive data:**
   ```bash
   echo "your-value" | gcloud secrets create FLASK_KEY --data-file=-
   ```

3. **Update all placeholder values** in `cloudbuild.yaml`:
   - `_FLASK_KEY`: Strong random secret key
   - `_DB_URI`: PostgreSQL or other database connection
   - `_SENDER_EMAIL`: Gmail account for sending emails
   - `_SENDER_PASSWORD`: App-specific password (not account password)
   - `_RECIPIENT_EMAIL`: Where to receive contact form submissions

### Email Configuration (Gmail)

For `SENDER_PASSWORD`:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Create an App password
4. Use this 16-character password in `SENDER_PASSWORD`

### Database Configuration

For production, use PostgreSQL with Supabase or similar:
```
postgresql://user:password@host:port/database?sslmode=require
```

Ensure your database has the required schema and is accessible from Cloud Run.

### Monitoring

After deployment, monitor your service:
- Cloud Run Console: https://console.cloud.google.com/run
- Cloud Build History: View build logs and history
- Cloud Logs: Monitor application logs

## Rollback

If needed, revert to previous version:
```bash
gcloud run deploy blog-with-users \
  --image asia-south1-docker.pkg.dev/PROJECT-ID/cloud-run-source-deploy/blog-with-users:PREVIOUS-SHA \
  --region asia-south1
```
