# Changelog

All notable changes to the **Bangla Language Foundation (BLF)** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added - Pre-Human Foundation Program (Groundwork Freeze)
- **Phase 2B Ontology Graph & Crosswalks**: Built typed in-memory directed graph `OntologyGraph` (`src/blf/ontology/graph.py`) with automated repository loading and backward derivation tracing; implemented Universal Dependencies (UD) crosswalk (`src/blf/ontology/ud_crosswalk.py`) for UD Bengali-BRU and PUD with explicit relation vocabulary (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `NO_DIRECT_MAPPING`, `PROVISIONAL`); built abstract external lexical adapter interfaces (`src/blf/ontology/lexical_crosswalk.py`).
- **Phase 4 Reversible Pipeline & Deduplication**: Implemented `ReversibleNormalizer` (`src/blf/pipeline/normalization.py`) tracking step-level transformation provenance with ZWJ/ZWNJ ligature policy; built `ConservativeTextCleaner` (`src/blf/pipeline/cleaning.py`) preserving Bengali diacritics and signs while removing corrupted control codes; created 4-tier deduplicator `MultiTierDeduplicator` (`src/blf/pipeline/deduplication.py`) across exact, normalized, morphosyntactic, and semantic near-duplicates; added `PipelineManifest` (`src/blf/pipeline/manifest.py`).
- **Phase 5 Annotation OS & Quality Workflow**: Formalized multi-layer annotation bundle models (`src/blf/annotation/layers.py`) covering tokenization, syntactic dependencies, semantic frames, pragmatics, and dialect markers; implemented monotonic lifecycle state machine `PromotionStateMachine` (`src/blf/annotation/state_machine.py`) with strict invariants preventing unverified promotion to `GOLD`; created `ConflictQueue` and adjudication resolvers (`src/blf/annotation/adjudication.py`); implemented multi-rater agreement metrics (`compute_fleiss_kappa`, `compute_krippendorff_alpha_nominal` in `src/blf/quality/advanced_iaa.py`) failing closed on missing data without synthetic scores.
- **Phase 6 Constrained Synthetic Generation**: Developed `ConstrainedGenerationPipeline` (`src/blf/generation/pipeline.py`) enforcing semantic frame selectional restrictions (`[+Animate]`, `[+Edible]`, `[+Liquid]`) and anti-Cartesian argument filtering; bound output to `synthetic_provenance.schema.json` with mandatory `SYNTHETIC_SOFTWARE_TEST_ONLY` tagging; preserved zero production corpus records invariant.
- **Phase 7 Dataset Assembly & Distribution Audit**: Built `FamilyGroupedSplitter` (`src/blf/dataset/split_policy.py`) guaranteeing zero train-test leakage by co-locating all sentence family variants in the same partition; created `DistributionAuditor` (`src/blf/dataset/distribution_audit.py`) checking quota compliance across registers, dialects, frames, and constructions; authored `docs/dataset-card-template.md`.
- **Phase 8 BLF-Bench & Contamination Prevention**: Created diagnostic linguistic probes for DOM, complex predicates, negation placement, honorific agreement, and morphotactics (`src/blf/benchmarks/probes.py`); implemented `ContaminationChecker` (`src/blf/benchmarks/contamination.py`) detecting verbatim n-gram overlap and family leakage; developed `BLFBenchRunner` (`src/blf/benchmarks/runner.py`) reporting structured metric contracts without fabricating empirical model numbers.
- **Licensing, Release & Paper Scaffolding**: Formulated data licensing evaluation in `docs/DATA_LICENSE_DECISION.md` (marked `DECISION_PENDING`); mapped all 23 sources in `sources/licensing/redistribution_matrix.json`; created unreleased build manifest in `release/release_manifest.json` confirming 0 Gold records; authored comprehensive methodology paper draft skeleton in `papers/methodology_paper_skeleton.md` with explicit empirical placeholders.
- **CI & Reproducibility Hardening**: Authoritative single-command local verification suite in `scripts/verify_all.py`; aligned `.github/workflows/ci.yml` across Python 3.10-3.13; expanded test suite to 155 unit tests (100% passing).
- **Fail-Closed Nominal Morphotactics**: Refactored `assess_nominal_morphotactics()` in `src/blf/linguistics/morphology/nominal_declension.py` to check against canonical noun lexicon and valid suffix sequences, failing closed to `MorphotacticStatus.UNKNOWN` with `auto_generation_safe=False` for arbitrary/unrecognized strings; calibrated `N+টা+গুলো` status from `ATTESTED_STANDARD` to `ATTESTED_OFFICIAL_EDUCATIONAL_USAGE` with `auto_generation_safe=False`.
- **Provisional External Source Registration**: Registered `NCTB-TG-BANGLA` (National Curriculum and Textbook Board Teacher's Guide) and `ACCESSIBLE-DICT-A2I` (a2i Accessible Dictionary) as `PROVISIONAL` in `sources/registry/sources.json` with rigorous bibliographic artifacts and primary evidence citations.
- **Pragmatic `যে` Epistemic Downgrade & Ambiguity Marking**: Downgraded engineered polyfunctional senses of *যে* (`SENSE-JE-EMOTIVE-MIRATIVE`, `SENSE-JE-CLAUSE-FINAL-EVALUATIVE`, `SENSE-JE-EMPHATIC-STANCE`) from `VERIFIED` / `HIGH` to `confidence="MEDIUM"`, `evidence_strength="PROVISIONAL"`, `review_status="NEEDS_HUMAN_REVIEW"` across `src/blf/linguistics/pragmatics.py` and `ontology/pragmatics/pragmatic_particles.json`; updated `analyze_particle_je()` so multiple plausible interpretations without disambiguating context mark `is_ambiguous=True` and `primary_sense="AMBIGUOUS"` while exposing `most_likely_sense`.
- **Fail-Closed Interrogative Wh-Construction Parser**: Enhanced `analyze_wh_construction()` in `src/blf/linguistics/pragmatics.py` to return explicit `construction_status` (`SUPPORTED_STANDARD`, `POLAR_OR_ORTHOGRAPHIC_AMBIGUITY`, `NEEDS_HUMAN_REVIEW`, `UNKNOWN`), failing closed with `is_grammatical=None` for unmodeled or out-of-domain inputs.
- **Aspectual Vector Compatibility Evidence Separation**: Refactored `assess_vector_compatibility()` in `src/blf/linguistics/complex_predicates.py` with `VERIFIED_VECTOR_COMBINATIONS` registry; distinguished empirically verified pairings (`VERIFIED_COMBINATION`, `auto_generation_safe=True`) from general grammatical compatibility (`TYPE_LICENSED`, `auto_generation_safe=False`) and unrecognized pole lemmas (`UNKNOWN`, `auto_generation_safe=False`).
- **Diagnostic Pilot 40 Source Grounding**: Updated `data/review_queue/human_review_pilot_40.json` (items 015, 016, 023, 030, 040) referencing canonical registered provisional source IDs (`NCTB-TG-BANGLA`, `ACCESSIBLE-DICT-A2I`) and calibrated hypotheses.
- **Adversarial Invariants & Regression Suite**: Expanded `tests/test_adversarial_invariants.py` to 15 comprehensive invariant tests verifying fail-closed nominal morphotactics, provisional source registration, epistemic status of *যে*, fail-closed Wh constructions, vector compatibility boundaries, and exact 40-item pilot freeze; updated `tests/test_pragmatics.py` (97 total unit tests passing).
- **Pre-Pilot Provenance Errata (Phase 2A.2f.1)**: Corrected `NCTB-TG-BANGLA` source identity to match Class 4 English Teacher's Guide PDF artifact with exact URL (`https://dpe.portal.gov.bd/.../TG%20-%20Class%204%20English.pdf`), TIER_C classification, and narrow claim binding for `ছবিটাগুলো` (`CLM-NCTB-CHOBITAGULO-OCCURRENCE`); corrected `ACCESSIBLE-DICT-A2I` attribution to include YPSA as implementing organization with a2i support, TIER_D classification, and bound headword `যে ৩` to `PARTICLE_JE_IS_POLYFUNCTIONAL` (`CLM-ACCESSIBLE-DICT-JE-POLYFUNCTIONAL`) while keeping publication year and BLF 4-sense model provisional; transformed vector verification set into evidence-bearing `VERIFIED_VECTOR_REGISTRY` mapping traceable `evidence_ids`, `claim_ids`, and `source_ids`, preventing unbound or dead vector combinations from claiming `VERIFIED_COMBINATION`; expanded invariant tests to 98 passing unit tests.

### Added - Phase 2A.2e Forensic Linguistic Calibration Patch
- **Classifier Morphotactics Calibration**: Neutralized blanket surface-string blacklist in `src/blf/generation/realizer.py`; added `assess_nominal_morphotactics()` and `MorphotacticStatus` enum in `src/blf/linguistics/morphology/nominal_declension.py` modeling attested `N+টা+গুলো` (NCTB educational attestation), `N+গুলা+CASE` (historical and contemporary usage), and colloquial `N+টা+দের` without claiming automatic canonical status; enforced that `check_morphotactic_invariants()` rejects only genuinely unsupported inverted patterns (e.g. `গুলোটি`, `গুলোরটি`).
- **Graded Aspectual Vector Compatibility**: Replaced binary stative ban with graded vector selection architecture in `src/blf/linguistics/complex_predicates.py` (`ALLOWED`, `CONTEXT_DEPENDENT`, `UNSUPPORTED`, `UNKNOWN`); distinguished auto-generation safety (`auto_generation_safe=False` for stative + `ফেলা`) from linguistic impossibility; updated `ontology/complex_predicates/complex_predicates.json` (`CPRED-VECTOR-PHELA-TELIC`) with explicit `stative_compatibility` and coercion factors.
- **Interrogative Wh-Orthography & Construction Separation**: Added `analyze_wh_construction()` in `src/blf/linguistics/pragmatics.py` separating orthographic Wh-spelling (`কি` vs `কী`) from argument structure constructions (nominative transitive vs genitive experiencer modal); updated `VERB_VALENCY_LEXICON` with perfective and conjunctive forms for `যা` and `আস`.
- **Polyfunctional Particle `যে` Expansion**: Expanded `ParticleSense` with rich pragmatic attributes (`host_position`, `speaker_commitment`, `mirativity`, `illocution_type`, etc.); modeled 4 evidence-backed senses in `src/blf/linguistics/pragmatics.py` and `ontology/pragmatics/pragmatic_particles.json` (`COMPLEMENTIZER`, `EMOTIVE_MIRATIVE`, `CLAUSE_FINAL_EVALUATIVE`, `EMPHATIC_STANCE`); implemented `analyze_particle_je()` with explicit ambiguity fallback.
- **Diagnostic Pilot Calibration**: Calibrated 5 analytical items in `data/review_queue/human_review_pilot_40.json`:
  - `PILOT-ITEM-015`: Modeled N+টা+গুলো (C) as independently attested (NCTB) requiring human calibration; N+গুলো+টা (B) as separate unresolved pattern (Priority: CRITICAL).
  - `PILOT-ITEM-016`: Modeled `ছেলেগুলাকে` (C) as attested conversational/popular Bangla (not ungrammatical); `ছেলেটাদেরকে` (B) as colloquial unresolved pattern (Priority: HIGH).
  - `PILOT-ITEM-023`: Modeled `থেকে ফেলল` (B) as marked/context-dependent requiring telic coercion/speaker evaluation rather than universal impossibility (Priority: HIGH).
  - `PILOT-ITEM-030`: Separated Wh-orthography from argument structure; `তোমার কী চাই?` (C) evaluated as structurally distinct experiencer construction (Priority: CALIBRATION / MEDIUM).
  - `PILOT-ITEM-040`: Modeled A (`সে যে এসে গেছে!`) and B (`সে এসে গেছে যে!`) as distinct pragmatic anchoring; C as polar surprise strategy (Priority: HIGH).
- **Comprehensive Regression Test Suite**: Replaced false invariant tests in `tests/test_adversarial_invariants.py` with 12 calibrated regression tests across classifier patterns, vector event structures, Wh constructions, and polyfunctional particles; updated `tests/test_realization.py`, `tests/test_complex_predicates.py`, and `tests/test_pragmatics.py` (total 95 unit tests passing).

### Added - Phase 2A.2d Review Capture Integrity & Pilot Launch Freeze
- **Reviewer Submission Bundle Schema**: Created `schemas/v0_1/reviewer_submission_bundle.schema.json` formalizing complete 40-item blinded submission payloads with strict candidate keys (`A`, `B`, `C`), unique preferred candidates, and zero research metadata leakage.
- **Machine-Readable Reviewer Consent Schema**: Created `schemas/v0_1/reviewer_consent.schema.json` separating consent to research use from consent to anonymized public release.
- **Fail-Closed Private Session Generator**: Hardened `scripts/create_private_review_session.py` with `--mode REAL|DEMO` (default `REAL`), enforcing pre-existing verified consent records, 128-bit private seeds (`secrets.randbits(128)`), dynamic UTC ISO-8601 timestamps, clean response templates (`submission_template_<reviewer>.json`), and security checks blocking output to tracked paths.
- **Fail-Closed Review Decoder & Immutability**: Enhanced `scripts/decode_review_submissions.py` to enforce bundle validation, session and reviewer matching, candidate count verification against canonical pilot items, preference policy enforcement, and SHA-256 cryptographic hashing of raw submissions.
- **De-Primed Calibration Practice Items**: Replaced practice items in `data/review_queue/practice_items.json` with calibration items teaching interface mechanics only (independent rating, ungrammatical identification, and context flagging) without touching analytical pilot phenomena; removed leading facilitator guidance from reviewer view.
- **Official Study Completeness Gate**: Upgraded `src/blf/quality/iaa.py` and `scripts/compute_iaa.py` with `--enforce-completeness` gate, pooled candidate-level Cohen's Kappa reporting, confusion matrices, and separate preferred-set agreement tracking.
- **End-to-End DEMO Verification Pipeline**: Created `scripts/run_demo_pipeline.py` verifying full synthetic lifecycle from session generation to dual IAA and disagreement export under explicit `SYNTHETIC_SOFTWARE_TEST_ONLY` status.
- **Comprehensive Integrity Tests**: Added `tests/test_review_capture_integrity.py` verifying candidate key restrictions, fail-closed decoder behavior, consent gating, template leak prevention, and completeness checks (91 total unit tests passing).

### Added - Phase 2A.2c Private Blind Sessions, Candidate-Level Judgments & Human Pilot Freeze
- **Private Session Architecture & Secret Gitignore**: Added `.blf-private/` and `.local-review/` to `.gitignore`; created `scripts/create_private_review_session.py` to generate uncompromised private sessions with randomized item and candidate orders, practice items, and opaque display IDs (`BLIND-R1-*`).
- **Public Pack Deprecation**: Marked Phase 2A.2b public demo packs and `pilot_40_randomization_mapping.json` as `DEPRECATED_FOR_REAL_REVIEW` / `DEMO_METHODOLOGY_ONLY` due to public git history mapping exposure.
- **Candidate-Level Acceptability & Raw Submission Schema**: Refactored `schemas/v0_1/human_review_decision.schema.json` to capture independent candidate-level ratings (`acceptability`, `certainty`) and separate `preferred_candidates` (supporting multiple choices and `NONE`) without requiring secret seeds or canonical IDs.
- **Decoded Review Record Schema**: Created `schemas/v0_1/decoded_review_record.schema.json` and decoder `scripts/decode_review_submissions.py` to translate raw blinded submissions back to canonical items for analysis.
- **Dual-Target IAA Engine**: Upgraded `src/blf/quality/iaa.py` and `scripts/compute_iaa.py` to calculate Target A (Candidate-Level Acceptability Agreement) and Target B (Preferred-Candidate Set Agreement).
- **Practice Items & Ethical Governance**: Authored `data/review_queue/practice_items.json` (3 calibration examples), `docs/reviewer-consent-and-ethics.md` (privacy minimization and consent statement), and `docs/pilot-decision-protocol.md` (pre-registered decision rules).

### Added - Phase 2A.2b Blinded Review Protocol & IAA Methodology Hardening
- **Blinded Human Review Generator & Seeded Randomizer**: Implemented `scripts/generate_blinded_pilot.py` producing reviewer-specific evaluation packages (`data/review_queue/blinded_packs/pilot_40_blinded_*.json` and `.md`) with seeded deterministic candidate permutations and secret mapping table in `data/review_queue/pilot_40_randomization_mapping.json`, strictly withholding internal hypotheses, expected answers, and source hints.
- **Stage 2 Adjudication Schema**: Created `schemas/v0_1/review_adjudication.schema.json` formalizing authoritative post-review disagreement reconciliation.
- **Human Review Decision Schema Fix**: Updated `schemas/v0_1/human_review_decision.schema.json` supporting hyphenated reviewer IDs (e.g. `REV-LINGUIST-01`), separate native speaker eligibility flags, and individual record status `RECORDED` (preventing individual decisions from self-declaring `ADJUDICATED_GOLD`).
- **Pairwise IAA & Multi-Rater Analyzer**: Upgraded `src/blf/quality/iaa.py` and `scripts/compute_iaa.py` enforcing explicit pairwise Cohen's Kappa (`--reviewer-a`, `--reviewer-b`), category breakdown analytics, confusion matrices, and exporting flagged disagreement items (`--output-disagreements`).
- **Two-Stage Protocol Documentation**: Authored `docs/human-review-methodology.md` detailing Stage 1 blinded judgment, reviewer eligibility criteria, candidate randomization, IAA statistical bounds, and Stage 2 evidence-aware adjudication.

### Added - Phase 2A.2 Attestation Integrity, Normative Calibration & Controlled Human-Review Pilot
- **Attestation Integrity & Granular Verification Enums**: Updated `schemas/v0_1/corpus_attestation.schema.json` and `src/blf/ontology/attestation.py` adding explicit verification statuses (`DISCOVERED`, `PROVISIONAL`, `LOCATOR_VERIFIED`, `TEXT_VERIFIED`, `FEATURE_VERIFIED`, `HUMAN_REVIEWED`, `REJECTED`) and verification methods; downgraded 12 existing attestations to `PROVISIONAL` and quarantined unindexed corpus split locators.
- **Attestation Validators & Offline Auditor**: Upgraded `scripts/validate_attestations.py` to validate `rule_ids` against canonical registry; created `scripts/audit_attestations.py` with deterministic `--offline` and `--online` auditing.
- **`হওয়া` Honorific Imperative Calibration**: Corrected 2nd person honorific imperative to `হোন` (*দয়া করে শান্ত হোন*, *সুস্থ হোন*) in `verbal_conjugator.py` and `verbal_paradigms.json`, maintaining distinction from indicative `হন` (*আপনি শিক্ষক হন*).
- **Negative Morphology Calibration**: Calibrated `-নি` perfective negation in `verbal_conjugator.py` to support canonical standard (*দিইনি*, *নিইনি*, *শিখিনি*) and reject silent fabrication for unmodeled roots.
- **Multi-Factor DOM Engine & Inanimate Specificity**: Updated `src/blf/linguistics/dom.py` removing universal ban on inanimate *-কে*; modeled source conflict and licensed accepted overt *-কে* under contrastive focus and topicalization (*এটাকে দাও*, *চিঠিটাকে রেখেছি*).
- **Structured Interrogative Valency Analyzer**: Rebuilt `disambiguate_ki()` in `src/blf/linguistics/pragmatics.py` using verb valency lexicon and argument accounting, returning explicit `AMBIGUOUS` fallback on unknown contexts.
- **Human Review Framework & IAA Tooling**: Created `schemas/v0_1/human_review_decision.schema.json`, `src/blf/quality/iaa.py`, and `scripts/compute_iaa.py` supporting Cohen's Kappa, raw agreement, disagreement extraction, and adjudication.
- **Stratified Human Review Pilot (40 Items)**: Generated `data/review_queue/human_review_pilot_40.json` and `.md` covering 6 critical categories for native linguist evaluation.
- **Epistemically Relabeled Candidate Pack (156 Items)**: Refactored `data/review_queue/linguistic_review_pack.json` and `.md` removing ungrounded decimal confidence in favor of categorical `HIGH`/`MEDIUM`/`LOW` and descriptive acceptability tags.
- **Categorical Gold-Readiness Gate**: Rewrote `research/gold-readiness-report.md` and `.json` with categorical evidence gates (`READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT`).

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
