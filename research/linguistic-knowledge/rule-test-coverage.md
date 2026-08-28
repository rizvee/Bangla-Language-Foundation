# BLF Linguistic Rule & Test Coverage Matrix

**Phase**: 2A.1 — Linguistic Integrity Recovery, Attestation & Gold-Readiness Gate  
**Total Pilot Rules**: 20  
**Test Suite**: 75 automated unit and regression tests across `tests/`  
**Test Coverage Ratio**: 100% (20 / 20 rules verified by automated test assertions)

---

## 1. Rule-to-Test Mapping Table

| Rule ID | Rule Name / Type | Canonical Source | Primary Test File & Method | Exact Assertion Type | Status |
|---|---|---|---|---|---|
| `RUL-SYN-SOV-DEFAULT` | Canonical SOV Ordering | `BA-GRAM-2011`, `AZAD-SYNTAX-1984` | `tests/test_realization.py::test_transitive_sov_realization` | Exact string match: `"আমি বই পড়লাম।"` | `VERIFIED` |
| `RUL-SYN-SCRAMBLE-TOPICAL` | Object Left-Topicalization | `AZAD-SYNTAX-1984` | `tests/test_realization.py::test_topicalization_and_prodrop` | Exact string match: `"চিঠিটা সে লেখে।"` | `VERIFIED` |
| `RUL-SYN-PRODROP-MATRIX` | Matrix Subject Pro-Drop | `THOMPSON-GRAM-2012` | `tests/test_realization.py::test_topicalization_and_prodrop` | Exact string match: `"ভাত খায়।"` | `VERIFIED` |
| `RUL-SYN-DATSUBJ-EXPERIENCER` | Experiencer Dative Subject | `KLAIMAN-1981`, `BA-GRAM-2011` | `tests/test_complex_predicates.py::test_light_verb_realization` | Exact string match: `"ক্ষিদে পায়"` | `VERIFIED` |
| `RUL-MSYN-DOM-ACCUSATIVE` | Differential Object Marking (-কে vs -Ø) | `KLAIMAN-1981`, `AZAD-SYNTAX-1984` | `tests/test_realization.py::test_feature_sensitive_dom_realization` | Exact string match: `"আমরা ডাক্তার খুঁজছি।"` vs `"শিক্ষক ছাত্রটিকে ডাকলেন।"` | `VERIFIED` |
| `RUL-MSYN-HON-AGREEMENT` | 3-Tier Honorific Concord | `BA-GRAM-2011`, `THOMPSON-GRAM-2012` | `tests/test_pragmatics.py::test_social_deixis_register_transform` | Exact string matches: `"আপনি বলেন"`, `"তুমি বলো"`, `"তুই বলিস"` | `VERIFIED` |
| `RUL-MORPH-PRES-INFLECTION` | Present Simple Inflection | `BA-GRAM-2011`, `BA-SPELL-2016` | `tests/test_morphology.py::test_regular_closed_root_kor` | Exact slot checks: `PRES_SIMP.1` == `"করি"`, `2_ORD` == `"করো"`, `2_HON` == `"করেন"` | `VERIFIED` |
| `RUL-MORPH-CONT-ASPECT` | Continuous Aspect (-ch-) | `BA-GRAM-2011` | `tests/test_morphology.py::test_regular_closed_root_kor` | Exact slot check: `PRES_CONT.1` == `"করছি"` | `VERIFIED` |
| `RUL-MORPH-FUT-INFLECTION` | Future Simple Inflection (-b-) | `BA-GRAM-2011` | `tests/test_morphology.py::test_regular_closed_root_kor` | Exact slot checks: `FUT_SIMP.1` == `"করব"`, `2_HON` == `"করবেন"` | `VERIFIED` |
| `RUL-SYN-NEG-POSTVERBAL` | Postverbal Sentential Negation | `BA-GRAM-2011` | `tests/test_morphology.py::test_negative_conjugation_polarity` | Exact string match: `"করি না"`, `"করব না"`, `"যাবে না"` | `VERIFIED` |
| `RUL-MSYN-NEG-PERFECTIVE` | Perfective Negation with -ni | `BA-GRAM-2011`, `THOMPSON-GRAM-2012` | `tests/test_morphology.py::test_negative_conjugation_polarity` | Exact string matches: `"করিনি"`, `"যায়নি"`, `"খায়নি"`, `"হয়নি"` | `VERIFIED` |
| `RUL-SEM-COPULA-NEGATION` | Copular Negator (noy / non / nei) | `BA-GRAM-2011` | `tests/test_realization.py::test_diagnostic_sentence_families_schema` | Exact copula realization and validation against schema | `VERIFIED` |
| `RUL-SEM-VECTOR-TELIC` | Aspectual Telic Vector (phela) | `AZAD-SYNTAX-1984`, `BA-GRAM-2011` | `tests/test_complex_predicates.py::test_vector_verb_realization` | Exact string matches: `"খেয়ে ফেলল"`, `"জেনে ফেলল"`, `"বুঝে ফেললাম"` | `VERIFIED` |
| `RUL-SEM-VECTOR-BENEF` | Benefactive Vectors (neoa / dewa) | `AZAD-SYNTAX-1984`, `BA-GRAM-2011` | `tests/test_complex_predicates.py::test_vector_verb_realization` | Exact string matches: `"কিনে নিলাম"`, `"লিখে দিল"` | `VERIFIED` |
| `RUL-MSYN-CLF-DEFINITE` | Definite Classifiers (-ta / -ti) | `BA-GRAM-2011` | `tests/test_morphology.py::test_human_noun_declension` | Exact nominal forms: `"মানুষটি"`, `"বইটা"` | `VERIFIED` |
| `RUL-MSYN-CLF-NUMERAL` | Numeral Classifier Syntax | `BA-GRAM-2011` | `tests/test_morphology.py::test_case_allomorphy_suffixes` | Classifier-numeral allomorphy and slot consistency | `VERIFIED` |
| `RUL-MSYN-POSTPOS-GENITIVE` | Genitive Postposition Governance | `BA-GRAM-2011` | `tests/test_pragmatics.py::test_ki_disambiguation` | Exact oblique/genitive probe: `"কিসের জন্য?"` | `VERIFIED` |
| `RUL-SYN-POLAR-INTERROGATIVE` | Polar Question Particle 'ki' | `BA-GRAM-2011`, `AZAD-SYNTAX-1984` | `tests/test_realization.py::test_polarity_and_question_realization` | Exact placements: `"তুমি কি ঢাকা যাবে ?"`, `"তুমি ঢাকা যাবে কি ?"` | `VERIFIED` |
| `RUL-MSYN-PLURAL-ANIMACY` | Plural Marking Animacy Split | `BA-GRAM-2011` | `tests/test_morphology.py::test_classifier_plural_exclusivity` | Strict rejection of `*টাগুলো`, `*টিরা`, `*টাদের` | `VERIFIED` |
| `RUL-SYN-CORRELATIVE-RELATIVE` | Correlative Relative Clauses | `BA-GRAM-2011`, `AZAD-SYNTAX-1984` | `tests/test_constructions.py::test_constructions_schema` | Construction `CONST-CORRELATIVE-REL` structural validation | `VERIFIED` |

---

## 2. Hardened Regression Test Summary

In Phase 2A.1, the test suite was hardened to replace coarse length/non-null checks with exact linguistic assertions and adversarial rejection tests:

1. **`হওয়া` Verbal Paradigm (`tests/test_morphology.py::test_irregular_root_ho`)**:
   - Explicitly asserts 20 inflectional slots including past ordinary `"হলো"`, present ordinary `"হয়"`, present continuous `"হচ্ছে"`, present perfect `"হয়েছে"`, conjunctive participle `"হয়ে"`, conditional `"হলে"`, and infinitive `"হতে"`.
2. **Cognitive Achievement with `ফেলা` (`tests/test_complex_predicates.py::test_vector_verb_realization`)**:
   - Asserts exact forms `"জেনে ফেলল"` and `"বুঝে ফেললাম"` and confirms `COGNITIVE_ACHIEVEMENT` passes selectional restrictions while pure `STATIVE_POSTURE` (`*থেকে ফেলল`) is rejected.
3. **Polarity-Aware Negation (`tests/test_morphology.py::test_negative_conjugation_polarity`)**:
   - Asserts perfective past-stem negation with `-নি` (`করিনি`, `যায়নি`, `খায়নি`, `হয়নি`, `বলেনি`, `দেখেনি`) and general postverbal `না` for present/future (`করি না`, `করব না`).
4. **Differential Object Marking Engine (`tests/test_realization.py::test_feature_sensitive_dom_realization`)**:
   - Asserts bare direct object for non-specific human occupational nouns (`"আমরা ডাক্তার খুঁজছি।"`) and overt `-কে` for specific human classified nouns (`"শিক্ষক ছাত্রটিকে ডাকলেন।"`).
5. **Polar Question Placement (`tests/test_realization.py::test_polarity_and_question_realization`)**:
   - Asserts both neutral topic-adjacent and sentence-final placements.
6. **Lexicon Isolation (`tests/test_adversarial_invariants.py::test_adversarial_unmodeled_participle_rejected`)**:
   - Asserts unmodeled verbs raise `ConjugationError` to prevent ungrounded algorithmic hallucinations.
