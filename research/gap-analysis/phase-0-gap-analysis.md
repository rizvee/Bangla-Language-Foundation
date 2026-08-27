# Multi-Dimensional Linguistic Gap Analysis — Phase 0

## 1. Overview & Epistemic Scope
This gap analysis evaluates the existing Bangla language and NLP dataset ecosystem against the multi-layered requirements of natural language understanding, grammar induction, large language model evaluation, and sign language mapping.

Every identified gap is evaluated against field-level verified resources in the BLF source registry (`sources/registry/sources.json`) and classified with an explicit epistemic status:
- **`[SUPPORTED]`**: Backed by direct evidence from primary literature and verified datasets.
- **`[PARTIALLY_SUPPORTED]`**: Supported by observed trends across major corpora but lacking exhaustive cross-domain census.
- **`[NOT_YET_VERIFIED]`**: Plausible hypothesis awaiting empirical verification in later project phases.

---

## 2. Comparative Matrix of Verified Resources

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               Comparative Multi-Layer Evaluation                                 │
├────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬───────────┤
│ Resource           │ Sentence │ Morphol. │ Semantic │ Spoken / │ Regional │ Banglish │ Provenance│
│                    │ Level    │ Depth    │ Frames   │ Dialogue │ Dialects │ Script   │ Audited   │
├────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼───────────┤
│ IndicCorp v2 (bn)  │ Yes      │ No       │ No       │ No       │ No       │ No       │ Web CC0   │
│ Bangla2B+ (BUET)   │ Docs     │ No       │ No       │ No       │ No       │ No       │ Verified  │
│ UD Bengali BRU     │ 56 sents │ Basic    │ No       │ No       │ No       │ No       │ Verified  │
│ UD Bengali PUD     │ 1k sents │ Basic    │ No       │ No       │ No       │ No       │ Parallel  │
│ BanglaNMT (BUET)   │ 2.75M pr │ No       │ No       │ No       │ No       │ No       │ Verified  │
│ Bengali.AI Speech  │ Audio    │ No       │ No       │ Prompt   │ Accents  │ No       │ Verified  │
│ BanglaTLit (2024)  │ 42.7k pr │ No       │ No       │ Social   │ No       │ Translit │ Verified  │
│ BnSentMix (2025)   │ 20k sents│ No       │ No       │ Social   │ No       │ Coarse   │ Verified  │
│ SOAS Sylheti (2014)│ Monograph│ Yes      │ No       │ Yes      │ Sylheti  │ Nagri/IPA│ Verified  │
│ BLF (Target Model) │ Families │ Rich     │ Yes      │ Yes      │ Mapped   │ Tagged   │ Tri-Tier  │
└────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴───────────┘
```

---

## 3. Evidence-Backed Gap Analysis Along 10 Dimensions

### Gap 1: Semantic Frame & Event Structure Representation `[SUPPORTED]`
- **Current Landscape**: No verified public FrameNet, PropBank, or comprehensive Abstract Meaning Representation (AMR) resource was identified for Bangladesh Standard Bangla (BDSB). Existing semantic datasets (e.g., XNLI-bn, TyDi QA-bn) assign sentence-level category labels or extract answer spans without formalizing event frames, core participants (Agent, Patient, Experiencer), or thematic relations.
- **Evidence**: Inspection of Universal Dependencies (`UD_Bengali-BRU`), IndicGLUE, and ACL Anthology repositories confirms the absence of frame-semantic role labeling.
- **BLF Target**: Introduction of `SemanticFrame` and `SemanticRoles` layers connecting event predicates to participating nominal and adverbial arguments.

### Gap 2: Sentence Family & Paraphrase Clustering `[SUPPORTED]`
- **Current Landscape**: No verified resource identified in the Phase 0 search clusters a core proposition across its grammatical permutations (active vs. passive vs. impersonal), pragmatic registers (formal vs. colloquial vs. intimate), and dialectal realizations under a unified proposition family identifier. Existing parallel and paraphrase corpora treat sentences as independent strings.
- **Evidence**: Literature review of BanglaNMT (Hasan et al., 2020), IndicTrans2 (Ramesh et al., 2023), and IndicCorp v2 (Kakwani et al., 2020).
- **BLF Target**: Architecture centered on `SentenceFamily` containing a canonical BDSB utterance linked to all register, dialect, and script realization variants.

### Gap 3: Spoken Conversational Dialogue & Pragmatic Particles `[PARTIALLY_SUPPORTED]`
- **Current Landscape**: The vast majority of published text tokens in large Bangla corpora (IndicCorp, Bangla2B+, OSCAR) derive from printed news, Wikipedia, and formal literary articles. Conversational pragmatic particles (`-to`, `-i`, `-o`, `-na`, `-ba`), discourse markers, and turn-taking structures are systematically underrepresented in written training sets.
- **Evidence**: Token distribution analysis in Kakwani et al. (2020) and Common Voice prompt reviews.
- **Limitation**: While colloquial speech exists on social platforms and video captions, structured open dialogue corpora with pragmatic turn annotations remain sparse.
- **BLF Target**: Explicit `Register` tagging and multi-turn dialogue acts modeling authentic spoken interaction.

### Gap 4: Regional Language Syntax vs. Isolated Word Glossaries `[SUPPORTED]`
- **Current Landscape**: Regional language documentation (e.g., Bangla Academy *Ancholik Bhashar Abhidhan*, SOAS Sylheti publications) exists predominantly as lexical glossaries, phonetic monographs, or audio recordings. No verified machine-readable NLP dataset provides connected sentence-level records with explicit syntactic and morphological mappings linking regional varieties (Sylheti, Chatgaya, Noakhailla, Rangpuri) to canonical BDSB.
- **Evidence**: Review of Bangla Academy records and SOAS Sylheti Project literature (Simard et al., 2014).
- **BLF Target**: Structured regional realization variants sharing sentence family propositions with explicit dialectal feature tags.

### Gap 5: Banglish Transliteration & Token-Level Script Mixing `[SUPPORTED]`
- **Current Landscape**: While benchmark datasets for sentence-level back-transliteration (BanglaTLit; Fahim et al., 2024) and code-mixed sentiment classification (BnSentMix; Alam et al., 2025) exist, no verified dataset provides token-level script classification combined with morphological boundary segmentation for hybrid words (e.g., English noun + Bengali locative clitic `office-e`, `table-ta`) and semantic frame alignment.
- **Evidence**: Analysis of BanglaTLit and BnSentMix annotation schemas.
- **BLF Target**: `CodeSwitchingType` classification with token-level morphosyntactic tagging for hybrid loanword clitics.

### Gap 6: Morphological Feature Depth `[SUPPORTED]`
- **Current Landscape**: The primary official Bangladesh dependency treebank in Universal Dependencies (`UD_Bengali-BRU`) contains only 56 sentences and 320 tokens. Existing resources lack fine-grained language-specific morphological features crucial for Bangla: tripartite honorific grades on verbs, Aktionsart of vector compound verbs in `-e + V`, and emphatic clitics.
- **Evidence**: Universal Dependencies `bn_bru` repository metadata.
- **BLF Target**: Typed morphological feature tuples in `Token.morphology` covering full person-honorific-aspect-clitic paradigms.

### Gap 7: Synthetic Transparency & Provenance Tracking `[SUPPORTED]`
- **Current Landscape**: Large modern multilingual corpora frequently incorporate synthetic back-translation or model-generated text without machine-readable provenance metadata regarding generator model, prompt templates, or human verification status.
- **Evidence**: Survey of web-scale datasets (e.g., BPCC, mC4).
- **BLF Target**: Strict Tri-Tier Quality Architecture (`GOLD`, `SILVER`, `SYNTHETIC`) with mandatory `SyntheticProvenance` metadata blocks.

### Gap 8: Benchmark Contamination & Diagnostic Isolation `[SUPPORTED]`
- **Current Landscape**: Standard public benchmarks for Indic languages frequently suffer from pretraining data contamination, where test sentences appear in web-crawled training corpora.
- **Evidence**: Recent evaluation studies on multilingual benchmarks (IndicGLUE, BELEBELE).
- **BLF Target**: Cryptographically isolated, human-verified diagnostic evaluation splits.

### Gap 9: Multi-Modal & Bangladeshi Sign Language (BdSL) Alignment `[SUPPORTED]`
- **Current Landscape**: No verified linguistic dataset bridges written/spoken Bangla grammar with Bangladeshi Sign Language (BdSL) spatial-temporal syntax at the semantic frame level.
- **Evidence**: Systematic review of South Asian accessibility literature.
- **BLF Target**: Schema anticipation of gloss-level semantic role mapping for future BdSL spatial grammar integration.

### Gap 10: Translationese Distribution Analysis in Parallel Corpora `[NOT_YET_VERIFIED]`
- **Status**: The hypothesis that parallel MT corpora (e.g., BPCC) contain systematically distorted constituent order (SVO calques) is plausible based on general MT literature, but has not yet been quantified with a reproducible statistical sample study for Bangla.
- **BLF Action**: Downgraded from an absolute assertion to an empirical hypothesis to be tested via diagnostic parsing probes in Phase 8.
