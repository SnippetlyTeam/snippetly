#!/bin/bash
#
# setup-https-prod.sh
# One-time script to obtain Let's Encrypt certificates for production VM
#
# This script should be run ONCE on the production VM after initial deployment
# to obtain SSL certificates from Let's Encrypt.
#
# Prerequisites:
# - Production VM is deployed and accessible at snippetly.codes
# - DNS A record for snippetly.codes points to the production VM IP (172.201.26.148)
# - docker-compose.yml and docker-compose.prod.yml are present in ~/snippetly
# - Certbot data directories exist at /opt/app-data/certbot/{conf,www}
#
# Usage:
#   ssh into production VM, then run:
#   cd ~/snippetly
#   sudo bash scripts/setup-https-prod.sh your-email@example.com
#

set -euo pipefail

# Check if email is provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <email-for-letsencrypt>"
  echo "Example: $0 admin@snippetly.codes"
  exit 1
fi

EMAIL="$1"
DOMAIN="snippetly.codes"
CERTBOT_DATA_DIR="/opt/app-data/certbot"

echo "=========================================="
echo "Setting up HTTPS for $DOMAIN"
echo "Email: $EMAIL"
echo "=========================================="

# Ensure we're in the right directory
cd ~/snippetly

# Step 1: Start the stack WITHOUT nginx-proxy first (to avoid cert errors)
echo ""
echo "Step 1: Starting services without nginx-proxy..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps \
  db redis mongodb backend celery-worker celery-beat frontend certbot

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Step 2: Start nginx-proxy temporarily in HTTP-only mode to pass ACME challenge
echo ""
echo "Step 2: Obtaining initial Let's Encrypt certificate..."

# Create temporary nginx config that ONLY serves ACME challenge (no HTTPS yet)
cat > /tmp/temp-nginx-http-only.conf << 'EOF'
server {
    listen 80;
    server_name snippetly.codes www.snippetly.codes;

    # ACME challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Temporary redirect for everything else
    location / {
        return 503 "Certificate setup in progress";
    }
}
EOF

# Start nginx with temporary config
docker run -d --rm \
  --name snippetly-nginx-temp \
  --network snippetly-net \
  -p 80:80 \
  -v /tmp/temp-nginx-http-only.conf:/etc/nginx/conf.d/default.conf:ro \
  -v ${CERTBOT_DATA_DIR}/www:/var/www/certbot:ro \
  nginx:1.25-alpine

echo "Temporary nginx started for ACME challenge..."
sleep 5

# Request certificate using certbot
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot \
  certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email "${EMAIL}" \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  -d "${DOMAIN}" \
  -d "www.${DOMAIN}"

# Stop temporary nginx
echo ""
echo "Step 3: Stopping temporary nginx..."
docker stop snippetly-nginx-temp || true
rm -f /tmp/temp-nginx-http-only.conf

# Step 4: Start the full production stack with HTTPS
echo ""
echo "Step 4: Starting full production stack with HTTPS..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "=========================================="
echo "HTTPS setup complete!"
echo "=========================================="
echo ""
echo "Your site should now be accessible at:"
echo "  https://${DOMAIN}"
echo ""
echo "Certificate details:"
ls -lh ${CERTBOT_DATA_DIR}/conf/live/${DOMAIN}/ || true
echo ""
echo "Certificates will auto-renew via the certbot container."
echo "Renewal checks run twice daily, and nginx reloads automatically on renewal."
echo ""
echo "To verify HTTPS:"
echo "  curl -I https://${DOMAIN}"
echo ""
