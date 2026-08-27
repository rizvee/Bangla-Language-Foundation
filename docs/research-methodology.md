# Research Methodology & Pipeline Lifecycle — BLF

## 1. Overview
The Bangla Language Foundation (BLF) methodology enforces a strict separation between source discovery, legal verification, linguistic formalization, dataset generation, and quality auditing.

---

## 2. Five-Stage Research Lifecycle

```
[1. Source Discovery] ──> [2. Legal Verification] ──> [3. Evidence Extraction]
                                                              │
                                                              ▼
[5. Quality Audit & Promotion] <── [4. Linguistic Modeling & Pipeline]
```

### Stage 1: Source Discovery
- Systematic literature review across Tier A–E sources.
- Focus on authoritative grammar manuals, regional dialect dictionaries, academic linguistics treatises, and public domain speech records.

### Stage 2: Legal Verification & Provenance
- Confirm redistribution rights, license clauses, and edition authenticity.
- Calculate sha256 checksums for source documents and store entries in `sources/registry/sources.json`.
- Reject bulk copyrighted prose ingestion; enforce extraction of abstract grammatical rules and lexical paradigms only.

### Stage 3: Evidence Extraction & Citation Discipline
- Extract explicit linguistic rules, morphological paradigms, and syntactic constraints.
- Map claims to verifiable citations (DOI, ISBN, institutional repository).
- Discard unverified folk claims or ungrounded model assumptions.

### Stage 4: Linguistic Modeling & Pipeline Execution
- Formalize extracted evidence into versioned ontology definitions and JSON schemas.
- Implement deterministic normalization, tokenization, and inflectional paradigms in Python.
- Execute constrained synthetic realization strictly under structured frame and grammatical constraints.

### Stage 5: Multi-Stage Quality Audit & Promotion
- Run automated schema validation and Unicode normalization checks.
- Audit for AI-slop, circular validation, and train/test contamination.
- Require human linguistic sign-off before promoting records to `GOLD`.
