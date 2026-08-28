# Changelog

All notable changes to the **Bangla Language Foundation (BLF)** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added - Phase 2A.1 Linguistic Integrity Recovery, Attestation & Gold-Readiness Gate
- **`হওয়া` (Howa) Inflection Paradigm**: Implemented dedicated `_conjugate_ho()` in `src/blf/linguistics/morphology/verbal_conjugator.py` covering all 6 person slots across 8 tense-aspect combinations, imperative, and participles (`হলো`, `হয়`, `হচ্ছে`, `হয়েছে`, `হব`, `হন`); added `PARADIGM-VERB-HO` to `ontology/paradigms/verbal_paradigms.json`.
- **Differential Object Marking (DOM) Engine**: Implemented `DOMEngine` in `src/blf/linguistics/dom.py` with multi-dimensional `ObjectFeatures` (Animacy, Definiteness, Specificity, Referentiality) assigning overt `-কে` vs bare `-Ø`.
- **Complex Predicate Polysemy & Selectional Repair**: Updated `src/blf/linguistics/complex_predicates.py` and `ontology/complex_predicates/complex_predicates.json` to permit cognitive achievement verbs (`জেনে ফেলা`, `বুঝে ফেলা`, `শিখে ফেলা`) while barring pure statives (`*থেকে ফেলা`). Formalized 8 polysemous vector verb specifications.
- **Polarity Morphology & -নি Negation**: Implemented `conjugate_negative()` in `verbal_conjugator.py` mapping Present Perfect + NEG to past stem + `-নি` (`করিনি`, `যায়নি`, `খায়নি`, `হয়নি`) and general postverbal `না`.
- **Corpus Attestation Subsystem**: Created `schemas/v0_1/corpus_attestation.schema.json`, `src/blf/ontology/attestation.py`, `ontology/attestations/corpus_attestations.json` (12 verified empirical attestations across literature and corpora), and `scripts/validate_attestations.py`.
- **Epistemic Frame & Dialogue Act Status Recalibration**: Expanded `schemas/v0_1/semantic_frame.schema.json` and `schemas/v0_1/dialogue_act.schema.json` status enums to `["BLF_DESIGNED", "SOURCE_GROUNDED", "EMPIRICALLY_ATTESTED", "HUMAN_REVIEWED", "STABLE"]` and updated `ontology/frames/core_frames.json` and `ontology/pragmatics/dialogue_acts.json`.
- **Diagnostic Human-Review Pack (156 Items)**: Implemented `scripts/generate_review_pack.py` producing `data/review_queue/linguistic_review_pack.json` and `.md` across 11 linguistic categories marked `PENDING_HUMAN_REVIEW`.
- **Test Suite Quality Hardening & Rule Coverage**: Hardened test suite with exact linguistic assertions and adversarial rejection tests (75 tests passing across 15 test suites). Created `research/linguistic-knowledge/rule-test-coverage.md` (100% rule coverage).
- **Gold-Readiness Evaluation Report**: Authored `research/gold-readiness-report.md` and `research/gold-readiness-report.json` issuing `CONDITIONAL_READY_FOR_HUMAN_CURATION` verdict.
- **Semantic Frame Schema**: Created `schemas/v0_1/semantic_frame.schema.json` formalizing 24 core everyday communicative frames, standardized thematic role sets, selectional restrictions, and predicate linkages.
- **Core Semantic Frames Catalog**: Authored `ontology/frames/core_frames.json` covering Motion, Ingestion, Commerce, Transfer, Cognition, Perception, Emotion, Work, and Stative domains.
- **Sentence Family Realization Engine**: Implemented `ConstrainedRealizer` in `src/blf/generation/realizer.py` enforcing DOM, agreement, and morphotactic invariants.
- **Diagnostic Sentence Families**: Authored `data/validation/sentence_families_diagnostic.json` (10 families, ~50 realizations) testing minimal pairs across questions, negation, honorificity, and vector predicates.
- **Cross-Layer Provenance Integrity Validator**: Implemented `scripts/validate_provenance_graph.py` verifying 100% complete derivation backward tracing with 0 broken links.
- **Master Validation Suite**: Implemented `scripts/validate_all.py` executing 9 authoritative project verification suites.
- **Adversarial Invariant Test Suite**: Added `tests/test_adversarial_invariants.py` asserting strict rejection of illegal affix stacking, stative-telic vectors, and honorific mismatches.

### Added - Phase 1D Conversational Register, Social Deixis & Pragmatic Layer
- **Dialogue Act Schema**: Created `schemas/v0_1/dialogue_act.schema.json` formalizing 17 communicative intents.
- **Pragmatics & Social Deixis Engine**: Implemented `PragmaticsEngine` in `src/blf/linguistics/pragmatics.py` providing 3-tier honorific transformations (`Apni`/`Tumi`/`Tui`), particle semantics, and `কি` vs `কী` disambiguation.
- **Pragmatic Catalogs**: Authored `ontology/pragmatics/dialogue_acts.json` and `pragmatic_particles.json`.
- **Linguistic Specification**: Authored `research/linguistic-knowledge/conversational-pragmatics.md`.

### Added - Phase 1C Construction Grammar & Complex Predicates
- **Construction & Complex Predicate Schemas**: Created `schemas/v0_1/linguistic_construction.schema.json` and `schemas/v0_1/complex_predicate.schema.json`.
- **Construction Catalog**: Authored `ontology/constructions/constructions.json` (22 verified clause constructions across Transitive, Intransitive, Ditransitive, Copular, Existential, Polar Ki, Imperatives, Correlatives).
- **Complex Predicate Engine**: Implemented `ComplexPredicateEngine` in `src/blf/linguistics/complex_predicates.py` validating selectional restrictions and synthesizing compound/vector verbs and LVCs.
- **Linguistic Specifications**: Authored `research/linguistic-knowledge/construction-catalog.md` and `complex-predicates.md`.

### Added - Phase 1B Morphosyntactic & Inflectional Paradigm Engine
- **Inflectional Paradigm Schema**: Created `schemas/v0_1/inflectional_paradigm.schema.json` supporting multidimensional morphological matrices (noun declension, pronominal paradigms, verbal conjugation) indexed by grammatical dimensions.
- **Nominal Declension Engine**: Implemented `NominalDeclensionEngine` in `src/blf/linguistics/morphology/nominal_declension.py` handling case allomorphy (NOM, ACC `-ke`/`-Ø`, GEN `-r`/`-yer`/`-er`, LOC `-e`/`-te`/`-y`/`-ye`), classifier-definiteness suffix stacking order (`[NounRoot] + [Classifier] + [Plural] + [Case]`), and human vs inanimate animacy splits.
- **Pronominal Paradigm Engine**: Implemented `PronominalParadigmEngine` in `src/blf/linguistics/morphology/pronominal_paradigms.py` providing exhaustive declension tables across 1st person (`Ami/Amra`), 2nd person honorificity tiers (`Apni`, `Tumi`, `Tui`), 3rd person deictic systems (`E/Ini`, `O/Uni`, `Se/Tini`), interrogatives (`Ke`, `Ki`), and relatives (`Je`).
- **Verbal Conjugation Engine**: Implemented `VerbalConjugatorEngine` in `src/blf/linguistics/morphology/verbal_conjugator.py` generating full tense-aspect matrices (PresSimp, PresCont, PresPerf, PastSimp, PastCont, PastPerf, PastHabitual, FutSimp, Imperative) and non-finite participles (Conjunctive `-e`, Conditional `-le`, Infinitive `-te`) across regular, vowel-mutating (`de-`, `kha-`, `ne-`), and irregular (`ja-` -> `ge-`) roots.
- **Golden Paradigm Catalogs**: Authored verified paradigm catalogs in `ontology/paradigms/` (`nominal_paradigms.json`, `pronominal_paradigms.json`, `verbal_paradigms.json`).
- **Paradigm Validator & Test Suite**: Added `scripts/validate_paradigms.py` and `tests/test_morphology.py` (total 44 unit tests passing, 100% compliant).
- **Linguistic Specification**: Authored `research/linguistic-knowledge/morphological-paradigms.md`.

### Added - Phase 1A Evidence-to-Linguistic-Knowledge System
- **Linguistic Knowledge Schemas**: Implemented 4 strict JSON Draft-07 schemas (`schemas/v0_1/`):
  - `linguistic_evidence.schema.json`: Fine-grained locator references, excerpt/paraphrase captures, and copyright handling classes (`DIRECT_EXCERPT_SHORT`, `SCHOLARLY_PARAPHRASE`, `RULE_CITATION`, `PUBLIC_DOMAIN_REPRODUCTION`).
  - `linguistic_claim.schema.json`: Atomic propositions across 12 linguistic levels, 4 epistemic classes (`SOURCE_ASSERTED`, `BLF_NORMALIZED`, `BLF_INFERRED`, `BLF_HYPOTHESIS`), language variety scope, and review states.
  - `linguistic_rule.schema.json`: Declarative machine-readable rule definitions (`rule_id`, `supporting_claim_ids`, `rule_type`, `structural_pattern`, `morphological_features`, `constraints`, `productivity`, `exceptions`).
  - `linguistic_example.schema.json`: Provenance-tracked utterances and negative counterexamples (`SOURCE_EXAMPLE`, `PUBLIC_DOMAIN_EXAMPLE`, `HUMAN_CREATED`, `RULE_GENERATED`) with grammaticality ratings.
- **Ontology Domain Package**: Authored typed Python domain models and enums in `src/blf/ontology/` (`models.py`, `__init__.py`).
- **Linguistic Terminology Crosswalk**: Established comprehensive mapping across Traditional Bangla Grammar, Bangla Academy (*Pramita Bangla Bhashar Byakaran*), Descriptive Linguistics, Universal Dependencies (UD), and BLF Canonical Ontology in `research/linguistic-knowledge/terminology-crosswalk.json` and `.md`.
- **Pilot Knowledge Extraction (Tier A & B Sources)**: Extracted and formalized:
  - 21 verified evidence items (`ontology/evidence/pilot_evidence.json`).
  - 36 atomic linguistic claims (`ontology/claims/pilot_claims.json`).
  - 20 declarative linguistic rules (`ontology/rules/pilot_rules.json`).
  - 22 provenance-backed examples and negative counterexamples (`ontology/examples/pilot_examples.json`).
  - 3 documented framework conflict relations and canonical resolutions (`ontology/conflicts/conflicts.json` and `research/linguistic-knowledge/conflicts.md`).
- **Integrity Validator & Regression Suite**: Implemented `scripts/validate_knowledge.py` and `tests/test_linguistic_knowledge.py` verifying referential integrity (sources->evidence->claims->rules->examples), anti-slop constraints, and prohibition of automated `HUMAN_APPROVED` states (total 34 unit tests passing, 100% compliant).
- **Linguistic Knowledge Documentation**: Authored `research/linguistic-knowledge/methodology.md`, `pilot-claims.md`, `conflicts.md`, and `extraction-status.md`.

### Added - Phase 0.3 Artifact-Specific License, Authorship & Bibliographic Consistency Audit
- **Artifact-Specific License Schema**: Upgraded `schemas/v0_1/source.schema.json` to model individual resource artifacts (`PAPER`, `CODE`, `DATASET`, `MODEL`, `CORPUS`, `RULEBOOK`, `DICTIONARY`) with distinct licenses, copyright states, locators, and redistribution rights.
- **BanglaBERT License & Artifact Hardening**: Aligned `BANGLA2B-2022` primary repository and model license to `CC-BY-NC-SA-4.0` (matching canonical `csebuetnlp/banglabert` LICENSE) and added separate paper (`CC-BY-4.0` open access) and web crawl corpus artifacts.
- **BanglaNMT Authorship & License Correction**: Replaced contaminated author metadata with verified canonical author list (*Tahmid Hasan, Abhik Bhattacharjee, Kazi Samin, Masum Hasan, Madhusudan Basak, M. Sohel Rahman, and Rifat Shahriyar*, EMNLP 2020, pp. 2612–2623) and verified `CC-BY-NC-SA-4.0` repository license.
- **BnSentMix Repository License Correction**: Corrected declared license of `BNSENTMIX-2025` from MIT to `Apache-2.0` (matching canonical `Nishita2000/BnSentMix` repo) and calibrated redistribution of social media text to `restricted_or_requires_review`.
- **Bangla Academy Locators Cleanup**: Eliminated synthetic locator strings, binding `BA-SPELL-2016` to ISBN `984-07-5531-5` and `BA-REGDICT-1965` to LoC LCCN `74930105`.
- **Auditor & Test Expansion**: Enhanced `scripts/audit_sources.py` with canonical author overlap checking and added 2 regression tests in `tests/test_source_audit.py` (total 25 unit tests, 100% passing).
- **Refrozen Phase 0.3 Manifest**: Generated `research/phase-0-manifest.json` sealing the Phase 0.3 baseline with fresh SHA-256 hashes.

### Added - Phase 0.2 Claim-Level Evidence Verification & Final Source Freeze
- **Frozen Evidence Baseline**: Created `research/phase-0-manifest.json` sealing the Phase 0 research foundation with cryptographic SHA-256 checksums across all core registries, schemas, and matrices.
- **Claim-Level Evidence Architecture**: Upgraded `schemas/v0_1/source.schema.json` and `sources/registry/sources.json` to bind individual field assertions (`title`, `year`, `edition`, `license`, `size`) to specific primary evidence objects and locators.
- **Semantic Identifier Matching**: Extended `scripts/audit_sources.py` with deterministic semantic title token similarity and author matching to reject false identifier attributions (e.g. offensive-span detection cited as BanglaBERT).
- **BanglaBERT Publication Correction**: Resolved canonical BanglaBERT identifiers to ACL: `2022.findings-naacl.98` (DOI: `10.18653/v1/2022.findings-naacl.98`, arXiv: `2101.00204`), correcting false reference `2022.naacl-main.185`.
- **Bangla Academy Grammar Correction**: Resolved canonical reference to *Pramita Bangla Bhashar Byakaran* (`BA-GRAM-2011`, 2011, 2 vols, LCCN 2012323386) edited by Rafiqul Islam and Pabitra Sarkar, correcting conflated 2012 3-volume record.
- **Explicit Legal Status Separation**: Decoupled `copyright_status`, `license`, and `redistribution_permission` across all sources to prevent unwarranted assumption of open licenses on printed monographs.
- **Expanded Regression Tests**: Added tests in `tests/test_source_audit.py` proving semantic rejection of false ACL/arXiv identifiers and refusal of generic homepages without locators.

### Added - Phase 0.1 Source Integrity Recovery & Evidence Hardening
- **Source Integrity Auditor**: Implemented `scripts/audit_sources.py` providing deterministic cross-identifier verification (ACL Anthology IDs, arXiv IDs, UD repository canonical names, and field-level evidence requirements).
- **Source Audit Ledger**: Established `sources/registry/source-audit.jsonl` tracking corrections and quarantine rationale for historical candidate misattributions.
- **Field-Level Verification Schema**: Upgraded `schemas/v0_1/source.schema.json` and `sources/registry/sources.json` to require explicit `verification` blocks with primary evidence URLs, access dates, and verified field tuples.
- **Regression Test Suite**: Added `tests/test_source_audit.py` guaranteeing automated detection and rejection of known false identifier signatures (e.g. arXiv:2206.14051, ACL 2021.wnut-1.14, ACL 2022.findings-emnlp.319).
- **Hardened Source Registry**: 16 fully verified primary sources across Tier A, B, and D, 1 partially verified source (`BPCC-BENGALI-2023`), and 4 quarantined historical candidate entries.
- **Epistemic Anti-Slop Expansion**: Updated `docs/research-writing-policy.md` and `.ai/checks/anti-ai-slop.md` with explicit definitions and prohibitions against Epistemic AI Slop (identifier fabrication, blended metadata, invented statistics, circular LLM verification).
- **Calibrated Gap Analysis**: Updated `research/gap-analysis/phase-0-gap-analysis.md` with explicit epistemic status tags (`[SUPPORTED]`, `[PARTIALLY_SUPPORTED]`, `[NOT_YET_VERIFIED]`).

---

## [0.1.0] - 2026-08-27

### Added
- **Repository Architecture & Tooling**: Initial project directory layout spanning `data/`, `ontology/`, `schemas/`, `sources/`, `research/`, `scripts/`, `src/`, `tests/`, and `docs/` (Software and research scaffolding; no public dataset release).
- **JSON Schemas (v0.1 Draft)**: Draft JSON Schema specifications for `utterance`, `sentence_family`, `source`, and `synthetic_provenance`.
- **Python Core Library (`src/blf/`)**:
  - `blf.linguistics.normalizer`: Bengali Unicode NFC normalization, Dari mapping, and character range validation.
  - `blf.linguistics.tags`: Enums for register, dialect, code-switching type, quality tier, and validation status.
  - `blf.core.models`: Typed dataclasses for core linguistic entities.
  - `blf.core.quality`: Quality tier invariant enforcement functions.
  - `blf.provenance.tracker`: Cryptographic SHA-256 and prompt hash tracking.
  - `blf.validation.validators`: Self-contained JSON schema validator.
- **Verification Scripts**:
  - `scripts/validate_schemas.py`: Verifies JSON schemas and test fixtures.
  - `scripts/validate_sources.py`: Validates `sources/registry/sources.json` entries.
  - `scripts/check_anti_slop.py`: Scans documentation for AI filler and canned phrasing.
  - `scripts/unicode_normalizer.py`: CLI for Unicode normalization.
- **Source Registry**: Seeded `sources/registry/sources.json` with initial verified records from Bangla Academy, Suniti Kumar Chatterji, and Universal Dependencies.
- **Automated Test Suite**: 13 unit tests covering normalization, schema invariants, source registry format, and anti-slop detection.
- **Research Documentation**: Comprehensive guides for architecture, research methodology, data quality model, provenance and licensing, reproducibility, and research writing.
