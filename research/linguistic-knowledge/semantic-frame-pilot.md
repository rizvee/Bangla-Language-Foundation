# Semantic Frame Core & Construction Alignment — BLF

## 1. Objectives & Architecture
The BLF Semantic Frame layer models event structures, thematic roles, and lexical realization constraints for Bangladesh Standard Bangla (BDSB). Designed to ground natural sentence generation and provide an interoperable semantic foundation for future sign language (BdSL) mapping, each frame specifies:
1. **Thematic Role Inventory**: Mandatory and optional participant roles.
2. **Syntactic Construction Linkage**: Compatible clause patterns from the construction catalog.
3. **Lexical Predicate Evocation**: Bangla verb roots, lemmas, and light verb constructions.

---

## 2. Standardized Thematic Role Inventory

| Semantic Role | Definition & Prototypical Function | Canonical Bangla Case Realization |
|---|---|---|
| **AGENT** | Volitional initiator of an action. | Nominative ($\emptyset$) |
| **EXPERIENCER** | Entity experiencing a mental, emotional, or sensory state. | Nominative ($\emptyset$) or Dative/Genitive (`-ke`/`-er`) |
| **PATIENT** | Entity undergoing a change of state or physical effect. | Accusative/DOM (`-ke` for animate definite, `-\emptyset` for inanimate) |
| **THEME** | Entity undergoing motion, transfer, or stative locatedness. | Nominative / Accusative ($\emptyset$) |
| **RECIPIENT** | Entity receiving possession or information. | Dative (`-ke`) |
| **BENEFICIARY** | Entity for whose advantage an action is performed. | Dative (`-ke`) or Postpositional (*-r jonno*) |
| **GOAL** | Spatial or abstract destination of motion/transfer. | Locative (`-e`/`-te`/`-y`) or Postpositional (*-r kache*) |
| **SOURCE** | Origin point of motion or transfer. | Postpositional (*theke* / *hote*) |
| **LOCATION** | Physical setting of an event or state. | Locative (`-e`/`-te`/`-y`) |
| **STIMULUS** | External entity triggering an experiencer state. | Nominative ($\emptyset$) |
| **CONTENT** | Information or proposition communicated or cognized. | Clausal complement or Direct nominal ($\emptyset$) |
| **ATTRIBUTE** | Property or classification assigned to a Theme. | Nominative ($\emptyset$) |
| **POSSESSOR** | Entity possessing a Theme in existential/possessive frames. | Genitive (`-r`/`-er`/`-yer`) |

---

## 3. Core Communicative Frames Summary (24 Verified Frames)
- **Motion & Translocation**: `FRAME-MOTION-TRANSLOCATION`, `FRAME-MOTION-DIRECTIONAL`
- **Possession & Commerce**: `FRAME-GIVING-TRANSFER`, `FRAME-RECEIVING-ACQUISITION`, `FRAME-COMMERCE-BUY`, `FRAME-POSSESSION-EXISTENTIAL`
- **Ingestion & Biology**: `FRAME-INGESTION-FOOD`, `FRAME-INGESTION-LIQUID`, `FRAME-SLEEP-PHYSIOLOGICAL`
- **Perception & Cognition**: `FRAME-PERCEPTION-VISUAL`, `FRAME-PERCEPTION-AUDITORY`, `FRAME-COGNITION-KNOWING`, `FRAME-COGNITION-THINKING`
- **Communication & Social**: `FRAME-COMMUNICATION-STATEMENT`, `FRAME-COMMUNICATION-REQUEST`, `FRAME-COMMUNICATION-QUESTION`, `FRAME-ASSISTANCE-HELPING`
- **Emotion & Sensations**: `FRAME-EMOTION-FEAR`, `FRAME-EMOTION-HAPPINESS`, `FRAME-SENSATION-HUNGER`
- **Action & Creation**: `FRAME-ACTIVITY-WORK`, `FRAME-CREATION-WRITING`
- **Stative & Spatial**: `FRAME-STATE-BEING-EQUATIVE`, `FRAME-STATE-LOCATION`
