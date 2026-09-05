# Reviewer Information & Ethical Participation Statement — BLF

## 1. Study Purpose & Scope
The **Bangla Language Foundation (BLF)** is an open research initiative developing evidence-grounded linguistic resources and evaluation methods for Bangladeshi Bangla.

The purpose of this human evaluation pilot is to validate sentence naturalness, register nuances, and grammatical acceptability in native Bangla.

## 2. Participant Tasks & Time Commitment
- **Task**: Evaluators review 40 short Bangla sentence items (plus 3 calibration practice items).
- **Format**: For each item, evaluators independently rate the acceptability of candidate sentences (A, B, and optional C) and indicate their preferred candidate(s).
- **Time Commitment**: Approximately 30 to 45 minutes.

## 3. Voluntary Participation & Right to Withdraw
- Participation in this evaluation is entirely voluntary.
- Evaluators may pause, skip individual items, or withdraw from the review session at any point without penalty or loss of benefits.

## 4. Privacy, Data Minimization & Pseudonymization
- **No Personal Identifiable Information (PII)**: BLF does not collect, record, or store evaluator names, email addresses, physical addresses, phone numbers, IP addresses, or government identification numbers in research datasets.
- **Pseudonymous Identifiers**: Evaluators are assigned random pseudonyms (e.g. `REV-LINGUIST-01`, `REV-NATIVE-02`).
- **Demographic Minimization**: Only broad linguistic background (native Bangladeshi speaker status, general regional variety, and professional qualification category) is recorded to verify eligibility.

## 5. Dual Consent Framework
Reviewer consent is formalized via machine-readable private records conforming to `schemas/v0_1/reviewer_consent.schema.json`, stored in `.blf-private/consent/`:
1. **Consent to Anonymized Research Use (Required for Participation)**: Authorizes internal scientific research use of pseudonymous acceptability ratings and linguistic comments to evaluate declarative linguistic rules, measure inter-annotator agreement, and train error-detection models.
2. **Consent to Anonymized Public Release (Optional / Explicit Grant)**: Authorizes inclusion of anonymized, aggregated ratings in open scientific datasets and academic preprints. Evaluators may consent to research use while declining public release.

No individual evaluator will be identifiable from any internal research or public artifact.

## 6. Institutional & Governance Basis
This evaluation involves non-invasive linguistic judgment tasks regarding language naturalness and contains no sensitive personal topics or clinical interventions. Valid machine-readable consent must be recorded prior to initializing any real review session. Software cannot fabricate consent; review sessions in `REAL` mode fail closed without authenticated consent records.

