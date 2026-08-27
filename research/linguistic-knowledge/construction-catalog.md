# BDSB Construction Grammar Catalog — BLF

## 1. Theoretical Architecture
The BLF Construction Grammar layer formalizes the morphosyntactic clause patterns of Bangladesh Standard Bangla (BDSB). In contrast to template-based generation, constructions are pairings of form (syntactic configuration, word order, case government, agreement) and meaning (semantic roles, information structure, register constraints).

---

## 2. Core Construction Typology

### 2.1 Declarative Clause Patterns

| Construction ID | Name | Word Order | Semantic Roles | Case & Morphological Constraints |
|---|---|---|---|---|
| `CONST-DECL-TRANSITIVE-SOV` | Transitive SOV | `SOV` | AGENT, PATIENT | Subject takes NOM; Object follows DOM (`-ke` for animate definite, `-Ø` for inanimate); Verb agrees with Subject. |
| `CONST-DECL-INTRANSITIVE-SV` | Intransitive SV | `SV` | AGENT / THEME | Subject takes NOM; Verb agrees with Subject. |
| `CONST-DECL-DITRANSITIVE` | Ditransitive Transfer | `S_IO_DO_V` | AGENT, RECIPIENT, THEME | Indirect Object takes Dative `-ke`; Direct Object takes direct/DOM; IO canonically precedes DO. |

---

### 2.2 Copular, Existential & Experiencer Patterns

| Construction ID | Name | Syntactic Pattern | Affirmative Form | Negative Form |
|---|---|---|---|---|
| `CONST-COPULAR-EQUATIVE` | Identificational Copular | `NP[Nom] NP[Nom] (NEG)` | Zero Copula ($\emptyset$) | *নয়* / *নন* (*noy* / *non*) |
| `CONST-EXISTENTIAL-POSSESSIVE` | Existential / Possessive | `NP[Loc/Gen] NP[Nom] COP` | *আছে* (*ache*) | *নেই* (*nei*) |
| `CONST-EXPERIENCER-DATSUBJ` | Experiencer Dative Subject | `NP[Gen/Dat] NP[Nom] VP` | Default 3rd person verb agreement (no agreement with Experiencer). | Standard post-verbal *না* (*na*) |

---

### 2.3 Interrogative & Imperative Formations

| Construction ID | Functional Type | Structural Properties |
|---|---|---|
| `CONST-INTERROGATIVE-POLAR` | Polar (Yes/No) Question | Pre-verbal question particle *কি* (*ki*) with rising final intonation contour. |
| `CONST-INTERROGATIVE-WH-INSITU` | Content Question | In-situ Wh-phrase (*কে*, *কী*, *কোথায়*, *কখন*, *কেন*) without mandatory fronting. |
| `CONST-IMPERATIVE-HONORIFIC` | Polite Directive | Subject *আপনি* (overt or null); Verb takes imperative suffix `-un` (*করুন*, *বলুন*). |
| `CONST-PROHIBITIVE-NEGATIVE` | Prohibitive Directive | Imperative verb stem followed by post-verbal negator *না* (*করবেন না*, *করো না*). |

---

### 2.4 Complex Biclausal Patterns

| Construction ID | Pattern Name | Structural Linker | Matrix Relation |
|---|---|---|---|
| `CONST-COMPLEX-CONJUNCTIVE` | Sequential Participle | Non-finite participle in `-e` (*করে*, *গিয়ে*) | Strict subject coreference in unmarked clauses. |
| `CONST-COMPLEX-CONDITIONAL-SYNTHETIC` | Synthetic Conditional | Protasis verb in `-le` (*করলে*, *গেলে*) | Apodosis clause expresses consequence. |
| `CONST-COMPLEX-CORRELATIVE` | Relative-Correlative | $J$-series pronoun (*যে*, *যিনি*, *যা*, *যখন*) | Matrix $T$-series correlative (*সে*, *তিনি*, *তা*, *তখন*). |

---

### 2.5 Information Structure Patterns

| Construction ID | Pragmatic Function | Structural Mechanism |
|---|---|---|
| `CONST-INFO-TOPICALIZATION-OSV` | Left-Topicalization | Direct Object fronted to clause-initial slot ($O S V$) preserving case marking. |
| `CONST-INFO-PRODROP-SUBJECT` | Null Subject (Pro-Drop) | Subject pronoun omitted ($\emptyset$) when recoverable from verb agreement inflection. |
