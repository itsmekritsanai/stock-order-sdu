# Needs Validation (Audit Run 1)

All security candidates investigated during this run were successfully validated and brought to a definitive verdict (`confirmed` or `covered/clean`). There are no unresolved candidates blocked on missing capabilities or unverified states.

## Future Review & Deployment Checks (Operational Recommendations)

The following items are outside the local source repository scope and should be verified when deploying to university infrastructure:

1. **Reverse Proxy & TLS Termination:**
   - **Boundary:** Production network ingress.
   - **Check:** Verify that Nginx or Apache acts as reverse proxy terminating HTTPS/TLS with valid certificates and enforcing HSTS headers.
2. **Rate Limiting & DoS Protection:**
   - **Boundary:** Inbound HTTP requests.
   - **Check:** Ensure reverse proxy or web application firewall (WAF) enforces rate limiting on `/api` (particularly `loginStaff` and `loginUser` to prevent brute force attacks).
3. **Database Network Isolation:**
   - **Boundary:** PostgreSQL port 5432/5433.
   - **Check:** In production, bind PostgreSQL exclusively to the internal Docker network or `127.0.0.1`, rather than exposing it across host interfaces.

