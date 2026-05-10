# Manual Google Cloud Deployment Guide for Resume Analyzer

This comprehensive guide shows how to manually deploy your Resume Analyzer app to Google Cloud Platform step by step.

## 🚀 Overview

**Manual deployment** gives you complete control over:
- ✅ **Custom configurations**
- ✅ **Step-by-step understanding**
- ✅ **Full debugging access**
- ✅ **Learning opportunity**

## 📋 Prerequisites

### Required Accounts & Services
1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK (gcloud CLI)** installed
3. **Docker** installed locally
4. **GitHub account** (for code storage)

### Installation Commands
```bash
# Install Google Cloud SDK
# Windows
curl https://sdk.cloud.google.com | bash
# Or download installer: https://cloud.google.com/sdk/docs/install

# Install Docker
# Windows: Download Docker Desktop
# Linux: sudo apt-get install docker.io
# Mac: brew install docker
```

## 🔧 Step 1: Setup Google Cloud Environment

### 1.1 Install Google Cloud SDK
```bash
# Download and install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# After installation, restart terminal/command prompt
gcloud version
```

### 1.2 Authenticate with Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

### 1.3 Create and Configure Project
```bash
# Create new project (or use existing)
gcloud projects create resume-analyzer-prod

# Set active project
gcloud config set project resume-analyzer-prod

# Verify project
gcloud config get-value project
```

### 1.4 Enable Required APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "(run|cloudbuild|artifactregistry|storage)"
```

## 🐳 Step 2: Prepare Docker Image

### 2.1 Create Dockerfile for GCP
Create `dockerfile.gcp` with:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8501

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.gcp.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.gcp.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Run the app with Cloud Run optimizations
CMD ["streamlit", "run", "mobile_app.py", "--server.port=$PORT", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--browser.gatherUsageStats=false"]
```

### 2.2 Create GCP Requirements
Create `requirements.gcp.txt` with:
```txt
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
Pillow>=9.5.0
python-docx>=0.8.11
PyPDF2>=3.0.1
pdfplumber>=0.9.0
streamlit-lottie>=0.0.3
requests>=2.31.0
openai>=1.3.0
google-generativeai>=0.3.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pypdf>=3.17.0
docx>=0.8.11
lxml>=4.9.0
cssutils>=2.7.0
pytz>=2023.3
altair>=4.2.0
validators>=0.22.0
watchdog>=3.0.0
tqdm>=4.66.0
networkx>=3.1
openpyxl>=3.1.0
xlsxwriter>=3.1.0
python-multipart>=0.0.6
pydantic>=2.5.0
httpx>=0.25.0
beautifulsoup4>=4.12.0
nltk>=3.8.1
spacy>=3.7.2
wordcloud>=1.9.2
geopy>=2.4.0
folium>=0.15.0
branca>=0.6.0
streamlit-option-bar>=0.1.0
streamlit-aggrid>=0.3.4
streamlit-extras>=0.3.0
streamlit-plotly-events>=0.0.6
streamlit-elements>=0.1.0
streamlit-ace-editor>=0.1.0
streamlit-authenticator>=0.2.3
streamlit-camera-input>=0.1.0
streamlit-drawable-canvas>=0.9.0
streamlit-mic-recorder>=0.0.3
streamlit-audiorecorder>=0.0.3
streamlit-speech-to-text>=0.0.1
streamlit-text-to-speech>=0.0.1
```

### 2.3 Create Mobile App
Create `mobile_app.py` with:
```python
"""
Mobile-Optimized Resume Analyzer for Google Cloud
"""
import os
import sys
import streamlit as st

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import mobile configuration
from mobile_config import configure_mobile_app, mobile_friendly_upload, mobile_friendly_button, mobile_info_message

# Configure for mobile and GCP
configure_mobile_app()

# Import main application
from app import ResumeApp

def main():
    """Main function for GCP deployment"""
    # Show mobile info
    mobile_info_message()
    
    # Initialize and run app
    app = ResumeApp()
    app.main()

if __name__ == "__main__":
    main()
```

## 🏗️ Step 3: Build and Push Docker Image

### 3.1 Build Docker Image Locally
```bash
# Build the Docker image
docker build -f dockerfile.gcp -t gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest .

# Verify image was built
docker images | grep resume-analyzer
```

### 3.2 Configure Docker Authentication
```bash
# Authenticate Docker with Google Container Registry
gcloud auth configure-docker

# Verify authentication
docker pull gcr.io/cloud-builders/docker
```

### 3.3 Push Image to Google Container Registry
```bash
# Push the image
docker push gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest

# Verify image is pushed
gcloud container images list --repository gcr.io/YOUR_PROJECT_ID/resume-analyzer
```

## 🚀 Step 4: Deploy to Cloud Run

### 4.1 Deploy Application
```bash
# Deploy to Cloud Run
gcloud run deploy resume-analyzer \
    --image=gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest \
    --project=YOUR_PROJECT_ID \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --port=8501 \
    --memory=2Gi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=10 \
    --set-env-vars=PORT=8501,STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 4.2 Verify Deployment
```bash
# Check deployment status
gcloud run services describe resume-analyzer \
    --region=us-central1 \
    --format="table(status.url,status.latestReadyRevisionName,status.latestReadyRevisionCreateTime)"

# Get service URL
gcloud run services describe resume-analyzer \
    --region=us-central1 \
    --format="value(status.url)"
```

### 4.3 Test Application
```bash
# Test the deployed application
curl -f https://resume-analyzer-xxxxx-uc.a.run.app/_stcore/health

# Open in browser
# Visit the URL returned by the deployment
```

## 🗄️ Step 5: Configure Cloud Storage (Optional)

### 5.1 Create Storage Bucket
```bash
# Create bucket for file uploads
gsutil mb gs://YOUR_PROJECT_ID-resume-uploads

# Set bucket to public
gsutil iam ch allUsers:objectViewer gs://YOUR_PROJECT_ID-resume-uploads

# Verify bucket
gsutil ls gs://YOUR_PROJECT_ID-resume-uploads
```

### 5.2 Configure Lifecycle Policy
Create `lifecycle.json`:
```json
{
  "rule": [
    {
      "action": {
        "type": "Delete"
      },
      "condition": {
        "age": 30,
        "withState": "ANY"
      }
    }
  ]
}
```

Apply lifecycle policy:
```bash
gsutil lifecycle set gs://YOUR_PROJECT_ID-resume-uploads lifecycle.json
```

## ⚙️ Step 6: Configure Environment Variables

### 6.1 Set Up Secrets Manager
```bash
# Create secrets
gcloud secrets create openai-api-key --replication-policy="automatic"
gcloud secrets create gemini-api-key --replication-policy="automatic"

# Add secret values
echo "your-openai-api-key-here" | gcloud secrets versions add openai-api-key --data-file=-
echo "your-gemini-api-key-here" | gcloud secrets versions add gemini-api-key --data-file=-
```

### 6.2 Grant Access to Service Account
```bash
# Get default service account
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

# Grant secret access
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 6.3 Update Deployment with Secrets
```bash
# Redeploy with secrets
gcloud run deploy resume-analyzer \
    --image=gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest \
    --project=YOUR_PROJECT_ID \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --port=8501 \
    --memory=2Gi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=10 \
    --set-env-vars=PORT=8501,STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    --set-secrets=/secrets/OPENAI_API_KEY=openai-api-key:latest,/secrets/GEMINI_API_KEY=gemini-api-key:latest
```

## 📊 Step 7: Configure Monitoring

### 7.1 Set Up Logging
```bash
# View application logs
gcloud logs read "resource.type=cloud_run_revision" \
    --limit=50 \
    --format="table(timestamp,textPayload)"

# Export logs to BigQuery
gcloud logging sinks create resume-analyzer-logs \
    bigquery.googleapis.com/projects/YOUR_PROJECT_ID/datasets/logs \
    --log-filter='resource.type="cloud_run_revision"'
```

### 7.2 Set Up Monitoring
```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json

# Create alert policies
gcloud alpha monitoring policies create \
    --notification-channels=projects/YOUR_PROJECT_ID/notificationChannels/123456789 \
    --condition-display-name="High Error Rate" \
    --condition-filter='metric.type="run.googleapis.com/container/error_count"'
```

## 🔧 Step 8: Configure Custom Domain (Optional)

### 8.1 Map Custom Domain
```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create resume.yourdomain.com \
    --service=resume-analyzer \
    --region=us-central1

# Verify domain mapping
gcloud run domain-mappings describe resume.yourdomain.com \
    --region=us-central1
```

### 8.2 Configure DNS
```bash
# Get verification records
gcloud run domain-mappings describe resume.yourdomain.com \
    --region=us-central1 \
    --format="value(status.resourceRecords)"

# Add these records to your DNS provider
# Usually: A record, CNAME record, or TXT record for verification
```

## 🔍 Step 9: Troubleshooting

### 9.1 Common Issues

#### "Deployment Failed"
```bash
# Check deployment logs
gcloud run services describe resume-analyzer \
    --region=us-central1 \
    --format="yaml"

# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

#### "Image Not Found"
```bash
# Verify image exists
gcloud container images list --repository gcr.io/YOUR_PROJECT_ID/resume-analyzer

# Check image details
gcloud container images describe gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest
```

#### "Permission Denied"
```bash
# Check IAM permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@gmail.com" \
    --role="roles/run.admin"
```

#### "High Memory Usage"
```bash
# Monitor memory usage
gcloud monitoring metrics list \
    --filter='metric.type:"run.googleapis.com/container/memory_usage"'

# Increase memory allocation
gcloud run services update resume-analyzer \
    --region=us-central1 \
    --memory=4Gi
```

### 9.2 Debug Commands
```bash
# Check service status
gcloud run services list

# Check revisions
gcloud run revisions list --service=resume-analyzer --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic resume-analyzer \
    --region=us-central1 \
    --to-revisions=REVISION_NAME
```

## 📋 Step 10: Maintenance

### 10.1 Update Application
```bash
# Build new version
docker build -f dockerfile.gcp -t gcr.io/YOUR_PROJECT_ID/resume-analyzer:v2.0 .

# Push new version
docker push gcr.io/YOUR_PROJECT_ID/resume-analyzer:v2.0

# Deploy new version
gcloud run deploy resume-analyzer \
    --image=gcr.io/YOUR_PROJECT_ID/resume-analyzer:v2.0 \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated
```

### 10.2 Scale Application
```bash
# Configure auto-scaling
gcloud run services update resume-analyzer \
    --region=us-central1 \
    --min-instances=0 \
    --max-instances=10 \
    --cpu-throttling=false

# Set concurrency
gcloud run services update resume-analyzer \
    --region=us-central1 \
    --concurrency=20
```

### 10.3 Backup and Recovery
```bash
# Export configuration
gcloud run services describe resume-analyzer \
    --region=us-central1 \
    --format="yaml" > service-config.yaml

# Export IAM policy
gcloud projects get-iam-policy YOUR_PROJECT_ID > iam-policy.json
```

## ✅ Success Checklist

### Before Deployment
- [ ] Google Cloud SDK installed and authenticated
- [ ] Project created and configured
- [ ] Required APIs enabled
- [ ] Docker image built successfully
- [ ] Image pushed to Container Registry
- [ ] Environment variables configured

### After Deployment
- [ ] Service deployed successfully
- [ ] Application accessible via URL
- [ ] All features working properly
- [ ] Mobile responsive design
- [ ] Logs and monitoring configured
- [ ] Error handling working

### Production Ready
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active (automatic)
- [ ] Monitoring alerts set up
- [ ] Backup procedures documented
- [ ] Scaling policies configured
- [ ] Security policies implemented

## 🎯 Quick Reference Commands

### Essential Commands
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy application
gcloud run deploy resume-analyzer --image=gcr.io/YOUR_PROJECT_ID/resume-analyzer:latest

# View logs
gcloud logs read "resource.type=cloud_run_revision"

# Check service status
gcloud run services describe resume-analyzer --region=us-central1

# Update service
gcloud run services update resume-analyzer --region=us-central1 --memory=4Gi
```

### URLs and Access
- **Cloud Run URL**: `https://resume-analyzer-xxxxx-uc.a.run.app`
- **Console**: `https://console.cloud.google.com/run`
- **Container Registry**: `https://console.cloud.google.com/gcr`
- **Monitoring**: `https://console.cloud.google.com/monitoring`

## 🎉 Congratulations!

Your Resume Analyzer is now **manually deployed to Google Cloud** with:

- ✅ **Complete control** over deployment
- ✅ **Production-ready** configuration
- ✅ **Mobile-optimized** interface
- ✅ **Auto-scaling** capabilities
- ✅ **Monitoring** and logging
- ✅ **Security** best practices

**Your app is live at**: `https://resume-analyzer-xxxxx-uc.a.run.app`

**Ready for Android users**: Fully responsive and touch-optimized! 📱✨

## 📞 Support Resources

### Documentation
- **Google Cloud Run**: cloud.google.com/run/docs
- **Container Registry**: cloud.google.com/container-registry/docs
- **Cloud Storage**: cloud.google.com/storage/docs
- **Monitoring**: cloud.google.com/monitoring/docs

### Troubleshooting
- **Stack Overflow**: Use [google-cloud-run] tag
- **Google Cloud Community**: cloud.google.com/community
- **Support**: cloud.google.com/support

---

**Your Resume Analyzer is now production-ready on Google Cloud!** ☁️✨
