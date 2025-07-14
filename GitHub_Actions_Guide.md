# GitHub Actions Configuration Guide for Full Stack Deployment

This guide provides comprehensive instructions for setting up a GitHub Actions workflow to automatically build and deploy your FastAPI backend to Google Cloud Run and your React frontend to Firebase Hosting from a single GitHub repository.

## Repository Structure Assumption

This guide assumes your repository has a structure similar to this:

```
your-repo/
├── .github/
│   └── workflows/
│       └── deploy.yml <-- This is the file you'll create
├── main.py <-- Your FastAPI backend files (in the root)
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── my-react-app/ <-- Your React frontend folder
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── .env.production <-- NOT committed to GitHub
│   ├── firebase.json <-- SHOULD be committed to GitHub
│   └── .firebaserc <-- SHOULD be committed to GitHub
└── ... other project files
```

## Step 1: Set Up GitHub Secrets

GitHub Secrets are used to securely store sensitive information (like API keys and service account credentials) that your GitHub Actions workflow needs but should not be committed directly into your repository.

### a. Google Cloud Service Account Key (for Cloud Run Deployment)

This key grants your GitHub Actions workflow permissions to interact with Google Cloud services (Cloud Build, Cloud Run, Artifact Registry, etc.).

**Create a Service Account in Google Cloud:**

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Navigate to **IAM & Admin > Service Accounts**
3. Click **"+ CREATE SERVICE ACCOUNT"**
4. **Service account name:** Give it a descriptive name (e.g., `github-actions-deployer`)
5. Click **"CREATE AND CONTINUE"**

**Grant Permissions to the Service Account:**

This service account needs specific roles to build Docker images and deploy to Cloud Run.

In the "Grant this service account access to project" section, add the following roles:
- `Cloud Build Editor` (roles/cloudbuild.builds.editor)
- `Cloud Run Admin` (roles/run.admin)
- `Service Account User` (roles/iam.serviceAccountUser)
- `Artifact Registry Writer` (roles/artifactregistry.writer)
- `Storage Admin` (roles/storage.admin)

Click **"DONE"**.

**Generate a JSON Key for the Service Account:**

1. After creating the service account, go back to the Service Accounts list
2. Click on the email address of the service account you just created (e.g., `github-actions-deployer@your-project-id.iam.gserviceaccount.com`)
3. Go to the **Keys** tab
4. Click **"ADD KEY" > "Create new key"**
5. Select **"JSON"** as the Key type
6. Click **"CREATE"**
7. A JSON file will be downloaded to your computer. Open this file and copy its entire content

**Add the JSON Key to GitHub Secrets:**

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `GCP_SA_KEY`
4. **Secret:** Paste the entire JSON content you copied from the downloaded file
5. Click **Add secret**

### b. Firebase Service Account Key (for Firebase Hosting Deployment)

This is the recommended and secure way to authenticate Firebase deployments in GitHub Actions, replacing the deprecated `firebase login:ci` token.

**Create a Firebase Service Account in Google Cloud:**

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Navigate to **IAM & Admin > Service Accounts**
3. Click **"+ CREATE SERVICE ACCOUNT"**
4. **Service account name:** Give it a descriptive name (e.g., `firebase-deployer`)
5. Click **"CREATE AND CONTINUE"**

**Grant Permissions to the Firebase Service Account:**

This service account needs roles to deploy to Firebase Hosting.

In the "Grant this service account access to project" section, add the following roles:
- `Firebase Admin` (roles/firebase.admin) - This grants broad administrative access to Firebase. For production, consider more granular roles like Firebase Hosting Admin (roles/firebasehosting.admin) and Firebase Hosting Viewer (roles/firebasehosting.viewer) if you want to limit permissions. Firebase Admin is simpler for initial setup.
- `Storage Object Admin` (roles/storage.objectAdmin) - Firebase Hosting uses Cloud Storage buckets to store your deployed files. This role allows the service account to manage those files.

Click **"DONE"**.

**Generate a JSON Key for the Firebase Service Account:**

1. After creating the service account, go back to the Service Accounts list
2. Click on the email address of the service account you just created (e.g., `firebase-deployer@your-project-id.iam.gserviceaccount.com`)
3. Go to the **Keys** tab
4. Click **"ADD KEY" > "Create new key"**
5. Select **"JSON"** as the Key type
6. Click **"CREATE"**
7. A JSON file will be downloaded to your computer. Open this file and copy its entire content

**Add the JSON Key to GitHub Secrets:**

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `FIREBASE_SERVICE_ACCOUNT_KEY` (using a more descriptive name now)
4. **Secret:** Paste the entire JSON content you copied from the downloaded file
5. Click **Add secret**

### c. OpenAI API Key (for FastAPI Backend)

This is a separate secret for your OpenAI API key, distinct from your GCP service account.

**Add the OpenAI API Key to GitHub Secrets:**

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `OPENAI_API_KEY` (use this exact name if your Python code uses `os.environ.get("OPENAI_API_KEY")`)
4. **Secret:** Paste your actual OpenAI API key
5. Click **Add secret**

### d. Frontend Backend URL (for React build)

If your React app is built in GitHub Actions and needs the backend URL at build time, add it as a secret.

**Add the Backend URL to GitHub Secrets:**

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `VITE_API_BASE_URL`
4. **Secret:** Paste the full URL of your deployed Cloud Run service (e.g., `https://cvapi-backend-service-xxxxxx-uc.a.run.app`)
5. Click **Add secret**

## Step 2: Create the Artifact Registry Repository (Crucial!)

Before your GitHub Actions workflow can push Docker images, the target Artifact Registry repository must exist.

**Go to Artifact Registry:**

1. Open your Google Cloud Console: https://console.cloud.google.com/
2. Ensure you have selected your project (cv-raphael-ai)
3. In the left navigation menu, go to **Artifact Registry > Repositories**

**Create the Repository:**

1. Click **"+ CREATE REPOSITORY"**
2. **Name:** Enter `cvapi-backend-service` (this must exactly match `FASTAPI_SERVICE_NAME` in your GitHub Actions workflow)
3. **Format:** Select `Docker`
4. **Mode:** Choose `Standard`
5. **Region:** Select `southamerica-east1` (this must exactly match `GCP_REGION` in your GitHub Actions workflow)
6. Click **"CREATE"**

Once created, you should see `cvapi-backend-service` listed in your repositories. The `cloud-run-source-deploy` repository can remain; it's often a default created by Cloud Run for source deployments and doesn't interfere with your custom setup.

## Step 3: Create the GitHub Actions Workflow File

Create a file named `deploy.yml` inside the `.github/workflows/` directory in your repository.

```
your-repo/
└── .github/
    └── workflows/
        └── deploy.yml <-- Create this file
```

Paste the following YAML content into `deploy.yml`:

```yaml
name: Deploy CV Agent Full Stack App to Google Cloud

on:
  push:
    branches: 
      - main # Trigger on pushes to the main branch (or your primary branch)

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    env:
      GCP_PROJECT_ID: 'cv-raphael-ai' # Your Google Cloud Project ID (string)
      GCP_REGION: southamerica-east1 # Your desired GCP region
      FASTAPI_SERVICE_NAME: cvapi-backend-service # IMPORTANT: This should be the name of your custom Artifact Registry repo and Cloud Run service
      FASTAPI_BACKAPI_DIR: backend-cv-agent # Directory for your FastAPI backend
      REACT_APP_DIR: cv-agent-front # Directory name for your React frontend

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # --- Backend (FastAPI on Cloud Run) Deployment ---
      - name: Authenticate Google Cloud CLI
        uses: google-github-actions/auth@v2
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}' # Use the GitHub Secret for GCP Service Account Key

      - name: Set up Google Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker to use Google Cloud Artifact Registry
        run: gcloud auth configure-docker ${{ env.GCP_REGION }}-docker.pkg.dev

      - name: Build and Push Docker Image for FastAPI Backend
        # Navigate into the backend directory to build the Docker image
        run: |
          cd ${{ env.FASTAPI_BACKAPI_DIR }}
          docker build -t ${{ env.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ env.FASTAPI_SERVICE_NAME }}/image:latest .
          docker push ${{ env.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ env.FASTAPI_SERVICE_NAME }}/image:latest

      - name: Deploy FastAPI Backend to Cloud Run
        run: |
          gcloud run deploy ${{ env.FASTAPI_SERVICE_NAME }} \
            --image ${{ env.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ env.FASTAPI_SERVICE_NAME }}/image:latest \
            --region ${{ env.GCP_REGION }} \
            --allow-unauthenticated \
            --platform managed \
            --set-env-vars OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}" \
            --port 8000 # Important: Match this to your Dockerfile's exposed port

      # --- Frontend (React on Firebase Hosting) Deployment ---
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20' # Use a stable Node.js version compatible with your React app

      - name: Install Frontend Dependencies
        run: |
          cd ${{ env.REACT_APP_DIR }}
          npm install

      - name: Build React App
        run: |
          cd ${{ env.REACT_APP_DIR }}
          npm run build
        env:
          # Pass the backend URL from GitHub Secrets to the React build process
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}

      - name: Deploy React App to Firebase Hosting
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}' # GitHub's default token for repo access
          # Use the Firebase Service Account Key directly
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT_KEY }}'
          projectId: ${{ env.GCP_PROJECT_ID }} # Use the same project ID
          channelId: live # Deploy to the live channel (or 'staging', etc.)
          # Specify the directory where firebase.json is located relative to the repo root
          # and the public directory relative to that firebase.json location
          entryPoint: './${{ env.REACT_APP_DIR }}' # Path to your React app directory
          publicDir: 'dist' # The 'dist' folder is inside the REACT_APP_DIR
```

## Step 4: Verify Your Project Code

### FastAPI Backend (main.py)

Ensure your FastAPI application accesses the `OPENAI_API_KEY` from environment variables, not from a `.env` file.

```python
import os

# This is the correct way to access environment variables in FastAPI
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    print("Error: OPENAI_API_KEY environment variable not found!")
    # Consider raising an exception here to prevent the app from running without the key
    # raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Use openai_api_key when initializing your OpenAI client or making calls
# e.g., openai.api_key = openai_api_key
```

### React Frontend (src/App.jsx or similar)

Ensure your React application accesses the backend URL using Vite's `import.meta.env` syntax.

```javascript
// Example in src/App.jsx
import React, { useState, useEffect } from 'react';

function App() {
  // Access the backend URL from Vite's environment variables
  const backendUrl = import.meta.env.VITE_API_BASE_URL;

  // ... rest of your component logic
}

export default App;
```

## Step 5: Commit and Push to GitHub

Once you have:

1. Set up all required GitHub Secrets (including the new `FIREBASE_SERVICE_ACCOUNT_KEY`)
2. Created the Artifact Registry repository named `cvapi-backend-service`
3. Updated the `.github/workflows/deploy.yml` file with the provided content (and replaced placeholders, especially `FIREBASE_SERVICE_ACCOUNT_KEY`)
4. Ensured your backend and frontend code correctly read environment variables

Commit these changes and push them to your main branch:

```bash
git add .
git commit -m "Configure GitHub Actions for full stack deployment with Firebase Service Account Key"
git push origin main
```

GitHub Actions will automatically detect the `deploy.yml` file and start the workflow. You can monitor its progress in the **"Actions"** tab of your GitHub repository.