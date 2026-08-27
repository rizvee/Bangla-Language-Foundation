# Linguistic Knowledge & Pipeline Coverage Matrix — BLF

**Status**: Verified Operational Pipeline  
**Date**: 2026-08-28  

---

## 1. Quantitative Inventory Across Pipeline Layers

| Pipeline Layer | Artifact Path | Schemas | Validated Instances | Key Linguistic Entities |
|---|---|---|---|---|
| **Phase 0 Source Registry** | `sources/registry/sources.json` | `source.schema.json` | 21 sources (16 Verified, 1 Partial, 4 Quarantined) | Primary Tier A–D sources |
| **Phase 1A Linguistic Knowledge** | `ontology/{evidence,claims,rules,examples}/` | 4 schemas (`linguistic_*.schema.json`) | 99 items (21 Evidences, 36 Claims, 20 Rules, 22 Examples) | Phonology, Morphology, Syntax, Semantics |
| **Phase 1B Inflectional Paradigms** | `ontology/paradigms/` | `inflectional_paradigm.schema.json` | 13 paradigms (4 Nouns, 5 Pronouns, 4 Verbs) | Nominal allomorphy, Honorific matrices, Conjugator |
| **Phase 1C Construction Grammar** | `ontology/constructions/constructions.json` | `linguistic_construction.schema.json` | 22 constructions | SOV, SV, S-IO-DO-V, Copula, Polar Ki, Imperatives |
| **Phase 1C Complex Predicates** | `ontology/complex_predicates/complex_predicates.json` | `complex_predicate.schema.json` | 8 complex predicates | Telic `phela`, Benefactive `neoa`/`dewa`, LVC `kora`/`howa` |
| **Phase 1D Conversational Pragmatics** | `ontology/pragmatics/` | `dialogue_act.schema.json` | 17 dialogue acts, 7 particles | Social deixis, Ki vs Kee disambiguation, Clitics |
| **Phase 2A Semantic Frames** | `ontology/frames/core_frames.json` | `semantic_frame.schema.json` | 24 semantic frames | Motion, Ingestion, Cognition, Commerce, Emotion |
| **Constrained Realization** | `data/validation/sentence_families_diagnostic.json` | `sentence_family.schema.json` | 10 diagnostic families (~50 variants) | Minimal pairs, Invariant validation |

---

## 2. Test & Verification Coverage

| Test Suite | File | Tests Count | Scope |
|---|---|---|---|
| **Linguistic Knowledge** | `tests/test_linguistic_knowledge.py` | 16 tests | Schema validation, claim-rule referential integrity, conflict resolution |
| **Morphology Engine** | `tests/test_morphology.py` | 11 tests | Noun declension, classifier exclusivity, pronoun matrices, verb conjugation |
| **Construction Grammar** | `tests/test_constructions.py` | 3 tests | Construction types, schema conformance |
| **Complex Predicates** | `tests/test_complex_predicates.py` | 4 tests | Vector verb synthesis, LVC realization, selection restrictions |
| **Pragmatics & Social Deixis** | `tests/test_pragmatics.py` | 4 tests | 3-tier register transformation, Ki/Kee disambiguation, focus clitics |
| **Semantic Frames** | `tests/test_frames.py` | 3 tests | Frame definitions, core roles, compatible constructions |
| **Constrained Realizer** | `tests/test_realization.py` | 6 tests | DOM, topicalized OSV, pro-drop, ditransitives, illegal affix rejection |
| **Adversarial Invariants** | `tests/test_adversarial_invariants.py` | 3 tests | Double determination rejection, stative telic rejection, honorific preservation |
| **Core BLF Engine** | `tests/test_*.py` (Normalizer, Authorship, Docs, Anti-Slop) | 18 tests | Unicode normalization, ACL metadata, slop detection |
| **Total Automated Tests** | — | **68 unit tests** | **100% Passing (0 failures, 0 errors)** |

---

## 3. Provenance Graph Integrity Summary
- Complete end-to-end tracing validated from Diagnostic Utterance $\rightarrow$ Sentence Family $\rightarrow$ Semantic Frame $\rightarrow$ Construction $\rightarrow$ Rule $\rightarrow$ Claim $\rightarrow$ Evidence $\rightarrow$ Source.
- **Zero broken links detected** (`scripts/validate_provenance_graph.py`).
