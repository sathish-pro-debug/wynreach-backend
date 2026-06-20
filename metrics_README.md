Metrics endpoints and example .env

Add to your backend `.env` (example):

# Enable debug metrics
DEBUG=True

# Protect debug endpoints with an API key (optional). If set, pass header X-Metrics-Api-Key:
METRICS_API_KEY=supersecretmetricskey

# Alternatively require an admin JWT to access Prometheus endpoint
SECRET_KEY=your_app_secret_key
ALGORITHM=HS256

# Enable Prometheus exporter (internal network only)
PROMETHEUS_ENABLED=True

Admin JWT example payload (use your `SECRET_KEY`):
{
  "sub": "admin@yourdomain",
  "is_admin": true,
  "exp": 1712345678
}

Generate a token using your usual tooling. The `/api/metrics/prometheus` endpoint accepts either a valid admin JWT (Authorization: Bearer <token>) or the `X-Metrics-Api-Key` header if configured.
