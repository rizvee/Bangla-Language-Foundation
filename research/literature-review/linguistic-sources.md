# Descriptive & Academic Linguistics Review — Phase 0

## 1. Overview
This literature review synthesizes key academic linguistic treatises on the Bangla language across phonology, morphology, syntax, semantics, and sociolinguistics. The purpose is to ground the BLF linguistic ontology, semantic frames, and grammatical constructions in peer-reviewed scientific literature.

---

## 2. Survey of Major Linguistic Authorities

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Major Academic Linguistic Traditions                 │
├───────────────────────────────┬────────────────────────────────────────┤
│ 1. Historical & Comparative   │ Suniti Kumar Chatterji (ODBL, 1926)    │
│    Linguistics                │ Muhammad Shahidullah (1959)            │
│                               │ Sukumar Sen (1942)                     │
├───────────────────────────────┼────────────────────────────────────────┤
│ 2. Formal & Generative Syntax │ Humayun Azad (Bakkototto, 1984)        │
│                               │ Probal Dasgupta (1989, 1993)           │
├───────────────────────────────┼────────────────────────────────────────┤
│ 3. Descriptive & Applied      │ Hanne-Ruth Thompson (Routledge, 2012)  │
│    Grammar                    │ Pabitra Sarkar (1987, 2012)            │
│                               │ Munier Chowdhury (1970)                │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Core Linguistic Phenomena & BLF Modeling Rules

### 3.1 Constituent Order & Information Packaging
- **Sources**: Azad (1984), Dasgupta (1989), Thompson (2012).
- **Linguistic Finding**: Canonical word order in Bangla is Subject-Object-Verb (SOV). However, pragmatic scrambling licenses OSV (topic topicalization), SVO (afterthought / focus), and VSO in spoken colloquial dialogue.
- **BLF Rule**: BLF sentence families model canonical BDSB realizations as SOV while grouping pragmatically shifted realizations (OSV, SVO) as explicit constructional variants within the same sentence family.

### 3.2 Honorific Agreement & Pronominal System
- **Sources**: Azad (*Pronominalization in Bengali*, 1983), Chatterji (1926).
- **Linguistic Finding**: Bangla personal pronouns enforce a strict tripartite honorific distinction in the second person (*Tui* [intimate/inferior], *Tumi* [ordinary/familiar], *Apni* [honorific/formal]) and a bipartite distinction in the third person (*She/Era* [ordinary] vs *Tini/Tãra* [honorific]).
- **BLF Rule**: Verbal inflections must strictly agree with the subject's honorific grade. A mismatch (e.g., *Apni jao* instead of *Apni jan*) is treated as an invalid grammatical realization in BLF quality audits.

### 3.3 Complex Predicates & Compound Verbs (Yukta-Kriya)
- **Sources**: Thompson (2012), Sarkar (2012), Chatterji (1926).
- **Linguistic Finding**: Bangla extensively utilizes complex predicates combining a non-finite conjunctive participle in `-e` with a finite vector/light verb (*dēoa*, *nēoa*, *pōṛa*, *phelā*, *jāwā*, *āsā*, *othā*, *boshā*). The vector verb modifies Aktionsart, aspect, telicity, or psychological orientation (e.g., *kheye phela* [completive/sudden] vs *kheye nēoa* [self-benefactive]).
- **BLF Rule**: Compound verbs are annotated as multi-token complex predicates linked to a unified semantic frame, rather than two isolated verbs.

### 3.4 Pro-Drop (Null Subject) Phenomenon
- **Sources**: Azad (1984), Dasgupta (1989).
- **Linguistic Finding**: Because finite verb inflection uniquely encodes person and honorific status (1st, 2nd, 3rd $\times$ honorific grade), subject pronouns are frequently dropped in natural spoken and colloquial Bangla (*[Ami] kal jabo* $\rightarrow$ *Kal jabo*).
- **BLF Rule**: BLF utterance schemas support explicit pro-drop annotation. Synthetic generators are explicitly constrained against unnatural over-generation of redundant overt subject pronouns.

### 3.5 Case Alignment & Differential Object Marking (-ke)
- **Sources**: Chatterji (1926), Thompson (2012).
- **Linguistic Finding**: The accusative/dative suffix `-ke` is governed by animacy and definiteness. Animate and definite objects take `-ke` (*Ami cheletike dekhechi*), while inanimate and indefinite objects take the zero/unmarked form (*Ami boi porchi*).
- **BLF Rule**: Automatic validation checks enforce differential object marking rules to prevent ungrammatical inanimate `-ke` over-application.

---

## 4. Synthesis for Phase 1 & 2 Ontology Design

| Linguistic Layer | Theoretical Reference | BLF Architectural Implementation |
|---|---|---|
| **Morphology** | Chatterji (1926), BA (2012) | Structured inflectional feature vectors in `Token.morphology` |
| **Syntax & Scrambling**| Azad (1984), Dasgupta (1989) | `ConstructionInstance` specifying voice, constituent order, and topicalization |
| **Pragmatic Clitics** | Thompson (2012) | Particle tagging (`-to`, `-i`, `-o`, `-na`, `-ba`) with conversational implicatures |
| **Semantic Roles** | Fillmore FrameNet / BLF adaptation | Frame-semantic roles (Agent, Patient, Experiencer, Goal, Theme) |
