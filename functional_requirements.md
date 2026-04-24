# Functional Requirements: Digital Onboarding Flow (DAO)

This document captures the comprehensive functional requirements for the end-to-end digital onboarding application (DAO), combining the full UI/UX flow from the Figma asset with specific business rules and system integrations.

## 1. Global UI/UX Elements
*   **Header Integration:** 
    *   Display a greeting with the user's first name (pulled from cache/Salesforce).
    *   Include a "Logout" button in the top-right corner on all post-credential pages (Identity Details through terms).
    *   **Logout Behavior:** Invalidates the session token, clears the client cache, redirects to Login, and prevents browser back-navigation to authenticated screens.
*   **Master Footer:**
    *   Copyright text: "© 2026 Clover Network LLC...".
    *   Promotional dates: "4/1/2026 to 12/31/2026".
    *   ZiFi logo must include the ™ mark.
    *   Social Media Links: LinkedIn, Facebook, Instagram, YouTube (remove X/Twitter).
    *   Ensure visually consistent disclaimer padding across all viewports.
*   **Support Hub:** Modal available throughout the flow for users to contact support.

## 2. End-to-End Application Flow
The application process follows a strict linear sequence, guiding users through personal and business data collection.

### Step 1: Welcome & Get Started
*   **Purpose:** Lead capture and enrollment initiation.
*   **UI Components:**
    *   Primary header: "One simple signup. Two powerful deposit accounts. Open both in about 10 minutes.*" (with footer disclaimer).
    *   Fields: First Name, Last Name, Email, Phone Number (must be formatted to indicate U.S. domestic).
    *   SMS Consent Checkbox: Must match legally approved text with working `www` links to SMS Terms and Privacy Policy.
*   **Logic & Routing:**
    *   Query Transmit `IsUser` API on submit.
    *   *Match Scenarios:* If Email exists/Phone differs OR Phone exists/Email differs: Show error toast and create Salesforce Lead. If both exist: Route to Login via `DAORoutedLogin`.
    *   *New User:* Trigger Alloy Get Started workflow, create Salesforce Lead (`RecordType: Deposit_Account_Opening`, scrubbed phone number `8011234567`), Create User in Transmit, and proceed to OTP.
    *   *Back Button Support:* Pre-fill data using cached GUID if user returns from the OTP page.

### Step 2: Mobile Verification (OTP)
*   **Purpose:** Verify user phone number via Transmit OTP.
*   **Logic (Alloy Update):** 
    *   Update Alloy "Pending OTP" action node upon completion.
    *   Set outcome to `Approved` if successful.
    *   Set outcome to `Denied` for terminal failures (e.g., 3 failed attempts).

### Step 3: Identity Details
*   **Purpose:** Capture primary applicant's personal information.
*   **UI Components:** Legal Name, DOB, SSN, Home Address, Residency status.
*   **Specific Rules:** Residency dropdown must include "US Citizen or National".

### Step 4: Business Details
*   **Purpose:** Core business identity information.
*   **UI Components:** Legal Business Name, DBA (Help text: "...or owner's surname"), Entity Type, Applicant Role, Business Address.
*   **Specific Rules:** 
    *   Entity Type descriptions: Sole Proprietorship ("A simple business generally owned and operated by one person"), Other Entity Types ("A business generally with multiple owners or a more structured legal setup").
    *   Role list must include "Managing Member".
    *   Sole Owner help text must include "...or domestic partner".

### Step 5: Additional Details / Business Activities
*   **Purpose:** Compliance and industry classification.
*   **UI Components:** Industry, NAICS codes, Business Story, Annual Revenue.
*   **Data Mapping:** `annual_revenue` (Picklist) and `business_story` (String) map directly to Salesforce `Account` object via cache (no hardcoding).

### Step 6: Business Ownership (Beneficial Owners)
*   **Purpose:** Identify individuals with >25% ownership.
*   **UI Components:** Add up to 5 Beneficial Owners. Captures Name, DOB, SSN, Address, Ownership %.
*   **Specific Rules:** 
    *   A "Debit Card" checkbox is available for owners but controlled by the GraphQL feature flag `enableBODebitCard`.

### Step 7: Controlling Party (Control Prong)
*   **Purpose:** Identify the individual with significant responsibility for managing the entity.
*   **Specific Rules:** The "Other" role radio button is controlled by the GraphQL feature flag `enableBOAuthorizedUser`.

### Step 8: Complete Your Profile (Review & Submit)
*   **Purpose:** Final review of data, capturing required account features before submission.
*   **Specific Rules:**
    *   **Removed Sections:** The "Additional Services" section (International ATM checkbox, check writing) is completely removed.
    *   **Validation:** Strict required-field enforcement is removed. Allow submission if at least one field is populated.
    *   **Authorized Signers:** This section is hidden by default and controlled by the GraphQL feature flag `enabledAuthorizedUsers`.

## 3. Post-Submission & Provisioning
*   **Transmit End of Journey:**
    *   Upon completion, set `onboarding_complete: true` and `reason: "activated"` in Transmit.
    *   Configure MFA: `email_enabled` (true), `sms_enabled` (true), `totp_enabled` (false).
    *   Set `notificationChannels` to `["email"]`.
*   **OMB Redirection:** Users can log into the Online Mobile Banking (OMB) platform immediately using their DAO credentials.

## 4. Docusign Identity Verification & Loan Workflows
*   **Verification:** Manual Docusign flow using Docusign Liveness (front/back ID + selfie) for primary applicant and all guarantors.
*   **Consent:** Explicit E-sign checkbox required before rendering the TCPA/SMS/KYC consent document. Timestamps must be recorded for auditability.
*   **Loan Documents:** Primary package includes W-9 and ACH Form (mobile verification only). Standalone templates provided for Guarantor W-9s and applicant SBA 1919s.

## 5. Communications & Marketing Automation (SFMC)
*   **Lead Campaign:** Targets drop-offs at the Get Started page. Sequence: Email 1 (Immediate), Email 2 (Day 3), Email 3 (Day 7), Email 4 (Day 15).
*   **Winback Campaign:** Targets applicants dropping off post-Identity Details. 4-email sequence emphasizing saved progress and account benefits.
*   **Decline Communication:** Automated email triggered upon application "Declined" status in Salesforce, dynamically populating the applicant's name.

## 6. Appendix: Public Website Maintenance
*   **Routing:** `/support` redirects to `/contactus`.
*   **SBA / Business Checking / Merchant / Terminals Pages:** Minor text adjustments (commas, footnotes, exact Visa ATM text).
*   **Hardware:** Remove deprecated FD 150 and Verifone hardware sections completely.
