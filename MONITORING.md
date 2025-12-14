# 📊 Monitoring Guide - Prometheus + Grafana

## Quick Start

### 1. Start monitoring stack

**Development:**
```bash
docker compose -f docker-compose.yml \
               -f docker-compose.override.yml \
               -f docker-compose.monitoring.yml up -d
```

**Production:**
```bash
docker compose -f docker-compose.yml \
               -f docker-compose.prod.yml \
               -f docker-compose.monitoring.yml up -d
```

### 2. Access dashboards

**Local development:**
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

**Production (via SSH tunnel):**
```bash
# Grafana
ssh -L 3000:localhost:3000 azureuser@<VM_IP>

# Prometheus
ssh -L 9090:localhost:9090 azureuser@<VM_IP>
```

Then open:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

### 3. Login to Grafana

**Default credentials:**
- Username: `admin`
- Password: `admin123` (change in production!)

**Change password:**
Set `GRAFANA_ADMIN_PASSWORD` environment variable in `.env`

---

## 📈 Available Metrics

### HTTP Metrics (Auto-tracked)

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request duration distribution |
| `http_requests_in_progress` | Gauge | Currently processing requests |

### Application Metrics (Backend)

| Metric | Type | Description |
|--------|------|-------------|
| `snippetly_active_users` | Gauge | Users active in last 24h |
| `snippetly_total_snippets` | Gauge | Total code snippets |
| `snippetly_database_connections` | Gauge | Active DB connections |

---

## 🔍 Useful Queries (PromQL)

### Request Rate
```promql
# Requests per second by endpoint
rate(http_requests_total[5m])

# Requests per second by status code
sum by (status_code) (rate(http_requests_total[5m]))
```

### Response Time
```promql
# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average response time
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

### Error Rate
```promql
# 5xx error rate
sum(rate(http_requests_total{status_code=~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))

# 4xx error rate
sum(rate(http_requests_total{status_code=~"4.."}[5m])) /
sum(rate(http_requests_total[5m]))
```

---

## 📊 Grafana Dashboards

### Pre-configured Dashboards

1. **Snippetly Overview** (auto-loaded)
   - HTTP request rate
   - 95th percentile response time
   - Error rates
   - Active users

### Import Community Dashboards

Great ready-made dashboards:

1. **FastAPI Dashboard**
   - ID: `14352`
   - Import: Dashboards → Import → Enter ID

2. **PostgreSQL Dashboard**
   - ID: `9628`
   - Import: Dashboards → Import → Enter ID

3. **Redis Dashboard**
   - ID: `11835`
   - Import: Dashboards → Import → Enter ID

---

## 🎯 Custom Metrics (Backend)

Add custom metrics to your code:

```python
from src.middleware.prometheus import total_snippets, active_users

# Increment snippet count
total_snippets.inc()

# Set active user count
active_users.set(count)

# Custom counter
from prometheus_client import Counter

user_signups = Counter('user_signups_total', 'Total user signups')
user_signups.inc()
```

---

## 🚨 Alerting (Optional)

### Add Alert Rules

Create `infra/prometheus/alerts/backend.yml`:

```yaml
groups:
  - name: backend
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile is {{ $value }}s"
```

Update `prometheus.yml`:
```yaml
rule_files:
  - "alerts/*.yml"
```

---

## 🔧 Maintenance

### Check Prometheus Targets

Visit http://localhost:9090/targets

All targets should be **UP** (green).

### View Metrics Directly

Backend metrics endpoint:
```bash
curl http://localhost:8000/api/metrics
```

### Retention Policy

- Prometheus retains data for **30 days** (configurable)
- Grafana stores dashboards permanently in volume

### Backup Dashboards

```bash
# Export all dashboards
docker exec snippetly-grafana grafana-cli admin export-dashboard > dashboards.json
```

---

## 🎓 Learning Resources

- [Prometheus Basics](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

## ⚠️ Production Tips

1. **Secure Access:**
   - ✅ Already bound to localhost
   - Access only via SSH tunnel
   - Don't expose 9090/3000 to internet

2. **Resource Limits:**
   - ✅ Already configured (512MB Prometheus, 256MB Grafana)
   - Monitor memory usage

3. **Backup:**
   - Grafana data in `/var/lib/grafana` volume
   - Backup dashboards regularly

4. **Change Default Password:**
   ```bash
   # In .env file
   GRAFANA_ADMIN_PASSWORD=your-secure-password
   ```

5. **Disable Anonymous Access:**
   Already disabled (`GF_USERS_ALLOW_SIGN_UP=false`)

---

## 🐛 Troubleshooting

**Metrics not appearing:**
1. Check backend is running: `docker ps | grep backend`
2. Check metrics endpoint: `curl http://localhost:8000/api/metrics`
3. Check Prometheus targets: http://localhost:9090/targets

**Grafana not loading:**
1. Check container: `docker logs snippetly-grafana`
2. Verify provisioning: `/etc/grafana/provisioning`

**High memory usage:**
1. Reduce retention: `--storage.tsdb.retention.time=15d`
2. Increase scrape interval: `scrape_interval: 30s`
