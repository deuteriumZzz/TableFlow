# Production Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the deployment for production: S3/MinIO for durable media storage, HTTPS via cert-manager, rate limiting on auth endpoints, Sentry error tracking, Prometheus metrics, and a PostgreSQL backup CronJob.

**Architecture:** MinIO runs as a K8s Deployment (single-node, sufficient for small deployments); django-storages routes all media uploads to it. cert-manager issues Let's Encrypt TLS certs via the NGINX Ingress annotation. Rate limiting lives at the Django middleware level using `django-ratelimit`. Sentry SDK hooks into Django signals. `django-prometheus` exposes `/metrics` that a K8s ServiceMonitor scrapes.

**Tech Stack:** django-storages[s3] 1.14, boto3 1.35, django-ratelimit 4.1, sentry-sdk[django] 2.x, django-prometheus 2.3, MinIO (bitnami/minio Helm chart or plain K8s Deployment), cert-manager 1.14

**Prerequisite:** Plan 01 (Code Cleanup + `api` App) must be merged first.

---

## File Map

**Modify:**
- `backend/requirements.txt` — add django-storages, boto3, django-ratelimit, sentry-sdk, django-prometheus
- `backend/config/settings.py` — add storage, rate-limit, sentry, prometheus config
- `backend/apps/accounts/views.py` — add rate limit decorator to token view
- `backend/config/urls.py` — add prometheus metrics URL
- `docker-compose.yml` — add MinIO service

**Create:**
- `k8s/minio/deployment.yaml`
- `k8s/minio/service.yaml`
- `k8s/minio/secret.yaml`
- `k8s/minio/pvc.yaml`
- `k8s/postgres/backup-cronjob.yaml`
- `k8s/monitoring/servicemonitor.yaml`

**Modify:**
- `k8s/ingress.yaml` — add TLS and cert-manager annotations
- `k8s/backend/configmap.yaml` — add new env vars
- `k8s/backend/secret.yaml` — add new secrets

---

### Task 1: S3/MinIO media storage — Django side

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Add to `backend/requirements.txt`**

```
django-storages[s3]==1.14.4
boto3==1.35.74
```

- [ ] **Step 2: Update `backend/config/settings.py`**

Add `'storages'` to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'storages',
]
```

Replace the existing `MEDIA_URL` / `MEDIA_ROOT` block with conditional storage:
```python
# Media storage — local in dev, S3/MinIO in prod
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='tableflow-media')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='')  # e.g. http://minio:9000
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/' if not AWS_S3_CUSTOM_DOMAIN else f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
```

- [ ] **Step 3: Install and verify settings load**

```bash
cd backend
pip install "django-storages[s3]==1.14.4" boto3==1.35.74
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py
git commit -m "feat: add S3/MinIO storage support via django-storages (disabled until USE_S3=True)"
```

---

### Task 2: Add MinIO to `docker-compose.yml`

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Read the current `docker-compose.yml`**

```
docker-compose.yml
```

- [ ] **Step 2: Add MinIO service and update backend env**

Add `minio` service and `createbuckets` init container, and wire `backend` to use it when `USE_S3=True`:

```yaml
services:
  postgres:
    # ... (unchanged)

  minio:
    image: minio/minio:RELEASE.2024-11-07T00-52-20Z
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin123}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 5

  createbuckets:
    image: minio/mc:RELEASE.2024-11-17T19-35-25Z
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin minioadmin123;
      mc mb --ignore-existing local/tableflow-media;
      mc anonymous set public local/tableflow-media;
      exit 0;
      "

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SECRET_KEY: ${SECRET_KEY:-django-insecure-change-me}
      DEBUG: ${DEBUG:-True}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-localhost,127.0.0.1,backend}
      DATABASE_URL: ${DATABASE_URL:-postgresql://tableflow:tableflow_dev_password@postgres:5432/tableflow}
      CORS_ALLOW_ALL_ORIGINS: "True"
      USE_S3: ${USE_S3:-False}
      AWS_ACCESS_KEY_ID: ${MINIO_ROOT_USER:-minioadmin}
      AWS_SECRET_ACCESS_KEY: ${MINIO_ROOT_PASSWORD:-minioadmin123}
      AWS_STORAGE_BUCKET_NAME: tableflow-media
      AWS_S3_ENDPOINT_URL: http://minio:9000
    volumes:
      - media_data:/app/media
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    # ... (unchanged)

volumes:
  postgres_data:
  media_data:
  minio_data:
```

- [ ] **Step 3: Test MinIO starts**

```bash
docker compose up minio createbuckets -d
sleep 5
curl -s http://localhost:9000/minio/health/live && echo " MinIO OK"
```

Expected: `MinIO OK`

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add MinIO service to docker-compose for local S3-compatible storage"
```

---

### Task 3: MinIO K8s deployment

**Files:**
- Create: `k8s/minio/secret.yaml`
- Create: `k8s/minio/pvc.yaml`
- Create: `k8s/minio/deployment.yaml`
- Create: `k8s/minio/service.yaml`

- [ ] **Step 1: Create `k8s/minio/secret.yaml`**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: minio-secret
  namespace: tableflow
type: Opaque
stringData:
  MINIO_ROOT_USER: "minioadmin"
  MINIO_ROOT_PASSWORD: "changeme-in-prod"
  AWS_ACCESS_KEY_ID: "minioadmin"
  AWS_SECRET_ACCESS_KEY: "changeme-in-prod"
```

- [ ] **Step 2: Create `k8s/minio/pvc.yaml`**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: tableflow
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

- [ ] **Step 3: Create `k8s/minio/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: tableflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
        - name: minio
          image: minio/minio:RELEASE.2024-11-07T00-52-20Z
          args: ["server", "/data", "--console-address", ":9001"]
          env:
            - name: MINIO_ROOT_USER
              valueFrom:
                secretKeyRef:
                  name: minio-secret
                  key: MINIO_ROOT_USER
            - name: MINIO_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: minio-secret
                  key: MINIO_ROOT_PASSWORD
          ports:
            - containerPort: 9000
            - containerPort: 9001
          volumeMounts:
            - name: minio-storage
              mountPath: /data
          readinessProbe:
            httpGet:
              path: /minio/health/live
              port: 9000
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "1Gi"
              cpu: "500m"
      volumes:
        - name: minio-storage
          persistentVolumeClaim:
            claimName: minio-pvc
```

- [ ] **Step 4: Create `k8s/minio/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: tableflow
spec:
  selector:
    app: minio
  ports:
    - name: api
      port: 9000
      targetPort: 9000
    - name: console
      port: 9001
      targetPort: 9001
```

- [ ] **Step 5: Update `k8s/backend/secret.yaml` — add S3 credentials**

Add these keys to the existing backend secret:
```yaml
  USE_S3: "True"
  AWS_ACCESS_KEY_ID: "minioadmin"
  AWS_SECRET_ACCESS_KEY: "changeme-in-prod"
  AWS_STORAGE_BUCKET_NAME: "tableflow-media"
  AWS_S3_ENDPOINT_URL: "http://minio:9000"
```

- [ ] **Step 6: Replace emptyDir with PVC in `k8s/backend/deployment.yaml`**

In the existing `deployment.yaml`, change the media volume from `emptyDir` to a PVC.

First create the PVC file `k8s/backend/media-pvc.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backend-media-pvc
  namespace: tableflow
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

Then update `k8s/backend/deployment.yaml` volumes section:
```yaml
      volumes:
        - name: media-storage
          persistentVolumeClaim:
            claimName: backend-media-pvc
```

- [ ] **Step 7: Commit**

```bash
git add k8s/minio/ k8s/backend/secret.yaml k8s/backend/deployment.yaml k8s/backend/media-pvc.yaml
git commit -m "feat: add MinIO K8s deployment; replace backend emptyDir with PVC"
```

---

### Task 4: Rate limiting on auth endpoints

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`
- Modify: `backend/apps/accounts/views.py`

- [ ] **Step 1: Add to `backend/requirements.txt`**

```
django-ratelimit==4.1.0
```

- [ ] **Step 2: Add cache backend to `backend/config/settings.py`**

`django-ratelimit` uses Django's cache. Add a memory cache (sufficient for single-instance deployments; use Redis for multi-replica):

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

RATELIMIT_USE_CACHE = 'default'
```

- [ ] **Step 3: Apply rate limit to login view in `backend/apps/accounts/views.py`**

```python
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST', block=True),
    name='dispatch',
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

This allows a maximum of 10 POST requests per minute per IP. Exceeding it returns HTTP 429.

- [ ] **Step 4: Install and test**

```bash
cd backend
pip install django-ratelimit==4.1.0
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Verify rate limit works (manual)**

```bash
python manage.py runserver &
sleep 2
# Send 11 rapid login attempts — the 11th should return 403
for i in $(seq 1 11); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/auth/token/ \
    -H "Content-Type: application/json" -d '{"username":"x","password":"x"}')
  echo "Request $i: $STATUS"
done
kill %1
```

Expected: requests 1–10 return 401 (wrong creds), request 11 returns 403 (rate limited).

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py backend/apps/accounts/views.py
git commit -m "feat: add rate limiting (10/min per IP) on POST /api/auth/token/"
```

---

### Task 5: HTTPS — cert-manager + TLS in Ingress

**Files:**
- Create: `k8s/cert-manager/cluster-issuer.yaml`
- Modify: `k8s/ingress.yaml`

- [ ] **Step 1: Install cert-manager in the cluster**

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.7/cert-manager.yaml
```

Wait for all cert-manager pods to be ready:
```bash
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/instance=cert-manager \
  -n cert-manager --timeout=120s
```

Expected: `pod/... condition met` for 3 pods.

- [ ] **Step 2: Create `k8s/cert-manager/cluster-issuer.yaml`**

Replace `your-email@example.com` with the actual email (used by Let's Encrypt for expiry notices):

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
```

Apply it:
```bash
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
kubectl get clusterissuer letsencrypt-prod
```

Expected: `READY True`

- [ ] **Step 3: Update `k8s/ingress.yaml` to add TLS**

Replace the existing `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tableflow-ingress
  namespace: tableflow
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - tableflow.example.com
      secretName: tableflow-tls
  rules:
    - host: tableflow.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /admin
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /media
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

- [ ] **Step 4: Apply and verify certificate is issued**

```bash
kubectl apply -f k8s/ingress.yaml
# Wait up to 2 minutes for cert to be issued
kubectl get certificate -n tableflow --watch
```

Expected: `tableflow-tls` shows `READY True`.

- [ ] **Step 5: Commit**

```bash
git add k8s/cert-manager/ k8s/ingress.yaml
git commit -m "feat: add cert-manager ClusterIssuer + TLS in Ingress (Let's Encrypt)"
```

---

### Task 6: Sentry error tracking

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Add to `backend/requirements.txt`**

```
sentry-sdk[django]==2.19.2
```

- [ ] **Step 2: Update `backend/config/settings.py`**

Add Sentry initialization (at the bottom of the file, after all other settings):

```python
SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    import logging

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config('SENTRY_ENVIRONMENT', default='production'),
    )
```

- [ ] **Step 3: Add structured logging (always on, not just Sentry)**

Add a `LOGGING` dict to `settings.py` for structured JSON logs in production:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('LOG_LEVEL', default='WARNING'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='WARNING'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

- [ ] **Step 4: Add `SENTRY_DSN` to K8s secret**

In `k8s/backend/secret.yaml`, add:
```yaml
  SENTRY_DSN: ""        # fill in from Sentry project settings
  SENTRY_ENVIRONMENT: "production"
  LOG_LEVEL: "WARNING"
```

- [ ] **Step 5: Install and verify**

```bash
cd backend
pip install "sentry-sdk[django]==2.19.2"
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py k8s/backend/secret.yaml
git commit -m "feat: add Sentry error tracking and structured console logging"
```

---

### Task 7: Prometheus metrics

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`
- Create: `k8s/monitoring/servicemonitor.yaml`

- [ ] **Step 1: Add to `backend/requirements.txt`**

```
django-prometheus==2.3.1
```

- [ ] **Step 2: Update `backend/config/settings.py`**

Add `'django_prometheus'` as the first and last entries in `INSTALLED_APPS` and `MIDDLEWARE`:

```python
INSTALLED_APPS = [
    'django_prometheus',   # FIRST
    'django.contrib.admin',
    ...
    'apps.api',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',   # FIRST
    'django.middleware.security.SecurityMiddleware',
    ...
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',    # LAST
]
```

- [ ] **Step 3: Add metrics URL to `backend/config/urls.py`**

```python
urlpatterns = [
    ...
    path('', include('django_prometheus.urls')),  # exposes /metrics
]
```

- [ ] **Step 4: Install and test**

```bash
cd backend
pip install django-prometheus==2.3.1
python manage.py runserver &
sleep 2
curl -s http://localhost:8000/metrics | head -5
kill %1
```

Expected: first few lines of Prometheus text format (e.g. `# HELP django_...`).

- [ ] **Step 5: Create `k8s/monitoring/servicemonitor.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tableflow-backend
  namespace: tableflow
  labels:
    app: backend
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

Also add a named port `http` to `k8s/backend/service.yaml`:
```yaml
spec:
  selector:
    app: backend
  ports:
    - name: http
      port: 8000
      targetPort: 8000
```

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/config/settings.py backend/config/urls.py \
        k8s/monitoring/ k8s/backend/service.yaml
git commit -m "feat: add django-prometheus metrics at /metrics + K8s ServiceMonitor"
```

---

### Task 8: PostgreSQL backup CronJob

**Files:**
- Create: `k8s/postgres/backup-cronjob.yaml`

- [ ] **Step 1: Create `k8s/postgres/backup-cronjob.yaml`**

This job runs `pg_dump` nightly at 02:00 UTC and uploads the dump to MinIO using the `mc` CLI:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: tableflow
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: postgres:16-alpine
              command:
                - /bin/sh
                - -c
                - |
                  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                  DUMP_FILE="/tmp/tableflow_${TIMESTAMP}.sql.gz"
                  pg_dump "$DATABASE_URL" | gzip > "$DUMP_FILE"
                  # Upload to MinIO
                  wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
                  chmod +x /tmp/mc
                  /tmp/mc alias set minio http://minio:9000 "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
                  /tmp/mc mb --ignore-existing minio/tableflow-backups
                  /tmp/mc cp "$DUMP_FILE" "minio/tableflow-backups/$(basename $DUMP_FILE)"
                  echo "Backup uploaded: $(basename $DUMP_FILE)"
                  # Retain only last 30 backups
                  /tmp/mc ls minio/tableflow-backups/ | sort | head -n -30 | awk '{print $NF}' | \
                    xargs -I{} /tmp/mc rm "minio/tableflow-backups/{}" 2>/dev/null || true
              env:
                - name: DATABASE_URL
                  valueFrom:
                    secretKeyRef:
                      name: backend-secret
                      key: DATABASE_URL
                - name: MINIO_ACCESS_KEY
                  valueFrom:
                    secretKeyRef:
                      name: minio-secret
                      key: MINIO_ROOT_USER
                - name: MINIO_SECRET_KEY
                  valueFrom:
                    secretKeyRef:
                      name: minio-secret
                      key: MINIO_ROOT_PASSWORD
              resources:
                requests:
                  memory: "64Mi"
                  cpu: "50m"
                limits:
                  memory: "256Mi"
                  cpu: "200m"
```

- [ ] **Step 2: Test the job manually**

```bash
kubectl apply -f k8s/postgres/backup-cronjob.yaml

# Trigger a manual run
kubectl create job --from=cronjob/postgres-backup postgres-backup-manual -n tableflow

# Watch the pod
kubectl get pods -n tableflow -l job-name=postgres-backup-manual --watch
```

Expected: pod completes with `STATUS = Completed`.

Check logs:
```bash
kubectl logs -n tableflow -l job-name=postgres-backup-manual
```

Expected: `Backup uploaded: tableflow_YYYYMMDD_HHMMSS.sql.gz`

- [ ] **Step 3: Commit**

```bash
git add k8s/postgres/backup-cronjob.yaml
git commit -m "feat: add nightly PostgreSQL backup CronJob to MinIO"
```
