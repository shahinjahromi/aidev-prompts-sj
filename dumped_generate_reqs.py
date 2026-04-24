import os

FR_PATH = r"c:\Users\ShahinJahromi\aidev-prompts-sj\dao-poc-alloy\ado-poc-alloy-ai-blueprint\01-requirements\01-pending-promotion\functional_requirements.yaml"
NFR_PATH = r"c:\Users\ShahinJahromi\aidev-prompts-sj\dao-poc-alloy\ado-poc-alloy-ai-blueprint\01-requirements\01-pending-promotion\nfr-and-global-cr\nfr-and-global-cr.yaml"

fr_yaml = """schema_version: 1
type: functional_requirements
items:
- id: FR-0000001-header-integration
  text: Display greeting with user's first name, include a logout button, and ensure logout invalidates token/redirects to Login.
  section: 1. Global UI/UX Elements
  acceptance_criteria:
  - id: AC-0000001-header-integration
    title: Header is correct and Logout works
    criteria:
    - User's first name is shown
    - Logout button is present in the top-right
    - Clicking logout invalidates the session token, clears cache, and redirects to Login
    scenarios:
    - name: Logout click
      given: A user is logged in
      when: They click Logout
      then: Token is invalidated, cache is cleared, redirected to login
  acceptance_tests:
  - id: AT-0000001-header-integration
    name: E2E Logout Flow
    steps:
    - Navigate to Dashboard after login
    - Verify first name in header
    - Click Logout button
    - Assert session token is removed
    - Assert redirection to Login page
    - Attempt back navigation and assert it's blocked
    expected_result: User is successfully logged out and cannot return.

- id: FR-0000002-master-footer
  text: Display correct master footer including copyright, dates, ZiFi logo, and specific social links.
  section: 1. Global UI/UX Elements
  acceptance_criteria:
  - id: AC-0000002-master-footer
    title: Footer renders correctly
    criteria:
    - Copyright text is correct
    - Promotional dates match requirements
    - ZiFi logo has TM
    - X/Twitter is removed
    scenarios:
    - name: Standard render
      given: The application loads
      when: The footer is rendered
      then: All elements match requirements
  acceptance_tests:
  - id: AT-0000002-master-footer
    name: E2E Footer Element Check
    steps:
    - Navigate to Home Page
    - Scroll to footer
    - Assert copyright text exactly matches expected
    - Assert promotional dates exactly match expected
    - Assert ZiFi logo has TM
    - Assert social links include LinkedIn, Facebook, Instagram, YouTube and do NOT include Twitter
    expected_result: Footer elements are present and correct.

- id: FR-0000003-support-hub
  text: Support Hub modal is available throughout the flow.
  section: 1. Global UI/UX Elements
  acceptance_criteria:
  - id: AC-0000003-support-hub
    title: Support Modal works
    criteria:
    - Modal opens on click
    - Modal available in all flows
    scenarios:
    - name: Open modal
      given: User is anywhere in flow
      when: They click support
      then: Modal opens
  acceptance_tests:
  - id: AT-0000003-support-hub
    name: E2E Support Modal
    steps:
    - Navigate to Get Started
    - Click Support
    - Assert modal is visible
    - Close modal
    expected_result: Modal displays properly.

- id: FR-0000004-welcome-get-started
  text: Get Started captures first/last name, email, phone. Queries Transmit and creates Lead if dupes found, else creates Lead and User and goes to OTP.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000004-welcome-get-started
    title: Lead capture and routing logic
    criteria:
    - Fields are correctly captured
    - Transmit is queried
    - SF Lead created if phone/email partial match, shows toast
    - New User triggers Alloy get started, SF lead, Transmit user, routes to OTP
    scenarios:
    - name: New User scenario
      given: A new user
      when: They submit valid data
      then: Alloy, SF, Transmit are triggered, routed to OTP
  acceptance_tests:
  - id: AT-0000004-welcome-get-started
    name: E2E Get Started New User
    steps:
    - Navigate to Get Started
    - Fill out Name, Email, Phone
    - Check SMS consent
    - Submit
    - Verify API calls to Transmit and Alloy
    - Assert redirected to OTP
    expected_result: User routed to OTP and external services invoked.

- id: FR-0000005-otp
  text: Verify user phone via Transmit OTP. Updates Alloy action node to Approved or Denied.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000005-otp
    title: OTP verification works
    criteria:
    - Code is sent to phone
    - Alloy action node is updated to Approved upon success
    scenarios:
    - name: Successful OTP
      given: User is on OTP page
      when: Valid code entered
      then: Alloy node is updated Approved
  acceptance_tests:
  - id: AT-0000005-otp
    name: E2E Successful OTP
    steps:
    - Enter random valid length OTP
    - Mock Transmit success
    - Submit OTP
    - Assert Alloy action node gets Approved status
    - Assert next page transition
    expected_result: OTP verified successfully.

- id: FR-0000006-identity-details
  text: Capture primary applicant's personal info, residency must include US Citizen.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000006-identity-details
    title: Identity details fields
    criteria:
    - Name, DOB, SSN, Home Address, Residency are present
    - Residency includes US Citizen or National
    scenarios:
    - name: Standard render
      given: User on ID details
      when: Page loaded
      then: US Citizen is in dropdown
  acceptance_tests:
  - id: AT-0000006-identity-details
    name: E2E ID Details
    steps:
    - Load ID details page
    - Fill Name, DOB, SSN, Address
    - Select US Citizen from Residency
    - Submit form
    - Assert success
    expected_result: Information gathered correctly.

- id: FR-0000007-business-details
  text: Core business identity. Includes Specific Entity Type descriptions and Managed Member Role.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000007-business-details
    title: Business details fields
    criteria:
    - Entity types are described
    - Managing Member is an option
    - Sole Owner help text is present
    scenarios:
    - name: Standard render
      given: User on business details
      when: Page loaded
      then: Descriptions match requirements
  acceptance_tests:
  - id: AT-0000007-business-details
    name: E2E Biz Details
    steps:
    - Load Biz details page
    - Verify Entity Type descriptions
    - Verify Managing Member role in list
    - Verify Sole Owner help text
    - Submit valid form
    - Assert success
    expected_result: Business details gathered correctly.

- id: FR-0000008-additional-biz-details
  text: Capture compliance info. Map annual_revenue and business_story directly to Salesforce Acct via cache.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000008-additional-biz-details
    title: Additional Biz Details mapping
    criteria:
    - Fields mapped to cache correctly
    scenarios:
    - name: Submit details
      given: User fills revenue and story
      when: Submits form
      then: Cache retains exact values for SF
  acceptance_tests:
  - id: AT-0000008-additional-biz-details
    name: E2E Additional Biz Details
    steps:
    - Load Additional details page
    - Fill Industry, NAICS, Story, Revenue
    - Submit form
    - Assert cache contains story and revenue explicitly
    expected_result: Data cached accurately for Salesforce.

- id: FR-0000009-beneficial-owners
  text: Identify individuals with >25% ownership. Debit Card checkbox controlled by enableBODebitCard.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000009-beneficial-owners
    title: Beneficial Owners
    criteria:
    - Max 5 owners
    - Debit Card checkbox toggleable via feature flag
    scenarios:
    - name: Flag ON
      given: enableBODebitCard is ON
      when: Page loads
      then: Checkbox is visible
  acceptance_tests:
  - id: AT-0000009-beneficial-owners
    name: E2E Beneficial Owners Debit Flag
    steps:
    - Set enableBODebitCard to true
    - Load BO page
    - Add an owner
    - Verify Debit Card checkbox is visible
    - Set enableBODebitCard to false
    - Verify Debit Card checkbox is hidden
    expected_result: Flag controls visibility.

- id: FR-0000010-controlling-party
  text: Control Prong. Other role radio button controlled by enableBOAuthorizedUser.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000010-controlling-party
    title: Control Prong
    criteria:
    - Other role radio controlled by feature flag
    scenarios:
    - name: Flag ON
      given: enableBOAuthorizedUser is ON
      when: Page loads
      then: Other option is visible
  acceptance_tests:
  - id: AT-0000010-controlling-party
    name: E2E Control Prong Flag
    steps:
    - Set enableBOAuthorizedUser to true
    - Load Control Prong page
    - Verify Other option is visible
    - Set enableBOAuthorizedUser to false
    - Verify Other option is hidden
    expected_result: Flag controls visibility.

- id: FR-0000011-complete-profile
  text: Complete Profile page. Removes Addt'l Services. Strict validation removed. Authorized Signers controlled by enabledAuthorizedUsers.
  section: 2. End-to-End Application Flow
  acceptance_criteria:
  - id: AC-0000011-complete-profile
    title: Complete Profile logic
    criteria:
    - Addtl services not visible
    - Submission allowed with 1+ fields populated
    - Auth Signers visible only via flag
    scenarios:
    - name: Submit with 1 field
      given: Only 1 field has data
      when: Submit is clicked
      then: Submission succeeds
  acceptance_tests:
  - id: AT-0000011-complete-profile
    name: E2E Complete Profile
    steps:
    - Navigate to Complete Profile
    - Verify Addtl Services is missing
    - Provide only 1 field
    - Submit form
    - Assert success
    - Verify Auth Signers flag behavior
    expected_result: Form behaves as per rules.

- id: FR-0000012-transmit-eoj
  text: Post-submission provisioning - set Transmit onboarding_complete, configure MFA, autologin to OMB.
  section: 3. Post-Submission & Provisioning
  acceptance_criteria:
  - id: AC-0000012-transmit-eoj
    title: Transmit provisioning
    criteria:
    - API sent to Transmit with complete flags
    - omb login redirection occurs
    scenarios:
    - name: Completion
      given: Form submitted
      when: Processing finishes
      then: Transmit updated and user routed to OMB
  acceptance_tests:
  - id: AT-0000012-transmit-eoj
    name: E2E Transmit Provisioning
    steps:
    - Submit final profile
    - Verify Transmit API call contains onboarding_complete true and correct MFA settings
    - Verify redirection to OMB platform
    expected_result: Session moved to OMB seamlessly.

- id: FR-0000013-docusign
  text: Manual Docusign flow using Liveness. Consent E-sign checkbox required with timestamps.
  section: 4. Docusign Verification
  acceptance_criteria:
  - id: AC-0000013-docusign
    title: Docusign rules
    criteria:
    - Consent timestamp must be captured
    - Correct templates mapped
    scenarios:
    - name: E-sign checkbox
      given: User at consent
      when: Check e-sign and submit
      then: Timestamp recorded
  acceptance_tests:
  - id: AT-0000013-docusign
    name: E2E Docusign Consent
    steps:
    - Load consent page
    - Check E-sign
    - Submit consent
    - Assert timestamp is recorded in payload
    - Verify redirection to DocuSign liveness check
    expected_result: Docusign consent captures accurate execution.

- id: FR-0000014-sfmc-automation
  text: Lead & Winback Campaigns via SFMC. Includes automated decline emails.
  section: 5. Communications
  acceptance_criteria:
  - id: AC-0000014-sfmc-automation
    title: SFMC logic
    criteria:
    - Lead triggers correctly
    - Winback triggers correctly
    - Decline triggers upon SF status
    scenarios:
    - name: Submit Decline
      given: SF status is Declined
      when: Event triggers
      then: SFMC Decline email sent
  acceptance_tests:
  - id: AT-0000014-sfmc-automation
    name: E2E SFMC Dropoff mapping
    steps:
    - Create lead and abandon at Step 1
    - Verify SFMC Lead Campaign triggered
    - Simulate SF status Declined
    - Verify SFMC Decline email webhook triggered
    expected_result: Communications are automated based on flow.

- id: FR-0000015-website-maintenance
  text: Website routing updates to /contactus, copy changes, removal of FD 150 hardware options.
  section: 6. Appendix Public Website Maintenance
  acceptance_criteria:
  - id: AC-0000015-website-maintenance
    title: Maintenance changes
    criteria:
    - FD 150 removed
    - /support redirects to /contactus
    scenarios:
    - name: Routing
      given: Url is /support
      when: Hit
      then: Redirect to /contactus
  acceptance_tests:
  - id: AT-0000015-website-maintenance
    name: E2E Website Routing
    steps:
    - Navigate to /support
    - Assert redirect to /contactus
    - Navigate to Hardware page
    - Assert FD 150 does not exist
    expected_result: Maintenance elements are completely removed/redirected.
"""
nfr_yaml = """schema_version: 1
type: nfr_and_global_cr
items:
- id: GLOBAL-0000001-csp-security
  text: Implement cryptographic nonce in HTML tags for Public website (CSP).
  section: 1. Security
  acceptance_criteria:
  - id: AC-0000016-csp-security
    title: CSP is enforced
    criteria:
    - Nonce is present in script tags
    - CSP headers are sent
    scenarios:
    - name: Page load
      given: Site is accessed
      when: Response received
      then: headers have CSP nonce
  acceptance_tests:
  - id: AT-0000016-csp-security
    name: E2E CSP Verification
    steps:
    - Load main page
    - Inspect headers
    - Assert Content-Security-Policy contains nonce
    - Assert script tags have nonce
    expected_result: CSP is correctly applied.

- id: GLOBAL-0000002-dependency-security
  text: Resolve Handlebars.js template injection vulnerabilities.
  section: 1. Security
  acceptance_criteria:
  - id: AC-0000017-dependency
    title: Handlebars removed/updated
    criteria:
    - No outdated handlebars in lockfile
    scenarios:
    - name: Audit
      given: NPM audit
      when: Run
      then: No critical vulns
  acceptance_tests:
  - id: AT-0000017-dependency
    name: E2E Dependency Scan
    steps:
    - Run npm audit
    - Verify handlebars vulnerability does not exist
    expected_result: Dependencies are clean.

- id: GLOBAL-0000003-tokenization
  text: Move Alloy Keys to secure Environment structure.
  section: 1. Security
  acceptance_criteria:
  - id: AC-0000018-tokens
    title: Tokens are not hardcoded
    criteria:
    - No TS files contain API keys directly
    scenarios:
    - name: Code scan
      given: Src directory
      when: Scanned
      then: No naked API keys
  acceptance_tests:
  - id: AT-0000018-tokens
    name: E2E Environment Checks
    steps:
    - Inspect environment.ts generation
    - Verify keys inject from .env
    - Search codebase for Alloy API string, assert 0 results
    expected_result: Security implemented.

- id: GLOBAL-0000004-session-management
  text: Logout completely terminates API token, cache, and prevents back-navigation.
  section: 1. Security
  acceptance_criteria:
  - id: AC-0000019-session
    title: Session dead on logout
    criteria:
    - Tokens killed
    - Cache cleared
    scenarios:
    - name: Logout click
      given: A user
      when: Clicks logout
      then: Complete death of session data
  acceptance_tests:
  - id: AT-0000019-session
    name: E2E Session Expiration
    steps:
    - Login
    - Logout
    - Check localStorage
    - Assert it is empty
    - Click Back
    - Assert redirected to Login
    expected_result: Zero persistence post-logout.

- id: GLOBAL-0000005-consent-auditing
  text: Explicit timestamps for E-Sign, TCPA, KYC consents.
  section: 1. Security
  acceptance_criteria:
  - id: AC-0000020-consent
    title: Timestamps recorded
    criteria:
    - Payload contains unix timestamps corresponding to consent clicks
    scenarios:
    - name: Submit
      given: Consent checked
      when: Submitted
      then: Timestamp passed
  acceptance_tests:
  - id: AT-0000020-consent
    name: E2E Consent Timestamp
    steps:
    - Click Consent box
    - Submit
    - Verify outbound API payload includes strict ISO timestamp for consent_time
    expected_result: Auditing present.

- id: GLOBAL-0000006-feature-flags
  text: GraphQL feature flagging for enableBODebitCard, enableBOAuthorizedUser, enabledAuthorizedUsers.
  section: 2. Configuration
  acceptance_criteria:
  - id: AC-0000021-feature-flags
    title: Flags fetched from GQL
    criteria:
    - Flags power the UI toggles
    scenarios:
    - name: Load
      given: App load
      when: App starts
      then: Calls GQL for config
  acceptance_tests:
  - id: AT-0000021-feature-flags
    name: E2E GQL Flags
    steps:
    - Start App
    - Mock GraphQL config response
    - Verify UI hides/shows elements appropriately
    expected_result: App uses remote config.

- id: GLOBAL-0000007-salesforce-payload
  text: SF payload scrubs phone number to 8011234567. No hardcoded payloads allowed for account fields.
  section: 3. Data Integrity
  acceptance_criteria:
  - id: AC-0000022-sf-payload
    title: Payload clean
    criteria:
    - Phone numbers strict regex cleaned
    - Account fields read from cache
    scenarios:
    - name: Submit Lead
      given: Phone is formatted
      when: Sent to SF
      then: SF receives raw integer representation
  acceptance_tests:
  - id: AT-0000022-sf-payload
    name: E2E Salesforce Mapping
    steps:
    - Type (801) 555-1212
    - Submit Lead
    - Intercept SF Call
    - Assert phone is 8015551212
    expected_result: Data scrubs accurately.

- id: GLOBAL-0000008-alloy-idempotency
  text: Alloy Get Started must be idempotent. Avoid resubmitting if cache unchanged. Update Node explicitly to Approved/Denied.
  section: 4. Systems Integration
  acceptance_criteria:
  - id: AC-0000023-alloy-idemp
    title: Idempotent execution
    criteria:
    - No repeat API hits if payload matches cache
    scenarios:
    - name: Double submit
      given: Nothing changed
      when: Submitted
      then: Use cached journey ID
  acceptance_tests:
  - id: AT-0000023-alloy-idemp
    name: E2E Alloy Idempotency
    steps:
    - Submit form
    - Return to form
    - Submit again without changes
    - Assert Alloy API is NOT hit a second time
    expected_result: Alloy handles idempotency properly.

- id: GLOBAL-0000009-sfmc-tracking
  text: Emails include UTM/Tracking IDs. Reporting must work for cadences.
  section: 4. Systems Integration
  acceptance_criteria:
  - id: AC-0000024-sfmc-tracking
    title: SFMC tracking headers
    criteria:
    - Send events include campaign ID
    scenarios:
    - name: Webhook triggered
      given: Abandon
      when: Email queued
      then: Include UTM tags
  acceptance_tests:
  - id: AT-0000024-sfmc-tracking
    name: E2E SFMC Tracking
    steps:
    - Trigger email
    - Inspect API Hook
    - Verify UTM and Campaign tags are present in payload
    expected_result: Emails are tracked.
"""

os.makedirs(os.path.dirname(NFR_PATH), exist_ok=True)
with open(FR_PATH, "w") as f:
    f.write(fr_yaml)
    
with open(NFR_PATH, "w") as f:
    f.write(nfr_yaml)
