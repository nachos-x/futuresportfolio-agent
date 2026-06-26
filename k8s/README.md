# Kubernetes (GKE) Deployment

This directory contains manifests to deploy the app on Google Kubernetes Engine (GKE).

## Prerequisites

- GCP project with billing enabled
- `gcloud` CLI authenticated (`gcloud auth login`)
- Docker installed (or use Cloud Build)
- `kubectl` configured

## 1. Enable required APIs

```bash
gcloud services enable container.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com
```

## 2. Create Artifact Registry (for Docker images)

```bash
gcloud artifacts repositories create streamlit-futures \
  --repository-format=docker \
  --location=us-central1 \
  --description="Streamlit futures monitor images"
```

## 3. Build and push the image

Replace `YOUR_PROJECT_ID`:

```bash
# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-futures/streamlit-futures:latest .

# Push
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-futures/streamlit-futures:latest
```

Update the `image:` line in `k8s/deployment.yaml` with your pushed image.

## 4. Create GKE cluster (if you don't have one)

```bash
gcloud container clusters create streamlit-cluster \
  --zone=us-central1-a \
  --num-nodes=1 \
  --machine-type=e2-standard-4 \
  --enable-ip-alias
```

Get credentials:

```bash
gcloud container clusters get-credentials streamlit-cluster --zone=us-central1-a
```

## 5. Create the secret (API key)

```bash
kubectl create secret generic openrouter-secret \
  --from-literal=api-key=YOUR_OPENROUTER_API_KEY_HERE
```

Do **not** commit real keys.

## 6. Apply manifests

First create the secret (replace with your real key):

```bash
kubectl create secret generic openrouter-secret \
  --from-literal=api-key=sk-or-YOUR_REAL_OPENROUTER_KEY
```

Then apply (edit the image in deployment.yaml first):

```bash
kubectl apply -f k8s/
```

Or apply individually:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## 7. Access the app

For LoadBalancer (simpler):

Change Service type to `LoadBalancer` temporarily or create a separate service.

For Ingress (recommended with GCE Ingress):

```bash
kubectl get ingress streamlit-futures-ingress
```

Note the EXTERNAL-IP. It can take a few minutes to provision.

Access: `http://<EXTERNAL-IP>`

## 8. Useful commands

```bash
# Watch pods
kubectl get pods -w

# Logs
kubectl logs -f deployment/streamlit-futures

# Scale (careful - Streamlit sessions are per pod)
kubectl scale deployment streamlit-futures --replicas=2

# Delete
kubectl delete -f deployment.yaml
```

## Notes

- Currently 1 replica. Streamlit doesn't scale horizontally well without sticky sessions.
- The app is CPU-heavy on "Generate Report". The resources are set accordingly.
- For production: add Ingress with HTTPS (Google-managed cert + domain).
- Update `.streamlit/config.toml` if needed for proxy settings when behind Ingress.
- Health checks use Streamlit's `/_stcore/health` endpoint.

## Alternative: Use Service type LoadBalancer (no Ingress)

Edit the Service in deployment.yaml and change to:

```yaml
type: LoadBalancer
```

Then get the external IP with:

```bash
kubectl get svc streamlit-futures
```

This provisions a TCP load balancer directly to port 8501.
