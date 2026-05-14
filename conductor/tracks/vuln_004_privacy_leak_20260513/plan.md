# Implementation Plan: VULN-004 Remediation

## Phase 1: Research & Audit
- [x] Document every instance where data is sent to a remote service. (71c6083)
- [x] Identify which PII is included in each request. (71c6083)

## Phase 2: Implementation
- [x] Add URL validation logic to `engines/config.py`. (323bced)
- [x] Update `TaiMenu` to show a warning when remote services are enabled. (2ed1310)
- [x] Implement a "Privacy Mode" setting to redact PII before sending if possible. (43f88cc)

## Phase 3: Validation
- [x] Verify that non-HTTPS URLs are rejected or trigger a strong warning. (323bced)
- [x] Confirm the UI correctly reflects the status of remote data transmission. (2ed1310)
- [x] Verify PII redaction in remote transmission via tests. (43f88cc)
