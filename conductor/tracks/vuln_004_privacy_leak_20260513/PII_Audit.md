# PII Remote Transmission Audit

This document tracks all instances where Personally Identifiable Information (PII) or sensitive user data is sent to remote services.

## Remote Services and Data Transmission

### 1. Remote LLM Service (`remote_llm_url`)
- **Endpoints:**
  - `/chat`: Receives full chat history (PII), including user messages and AI responses. Used for response generation.
  - `/sync_lore`: Receives entire Lorebook data. May contain sensitive world information or character details.
- **PII Type:** Chat logs, user-defined character information, lore.

### 2. Remote TTS Service (`remote_tts_url`)
- **Endpoints:**
  - `/upload_speaker`: Receives voice sample files (.wav). This is highly sensitive biometric-like data used for voice cloning.
  - `/generate_tts`: Receives text to be synthesized into speech. This text can contain user input or character-specific dialogue.
- **PII Type:** Voice samples (biometric), synthesized text content.

## Identified Privacy Risks
- **Unencrypted Transmission:** If the remote URLs are configured with `http` instead of `https`, all PII is sent in plain text across the network.
- **Unvalidated Endpoints:** The application does not verify if the remote endpoint is trustworthy before sending data.
- **Lack of User Consent:** Users are not explicitly warned when data is about to leave their local machine.
