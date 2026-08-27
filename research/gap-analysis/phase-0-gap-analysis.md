# Multi-Dimensional Linguistic Gap Analysis — Phase 0

## 1. Overview
This gap analysis evaluates the existing Bangla language and NLP dataset landscape against the multi-layered requirements of modern natural language understanding, grammar induction, large language model evaluation, and sign language mapping.

Each identified gap is supported by comparative empirical evidence, stated with explicit confidence bounds, and contrasted against existing counter-examples.

---

## 2. Comparative Matrix of Existing Resources

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               Comparative Multi-Layer Evaluation                                 │
├────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬───────────┤
│ Resource           │ Sentence │ Morphol. │ Semantic │ Spoken / │ Regional │ Banglish │ Provenance│
│                    │ Level    │ Depth    │ Frames   │ Dialogue │ Dialects │ Script   │ Audited   │
├────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼───────────┤
│ IndicCorp v2 (bn)  │ Yes      │ No       │ No       │ No       │ No       │ No       │ No (Web)  │
│ UD Bengali Bengal  │ Yes      │ Partial  │ No       │ No       │ No       │ No       │ Yes       │
│ IndicTrans2 (bn)   │ Yes      │ No       │ No       │ No       │ No       │ No       │ Partial   │
│ Bengali.AI Speech  │ Yes      │ No       │ No       │ Prompt   │ Accents  │ No       │ Yes       │
│ QCRI Banglish      │ Pairs    │ No       │ No       │ Social   │ No       │ Translit │ Yes       │
│ SentiraBangla      │ Yes      │ No       │ No       │ Social   │ No       │ Coarse   │ Yes       │
│ SOAS Sylheti       │ Archive  │ Yes      │ No       │ Yes      │ Sylheti  │ Nagri    │ Yes       │
│ BLF (Target Model) │ Families │ Rich     │ Yes      │ Yes      │ Mapped   │ Tagged   │ Tri-Tier  │
└────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴───────────┘
```

---

## 3. Evidence-Backed Gap Analysis Along 10 Dimensions

### Gap 1: Semantic Representation & Frame Semantics
- **Current Landscape**: No verified public FrameNet, PropBank, or comprehensive AMR (Abstract Meaning Representation) resource exists for Bangladesh Standard Bangla. Existing semantic datasets (e.g., XNLI, TyDi QA) assign sentence-level category labels or extract span answers without formalizing event structures, participant roles, or core-frame relations.
- **Evidence**: Analysis of Universal Dependencies `bn_bengal`, IndicGLUE, and Hugging Face Bangla repositories confirms absence of frame-semantic role labeling.
- **Confidence**: High.
- **BLF Contribution**: Introduction of `SemanticFrame` and `SemanticRoles` layer connecting event predicates to participating nominal and adverbial arguments.

### Gap 2: Sentence Family & Paraphrase Clustering
- **Current Landscape**: Existing parallel and paraphrase corpora treat sentences as independent strings. No existing dataset clusters a core proposition across its syntactic permutations (active vs. passive vs. impersonal), pragmatic registers (formal vs. colloquial vs. intimate), and dialectal realizations under a unified family ID.
- **Evidence**: Literature review of IndicTrans, BanglaNMT, and IndicCorp.
- **Confidence**: High.
- **BLF Contribution**: Architecture centered on `SentenceFamily` containing a canonical BDSB utterance linked to all register, dialect, and script realization variants.

### Gap 3: Spoken Conversational Dialogue & Pragmatic Particles
- **Current Landscape**: Over 90% of available text tokens in large Bangla corpora (IndicCorp, OSCAR, mC4) derive from printed news, Wikipedia, and formal literary articles. Conversational particles (`-to`, `-i`, `-o`, `-na`, `-ba`), speech acts, and turn-taking dynamics are systematically underrepresented.
- **Evidence**: Token distribution analysis in Kakwani et al. (2020) and Common Voice prompt reviews.
- **Confidence**: High.
- **BLF Contribution**: Explicit `Register` tagging and multi-turn dialogue acts modeling authentic spoken interaction.

### Gap 4: Regional Language Syntax vs. Isolated Word Glossaries
- **Current Landscape**: Regional language resources (e.g., Bangla Academy Regional Dictionary, SOAS Sylheti collection) exist predominantly as lexical glossaries, phonetic monographs, or audio archives. Existing NLP corpora lack connected sentence-level records with explicit syntactic and morphological mappings linking regional varieties (Sylheti, Chatgaya, Noakhailla, Rangpuri) to canonical BDSB.
- **Evidence**: Literature review of Bangla Academy and ACL Anthology regional language papers.
- **Confidence**: High.
- **BLF Contribution**: Structured regional realization variants sharing sentence family propositions with explicit dialectal feature tags.

### Gap 5: Banglish Transliteration & Token-Level Script Mixing
- **Current Landscape**: Current transliteration corpora (e.g., QCRI Banglish) focus on sentence-level string transliteration. In mixed-script social communication (e.g., English words embedded in Bangla script or Latin script inserted into Bengali syntax), no verified dataset provides token-level script classification, morphological boundary segmentation for hybrid words (e.g., `meeting-e`, `table-ta`), and unified semantic alignment.
- **Evidence**: Analysis of SentiraBangla and QCRI transliteration datasets.
- **Confidence**: High.
- **BLF Contribution**: `CodeSwitchingType` classification with token-level morphosyntactic tagging for hybrid loanword clitics.

### Gap 6: Morphological Feature Depth
- **Current Landscape**: Existing treebanks (UD `bn_bengal`) annotate basic Universal POS and a subset of morphological features (Number, Person, Case). They omit fine-grained language-specific features crucial for Bangla: honorific grades on 2nd/3rd person verbs, Aktionsart of vector compound verbs, emphatic clitics, and classifier suffixes (`-ta`, `-ti`, `-khana`, `-gulo`).
- **Evidence**: Universal Dependencies `bn_bengal` feature inspection.
- **Confidence**: High.
- **BLF Contribution**: Typed morphological feature tuples in `Token.morphology` covering full person-honorific-aspect-clitic paradigms.

### Gap 7: Synthetic Transparency & Provenance Tracking
- **Current Landscape**: Large modern datasets frequently incorporate synthetic back-translation or model-generated text without explicit metadata regarding generator identity, prompt templates, run dates, or human verification status.
- **Evidence**: Analysis of recent web-scale multilingual datasets (e.g., BPCC, mC4).
- **Confidence**: High.
- **BLF Contribution**: Strict Tri-Tier Quality Model (`GOLD`, `SILVER`, `SYNTHETIC`) with mandatory `SyntheticProvenance` metadata blocks.

### Gap 8: Benchmark Contamination & Train/Test Split Leakage
- **Current Landscape**: Standard public benchmarks for Indic languages frequently suffer from pretraining data contamination, where test sentences appear verbatim in web-crawled pretraining corpora.
- **Evidence**: Recent evaluation studies on multilingual LLM benchmarks (IndicGLUE, BELEBELE).
- **Confidence**: High.
- **BLF Contribution**: Cryptographically isolated, human-verified diagnostic evaluation splits with explicit provenance audits.

### Gap 9: Multi-Modal & Sign Language (BdSL) Alignment
- **Current Landscape**: Existing Bangla datasets provide zero structural alignment between spoken/written grammar and Bangladeshi Sign Language (BdSL) spatial-temporal syntax.
- **Evidence**: Systematic review of South Asian accessibility and sign language literature.
- **Confidence**: High.
- **BLF Contribution**: Schema anticipation of gloss-level semantic role mapping for future BdSL spatial grammar integration.

### Gap 10: Translationese & English SVO Calque Distortion
- **Current Landscape**: Large parallel machine-translation corpora (e.g., IndicTrans2) are populated by translated English sentences that enforce literal Subject-Verb-Object (SVO) phrasing, distorting natural Bengali information structure and compound verb usage.
- **Evidence**: Error analysis of translated bitext in Ramesh et al. (2022).
- **Confidence**: High.
- **BLF Contribution**: Native speaker gold seed constructions grounding natural SOV constituent ordering and authentic complex predicates.
