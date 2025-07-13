# Google Cloud Deployment Instructions

This guide will walk you through deploying your React frontend to Firebase Hosting and your FastAPI backend to Cloud Run.

## Prerequisites

- **Google Cloud Account**: Ensure you have an active Google Cloud account.
- **Google Cloud SDK (gcloud CLI)**: Install and initialize the gcloud CLI on your local machine.
  - **Installation Guide**: Initialize with `gcloud init`
- **Node.js and npm/yarn**: For the React frontend.
- **Python and pip**: For the FastAPI backend.
- **Firebase CLI**: Install globally: `npm install -g firebase-tools`

## Part 1: Deploying the FastAPI Backend to Cloud Run

Cloud Run is a fully managed compute platform that enables you to deploy stateless containers that are invocable via web requests or Pub/Sub events.

### Step 1: Prepare your FastAPI application

#### Navigate to Backend Directory:

The FastAPI backend is located in the `backend-cv-agent` directory.
```bash
cd backend-cv-agent
```

#### Requirements and Dependencies:

The `requirements.txt` file is already included in the `backend-cv-agent` directory with all necessary dependencies:

```txt
fastapi==0.111.0
uvicorn==0.30.1
python-dotenv==1.0.1
```

**Note**: `python-dotenv` is added here if you use it for local development, but it won't be used in Cloud Run for production environment variables.

#### Docker Configuration:

The `Dockerfile` is already included in the `backend-cv-agent` directory. Create a `.dockerignore` file in the same directory to exclude unnecessary files from the Docker build context:

```
cv-agent-front/
```

You can add other files or folders you wish to exclude (e.g., `**pycache**/`, `.git/`, `.env`) on separate lines.

#### Create Dockerfile:

In the same `fastapi-backend` directory, create a file named `Dockerfile` (no extension) with the following content. This Dockerfile tells Cloud Run how to build your application's container image.

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
# The .dockerignore file will ensure 'cv-agent-front/' is not copied.
COPY . /app

# Expose the port that Uvicorn will run on
# Cloud Run will automatically set the PORT environment variable.
ENV PORT 8000

# Run the Uvicorn server when the container starts
# The --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Note**: The Dockerfile does NOT copy the `.env` file. This is intentional for security reasons.

### Step 2: Deploy to Cloud Run

#### Authenticate gcloud:

Open your terminal and ensure you are logged into your Google Cloud account:

```bash
gcloud auth login
```

#### Set your Google Cloud Project:

Replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID. You can find this in the Google Cloud Console dashboard.

```bash
gcloud config set project YOUR_PROJECT_ID
```

#### Deploy the Service:

Navigate to your `fastapi-backend` directory in the terminal.

```bash
cd fastapi-backend
```

Now, deploy your service. Cloud Run will automatically build the Docker image and deploy it.
Choose a region close to you (e.g., `us-central1`, `southamerica-east1`).

**Important**: How to handle environment variables (like API keys):

Instead of using a `.env` file in production, Cloud Run allows you to set environment variables directly during deployment. This is the recommended and more secure way to manage secrets and configurations for your Cloud Run service.

To deploy and set environment variables, and importantly, specify the container port:

```bash
gcloud run deploy fastapi-backend-service \
 --source . \
 --region southamerica-east1 \
 --allow-unauthenticated \
 --platform managed \
 --set-env-vars OPENAI_API_KEY="my_secret_key" \
 --port 8000  # <<< IMPORTANT: Tell Cloud Run your container listens on port 8000
```

Replace `OPENAI_API_KEY` with your actual API key.

The `--port 8000` flag explicitly tells Cloud Run that your container is listening on port 8000, resolving the DEADLINE_EXCEEDED error on 8080. Cloud Run will now correctly send traffic and health checks to port 8000.

#### Why not use .env in Docker?

- **Security**: Embedding secrets directly into a Docker image makes them harder to manage and potentially exposes them if the image is shared or accessed without proper authorization.
- **Flexibility**: Environment variables set at deployment time allow you to use the same Docker image across different environments (e.g., development, staging, production) with different configurations without rebuilding the image.

#### Accessing Environment Variables in FastAPI:

In your `main.py` (FastAPI application), you would access these environment variables using `os.environ.get()`:

```python
import os

# ... other imports

api_key = os.environ.get("OPENAI_API_KEY")  # Ensure you use OPENAI_API_KEY as set in --set-env-vars
if not api_key:  # Handle the case where the API_KEY is not set (e.g., raise an error, log a warning)
    print("Warning: OPENAI_API_KEY environment variable not set!")
```

For highly sensitive secrets (e.g., database passwords), consider **Google Cloud Secret Manager**.

Secret Manager allows you to store, manage, and access secrets securely. You can then grant your Cloud Run service permissions to access specific secrets from Secret Manager. This is a more advanced but highly recommended approach for production-grade applications. For this interview, using `--set-env-vars` is sufficient and demonstrates good practice.

#### Get the Service URL:

After successful deployment, the gcloud CLI will output the Service URL. It will look something like `https://fastapi-backend-service-xxxxxx-uc.a.run.app`. Copy this URL. You will need it for your React frontend.

## Part 2: Deploying the React Frontend to Firebase Hosting

Firebase Hosting provides fast and secure hosting for your web app, along with a global CDN.

### Step 1: Prepare your React application

#### Create React App:

If you haven't already, create a new Vite React project.

```bash
npm create vite@latest my-react-app -- --template react
cd my-react-app
npm install
```

Replace the content of `src/App.jsx` with the React code provided previously.

#### Update Backend URL in React:

Open `src/App.jsx` in your React project.

Find the line:

```javascript
const backendUrl = "YOUR_FASTAPI_CLOUD_RUN_URL_HERE";
```

Replace `YOUR_FASTAPI_CLOUD_RUN_URL_HERE` with the Cloud Run Service URL you copied in the previous step.

#### Build the React App:

Navigate to your React project directory in the terminal:

```bash
cd my-react-app
```

Build the production-ready version of your React application:

```bash
npm run build
```

This will create a `dist` directory containing all the static files for your frontend.

### Step 2: Initialize Firebase for Hosting

#### Login to Firebase:

```bash
firebase login -i
```

Follow the prompts to log in with your Google account. The `-i` flag forces interactive login, which can be helpful in certain environments.

#### Initialize Firebase Project:

In your React project's root directory (`my-react-app`), run:

```bash
firebase init
```

Follow these prompts:

1. **Which Firebase features do you want to set up for this directory?** Select `Hosting: Configure files for Firebase Hosting and (optionally) set up GitHub Action deploys`. Use Spacebar to select, Enter to confirm.

2. **Please select a Firebase project for this directory:** Select `Use an existing project` and choose the same Google Cloud project ID you used for Cloud Run.

3. **What do you want to use as your public directory?** Type `dist` (this is where Vite puts the build output) and press Enter.

4. **Configure as a single-page app (rewrite all URLs to /index.html)?** Type `Y` and press Enter.

5. **Set up automatic builds and deploys with GitHub?** Type `N` (unless you want to set up CI/CD, which is beyond this basic guide).

This will create a `firebase.json` file in your project root.

### Step 3: Deploy to Firebase Hosting

#### Deploy:

From your React project's root directory (`my-react-app`), run the deploy command:

```bash
firebase deploy --only hosting
```

This will upload the contents of your `dist` directory to Firebase Hosting.

#### Get the Hosting URL:

After successful deployment, the Firebase CLI will provide a "Hosting URL" (e.g., `https://your-project-id.web.app`). Copy this URL. This is the public URL of your React application.

## Verification

1. **Open Frontend URL**: Open the Firebase Hosting URL in your web browser.
2. **Check Message**: You should see the React app load, and after a moment, it should display the message: "Hello from FastAPI backend!"

### Troubleshooting:

#### Common Issues:

- **Failed to load message**: Double-check that your Cloud Run service is running and that the `backendUrl` in your React `App.jsx` is exactly correct.
- **Network errors**: Check the browser's developer console for any network errors (CORS issues, failed requests) or JavaScript errors.
- **Access denied**: Ensure your Cloud Run service has `--allow-unauthenticated` set if you want public access.

#### Firebase Project Not Listed in CLI

**Problem**: Your existing Google Cloud project doesn't appear in the `firebase init` project selection list.

**Explanation**: This happens because while all Firebase projects are Google Cloud projects under the hood, not all Google Cloud projects are automatically Firebase projects. For an existing Google Cloud project to appear in the Firebase CLI list, you need to explicitly "add Firebase" services to it.

**Solution**: Link your existing Google Cloud project to Firebase:

1. **Go to the Firebase Console**  
   Open your web browser and navigate to: https://console.firebase.google.com/

2. **Add Project**  
   Click on "**Add project**" (or "Create a project" if it's your first time).

3. **Select Existing Google Cloud Project**  
   Instead of creating a new project, look for a link or option that says:

   - "**Already have a Google Cloud project?**" or
   - "**Add Firebase to an existing Google Cloud project**"

   You might need to start typing your Google Cloud Project ID in the project name field, and it should appear in a dropdown list.

4. **Confirm and Continue**  
   Select your existing Google Cloud project from the list. Firebase will guide you through adding Firebase services to that project. This involves:

   - Accepting Firebase terms of service
   - Enabling necessary APIs automatically

5. **Enable Google Analytics** _(Optional but Recommended)_  
   You'll be prompted to enable Google Analytics. While optional, it's recommended for a complete Firebase experience and provides useful insights.

After completing these steps, your Google Cloud project will appear in the Firebase CLI project list during `firebase init`.

#### Permission Denied Errors During Deployment

**Problem**: You encounter `PERMISSION_DENIED` errors when running `gcloud run deploy` or other Google Cloud commands.

**Explanation**: This typically happens when your user account or service accounts don't have the necessary IAM roles to perform the deployment operations.

**Solution**: Grant the required permissions using either the Google Cloud Console or gcloud commands.

##### Option 1: Using Google Cloud Console (Recommended for ease of use)

1. **Go to the IAM & Admin page** in your Google Cloud Console:  
   https://console.cloud.google.com/iam-admin/iam

2. **Select your project** from the top dropdown.

3. **Click on "+ Grant Access"** at the top.

4. **For your user account** (e.g., `pratesrop@gmail.com`):

   - In the "**New principals**" field, enter your email address
   - In the "**Select a role**" dropdown, search for and add:
     - `Cloud Run Admin`
     - `Service Account User`
     - `Storage Admin` (or `Storage Object Admin`)
     - _(Optional, but comprehensive for development)_ `Editor`
   - Click "**Save**"

5. **For the Cloud Build Service Account**:
   - First, find its name in the IAM table. Look for a principal ending with `@cloudbuild.gserviceaccount.com`
   - It's usually named: `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`
   - Click on "**+ Grant Access**" again
   - In the "**New principals**" field, paste the Cloud Build service account email
   - In the "**Select a role**" dropdown, search for and add:
     - `Cloud Run Developer`
     - `Artifact Registry Writer` (if using Artifact Registry)
     - `Storage Object Creator`
   - Click "**Save**"

##### Option 2: Using gcloud Commands (More programmatic)

Replace `YOUR_PROJECT_ID` with your actual project ID and `PROJECT_NUMBER` with your project number. You can get your project number by running `gcloud projects describe YOUR_PROJECT_ID`.

```bash
# Get your project number (needed for Cloud Build service account)
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant roles to your user account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:pratesrop@gmail.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:pratesrop@gmail.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:pratesrop@gmail.com" \
    --role="roles/storage.admin"  # Or roles/storage.objectAdmin

# Grant roles to the Cloud Build service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/artifactregistry.writer"  # If using Artifact Registry

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/storage.objectCreator"
```

After granting these permissions, try running your `gcloud run deploy` command again. This should resolve the `PERMISSION_DENIED` error.
