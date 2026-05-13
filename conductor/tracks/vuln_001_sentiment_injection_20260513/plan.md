# Implementation Plan: VULN-001 Remediation

## Phase 1: Research & Reproduction
- [ ] Create a test case to demonstrate prompt injection in `get_sentiment_score`.

## Phase 2: Implementation
- [ ] Refactor `get_sentiment_score` to use a safer prompt template.
- [ ] Add input sanitization to remove common injection patterns.

## Phase 3: Validation
- [ ] Verify that the test case now fails to inject instructions.
- [ ] Ensure normal sentiment scoring still works as expected.
