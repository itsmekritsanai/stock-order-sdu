# Needs Validation: Run 2 (v3.0.6)

This document tracks security assumptions and external deployment conditions that cannot be decisively established through local source code inspection alone.

---

## 1. Production Reverse Proxy & TLS Termination

- **Assumption:** The Python HTTP server (`backend/server.py`) is deployed behind a production reverse proxy (e.g. Nginx, Caddy, or Cloudflare Tunnel) that handles TLS termination (HTTPS) and enforces rate limiting.
- **Risk if False:** If `server.py` is exposed directly to the public Internet without HTTPS, cleartext HTTP traffic can be intercepted, exposing staff tokens and user passwords over the wire.
- **Validation Steps:**
  1. Inspect the production web server configuration (e.g. `/etc/nginx/sites-enabled/*` or Cloudflare ingress configuration).
  2. Verify that port 8080 is bound only to `127.0.0.1` and not accessible from external interfaces.
  3. Confirm HTTP Strict Transport Security (HSTS) headers are added by the reverse proxy.

---

## 2. Environment Variable Secret Rotation

- **Assumption:** Production deployments override `STAFF_AUTH_SECRET`, `DB_PASSWORD`, and `STAFF_PASSWORD` using secure, non-default values via real environment variables or a sealed `.env` file.
- **Risk if False:** Anyone with knowledge of the default repository placeholders can authenticate as staff or connect to the database.
- **Validation Steps:**
  1. Verify the production `.env` file permissions (`chmod 600 .env`).
  2. Confirm `STAFF_AUTH_SECRET` contains at least 32 bytes of cryptographically secure random data.

