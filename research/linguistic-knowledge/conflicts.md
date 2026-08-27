# Theoretical Linguistic Conflicts & Framework Resolutions — BLF

## 1. Overview
This document records theoretical divergences across primary grammatical sources (`BA-GRAM-2011`, `THOMPSON-GRAM-2012`, `AZAD-SYNTAX-1984`, `ODBL-SKC-1926`) and outlines the formal BLF canonical resolution for computational modeling.

---

## 2. Documented Framework Conflicts

### 2.1 Case Inventory: Traditional Karaka Model vs 4-Case Morphological Model
- **Sources**:
  - `BA-GRAM-2011` (Pramita Bangla Bhashar Byakaran): Retains the traditional 7-karaka/case Sanskrit model (*Karta, Karma, Karana, Sampradana, Apadana, Adhikarana, Sambandha*).
  - `THOMPSON-GRAM-2012` & `ODBL-SKC-1926`: Identify only four genuine morphological inflection cases in modern Bengali (*Nominative -Ø, Objective/Accusative-Dative -ke, Genitive -r/-er, Locative -e/-te/-y*). Traditional *Karana* (*dara, diye*) and *Apadana* (*theke, hoite*) are analyzed as analytic postpositional phrases.
- **Relation**: `RuleRelationType.REFINES` (ID: `REL-CASE-SYSTEM-01`)
- **BLF Canonical Resolution**: BLF models 4 inflectional nominal cases (`blf:nominative`, `blf:accusative_dative_ke`, `blf:genitive`, `blf:locative`) and treats instrumental and ablative relations as postpositional phrases with genitive or direct complements.

---

### 2.2 Compound Verbs: Transformational Embedding vs Aspectual Complex Predicates
- **Sources**:
  - `AZAD-SYNTAX-1984` (Bakkototto): Models compound verbs as deep-structure embedded non-finite clauses undergoing clause-union transformation.
  - `THOMPSON-GRAM-2012`: Models compound verbs as monoclausal aspectual vector verb constructions where the pole verb in `-e` provides lexical meaning and the vector verb contributes telicity, directionality, or benefaction.
- **Relation**: `RuleRelationType.SUPPORTS` / `RuleRelationType.REFINES` (ID: `REL-COMPLEX-PRED-02`)
- **BLF Canonical Resolution**: BLF treats compound verbs as monoclausal complex predicates (`compound:svc` in Universal Dependencies), distinguishing them from true biclausal sequential participial clauses.

---

### 2.3 Perfective Negator 'ni': Defective Auxiliary vs Aspectual Clitic
- **Sources**:
  - `BA-GRAM-2011`: Categorizes 'ni' as a defective past negative particle attaching to present tense verbs.
  - `THOMPSON-GRAM-2012`: Formalizes 'ni' as an aspectual clitic that shifts the temporal reference of a present-stem finite verb to the perfective past.
- **Relation**: `RuleRelationType.REFINES` (ID: `REL-NEG-NI-03`)
- **BLF Canonical Resolution**: BLF enforces rule `RUL-MSYN-NEG-PERFECTIVE` requiring simple present verbal stem inflection before 'ni' and preventing ungrammatical co-occurrence with past *-l-* morphology.
