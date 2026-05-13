# Implementation Plan: VULN-004 Remediation

## Phase 1: Research & Audit
- [ ] Document every instance where data is sent to a remote service.
- [ ] Identify which PII is included in each request.

## Phase 2: Implementation
- [ ] Add URL validation logic to `engines/config.py`.
- [ ] Update `TaiMenu` to show a warning when remote services are enabled.
- [ ] Implement a "Privacy Mode" setting to redact PII before sending if possible.

## Phase 3: Validation
- [ ] Verify that non-HTTPS URLs are rejected or trigger a strong warning.
- [ ] Confirm the UI correctly reflects the status of remote data transmission.
