# Non-Functional Requirements & Architecture

This document captures the non-functional requirements (NFRs), security considerations, architectural updates, and technical constraints for the digital onboarding application, as extracted from the provided project data (Attaq-423).

## 1. Security & Threat Prevention
*   **Content Security Policy (CSP):** Implement a cryptographic nonce in the HTML tags for the public website to mitigate Cross-Site Scripting (XSS) risks.
*   **Dependency Vulnerabilities:** Resolve critical Handlebars.js template injection vulnerabilities detected by security scanners.
*   **Tokenization & Secrets Management:** Move Alloy API keys and Journey IDs away from hardcoded frontend `.ts` files into a secure `.env` file structure (`environment.ts` automatically generated via `generate-env.js`). All development configuration must follow the production tokenization pattern.
*   **Session Management:** Implement secure session termination upon clicking the "Logout" button. This must immediately invalidate the active API token, completely clear the frontend client cache, and ensure backwards navigation routing prevents viewing authenticated screens.
*   **Consent Auditing:** Ensure explicit timestamps and audit trails are recorded for all E-Sign, TCPA, and KYC consents executed during the Docusign flows.

## 2. Configuration & Feature Flagging
*   **Feature Flag Management:** Introduce configurable feature flags via the backend GraphQL configuration repository (no UI deployments required to toggle):
    *   `enableBODebitCard`: Controls the rendering of the Debit Card option on the Beneficial Owners page. Default: ON.
    *   `enableBOAuthorizedUser`: Controls the "Other" radio option on the Control Prong page. Default: ON.
    *   `enabledAuthorizedUsers`: Controls the Authorized Signers section on the Complete Your Profile page. Default: OFF.

## 3. Data Integrity & API Handling
*   **Salesforce Payload Formatting:** The phone number submitted to the Salesforce Lead API must be programmatically scrubbed and formatted as a strict, linear string of digits (e.g., `8011234567`) to prevent ingestion errors. Object `RecordType` must strictly evaluate to `Deposit_Account_Opening`.
*   **Cache vs. Hardcoding:** The architecture must strictly avoid hardcoded data payloads on the Complete Your Profile page. All data transmitted to Salesforce must be retrieved from the active user's session cache (e.g., `annual_revenue` and `business_story`).

## 4. Systems Integration & Analytics
*   **Alloy Orchestration:** Maintain idempotency for the Alloy "Get Started" API call. Do not re-trigger the Alloy journey upon form resubmissions if the cached payload data has not been modified by the user. Ensure Alloy Action Nodes ("Pending OTP") are reliably updated with `Approved` or `Denied` states based on Transmit MFA events.
*   **Email Tracking (SFMC):** All system-generated emails must include tracking IDs/UTMs for opens, click-throughs, and unsubscribes. SFMC reporting must validate these metrics accurately across all lead and winback campaign cadences.

## 5. Architecture Documentation
*   **System Diagram Updates:** Update the DAO Technical Sequence Diagram (Architecture Diagram) to accurately reflect the implementation of Transmit as the primary Identity/MFA provider replacing initial Alloy OTP flows, as well as updated interactions with Salesforce and Docusign.
