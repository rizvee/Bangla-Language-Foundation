# Bangla Language Foundation: A Grounded Ontological and Evaluation Framework for Bangladeshi Standard Bengali

**Authors**: Bangla Language Foundation Research Group  
**Target Venue**: ACL / EMNLP / LREC-COLING Methodology Paper  
**Status**: Pre-Human Foundation Framework Skeleton (Empirical Sections Pending Human Pilot)

---

## Abstract
Modern natural language processing systems for Bengali frequently struggle with morphosyntactic consistency, complex predicate licensing, and register-sensitive agreement. These deficiencies arise largely from training on noisy web-scraped text without formal linguistic ground truth. We present the Bangla Language Foundation (BLF), an open research initiative establishing an auditable, provenance-grounded framework for Bangladeshi Standard Bengali (BDSB). BLF integrates: (1) a multi-layer linguistic ontology linking descriptive grammatical sources to computational representations; (2) a derivation graph connecting sentence families down to primary library artifacts; (3) a double-blind, candidate-level human review annotation protocol with dual-target agreement metrics; and (4) BLF-Bench, a diagnostic evaluation suite with strict anti-contamination grouping. [EMPIRICAL METRICS, SAMPLE SIZES, AND INTER-ANNOTATOR AGREEMENT SCORES TO BE INSERTED AFTER FORMAL COMPLETION OF THE 40-ITEM CONTROLLED HUMAN PILOT.]

---

## 1. Introduction and Motivation
Contemporary language technologies for South Asian languages face a persistent methodological dilemma. While model scale and corpus volume have increased substantially, grammatical grounding remains fragile. Scraped datasets often conflate formal standard Cholit Bangla with informal internet shorthand, Anglicized romanization (Banglish), and uncurated machine-translated text. Consequently, models reproduce systemic errors in:
- Differential Object Marking (DOM)
- Complex predicate composition and vector verb aspectual licensing
- Honorific subject-verb agreement across sociolinguistic tiers
- Word order variation and discourse particle positioning

Rather than attempting to rectify these issues through post-hoc prompt engineering or unconstrained synthetic data generation, BLF constructs an epistemically traceable ground truth layer. Every rule, claim, and sentence pattern is bound to verifiable primary reference sources (Bangla Academy normative grammars, authoritative syntactic treatises, and attested corpus snapshots).

---

## 2. Linguistic Ontology and Theoretical Framework
The BLF linguistic architecture formalizes Bangladeshi Standard Bengali across six interconnected tiers:

1. **Orthography and Phonology**: Standardized Unicode NFC normalization preserving legitimate ligature controllers (ZWJ/ZWNJ after hasanta) and Bangla Academy banan rules (BA-SPELL-2016).
2. **Inflectional Morphology**: Deterministic inflection matrices for nominal declension (cases: nominative, accusative, genitive, locative; plural markers: -ra/-era, -gulo/-gula, -der) and verbal conjugation across 6 person-honorific slots and 8 tense-aspect combinations.
3. **Differential Object Marking (DOM)**: A multi-factorial model predicting overt accusative marking (`-কে`) versus unmarked bare zero-case (`-Ø`) based on animacy ([+Human], [+Animate], [-Animate]), definiteness, specificity, and topical prominence.
4. **Complex Predicates**: Formalization of compound verbs ($V_1\text{-e} + V_2$) and light verb constructions ($N/Adj + V$). Vector verbs (e.g., *দেওয়া*, *নেওয়া*, *ফেলা*, *ওঠা*, *বসা*) are constrained by selectional restrictions over pole event types.
5. **Construction Grammar & Semantic Frames**: Abstract sentence templates capturing canonical word order (SOV), topicalized OSV, experiencer-dative subject constructions, and polar interrogative placement.
6. **Cross-Framework Alignment**: Universal Dependencies (UD) crosswalk mapping BLF categories to UD_Bengali-BRU and UD_Bengali-PUD with explicit relation tags (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `NO_DIRECT_MAPPING`, `PROVISIONAL`).

---

## 3. Provenance and Derivation Graph
To eliminate circularity and ungrounded generation, BLF enforces backward derivation tracking:
$$\text{SentenceFamily} \longrightarrow \text{SemanticFrame} \longrightarrow \text{Construction} \longrightarrow \text{Rule} \longrightarrow \text{Claim} \longrightarrow \text{Evidence} \longrightarrow \text{Source}$$

- **Claim-Level Evidence Binding**: Each claim specifies the exact publication edition, page/section locator, and quote or paraphrase.
- **Source Integrity**: Sources are audited offline against canonical checksums and catalog identifiers (e.g., Library of Congress LCCN, official institutional repositories).
- **Attestation Corroboration**: Abstract rules are corroborated by attested usage in verified corpora (e.g., IndicCorp v2, Bengali Common Voice, NCTB curriculum materials).

---

## 4. Annotation OS and Human Review Protocol
To ensure high evidentiary standards, human evaluation is conducted under a double-blind, controlled protocol:

- **Reviewer Isolation**: Annotators complete reviews in air-gapped private review packs without access to underlying generation seeds, metadata, or other annotator responses.
- **Candidate-Level Acceptability**: Reviewers score each variant candidate individually rather than picking a single winner, preserving granular data on marginal or dialectal forms.
- **Dual Inter-Annotator Agreement (IAA)**:
  - Pooled Cohen's Kappa, Fleiss' Kappa, and Krippendorff's Alpha for categorical acceptability.
  - Set-theoretic overlap metrics for preferred-candidate selection.
- **Promotion Invariants**: A linguistic record cannot achieve `GOLD` status through automated algorithms or model self-evaluation. Promotion requires verified human consensus and documented arbitrator adjudication.

---

## 5. Constrained Generation and Synthetic Isolation
Where synthetic generation is employed for diagnostic expansion, it is constrained by formal grammars:
- **Anti-Cartesian Restrictions**: Semantic argument slots enforce selectional features (e.g., Ingestion requires [+Animate] Agent and [+Edible] or [+Liquid] Patient).
- **Execution Tagging**: Every synthetically generated record carries the mandatory tag `SYNTHETIC_SOFTWARE_TEST_ONLY`.
- **Zero Production Corpus Invariant**: Synthetic generation scripts are restricted to test fixtures and unit validation; zero bulk synthetic records are released as production data.

---

## 6. BLF-Bench: Diagnostic Probes and Contamination Safeguards
BLF-Bench evaluates models on targeted linguistic phenomena through isolated diagnostic probes:
1. **DOM Accuracy Probe**: Tests prediction of overt vs bare accusative marking.
2. **Complex Predicate Probe**: Tests semantic compatibility of vector verb combinations.
3. **Polarity Probe**: Tests negative particle positioning and morphology (e.g., past simple with *-ni* vs imperfective with *na*).
4. **Honorific Agreement Probe**: Tests subject pronoun to finite verb agreement across intimate, ordinary, and honorific tiers.
5. **Nominal Morphotactics Probe**: Tests structural classifier ordering.

**Contamination Prevention**: All diagnostic splits are partitioned strictly by `sentence_family_id`. No two variants derived from the same base proposition appear across both training and test splits. Verbatim n-gram overlap checks enforce complete partition isolation.

---

## 7. Empirical Results and Discussion
`[EMPIRICAL PILOT PENDING — NO FABRICATED METRICS]`

*Note: In accordance with BLF scientific integrity rules, this section will report actual empirical statistics (inter-annotator agreement coefficients, baseline model diagnostic accuracy, and adjudication resolutions) only after completion of the official 40-item human pilot review study. No synthetic or simulated reviewer scores are reported.*

---

## 8. Limitations and Sociolinguistic Scope
1. **Regional Dialect Breadth**: The current core ontology prioritizes Bangladeshi Standard Bengali (BDSB). While regional markers for Sylheti, Chittagonian, and Rajbanshi are formalized, comprehensive lexical coverage of regional dialects remains ongoing.
2. **Spoken Conversational Registers**: Current attestations focus primarily on edited prose, scripted media, and educational texts. Spoken dialogue phenomena require subsequent expansion.
3. **Sample Size**: The preliminary human pilot is intentionally bounded to 40 diagnostic items to validate instrumentation before scaling.

---

## 9. Ethics and Data Governance
All human review procedures follow formal institutional consent protocols. Annotators receive transparent task disclosures and fair remuneration. Source texts are cited under academic fair-use standards; no copyrighted primary literature is redistributed in bulk.

---

## References
- Azad, Humayun. 1984. *Bakkototto (Bangla Syntax)*. Dhaka University Press.
- Bangla Academy. 2011. *Pramita Bangla Bhashar Byakaran* [Standard Bengali Grammar, 2 Vols.]. Rafiqul Islam and Pabitra Sarkar (Eds.). Dhaka: Bangla Academy.
- Bangla Academy. 2016. *Bangla Academy Promito Bangla Bananer Niyom* [Standard Bengali Spelling Rules]. Dhaka: Bangla Academy.
- Chatterji, Suniti Kumar. 1926. *The Origin and Development of the Bengali Language* (ODBL). Calcutta University Press.
- Klaiman, M. H. 1981. *Volitionality and Animacy in Bengali*. Linguistics 19(7-8): 671-706.
- Thompson, Hanne-Ruth. 2012. *Bengali: A Comprehensive Grammar*. Routledge.
- Universal Dependencies Consortium. 2021. *Universal Dependencies Treebank: Bengali-BRU*.
