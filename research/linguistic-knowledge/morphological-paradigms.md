# Morphosyntactic & Inflectional Paradigm Engine — BLF

## 1. Overview & Objectives
The BLF Morphosyntactic & Inflectional Paradigm Engine operationalizes the atomic claims and declarative rules established in Phase 1A into executable, deterministic computational generators and verified paradigm catalogs for Bangladesh Standard Bangla (BDSB).

---

## 2. Nominal Inflection & Suffix Morphotactics

### 2.1 Affix Ordering Rule
Nominal morphology in BDSB follows a strict, non-permuting affix hierarchy:
$$\text{[Noun Root]} \rightarrow \text{[Numeral Classifier]} \rightarrow \text{[Plural Marker]} \rightarrow \text{[Case Suffix]} \rightarrow \text{[Focus Clitic]}$$

Examples:
- *বই + টা + র* $\rightarrow$ **বইটার** (`[Root:বই] [CLF:-টা] [Case:GEN:-র]`)
- *মানুষ + টি + কে* $\rightarrow$ **মানুষটিকে** (`[Root:মানুষ] [CLF:-টি] [Case:ACC:-কে]`)
- *ছেলে + গুলো + তে* $\rightarrow$ **ছেলেগুলোতে** (`[Root:ছেলে] [PL:-গুলো] [Case:LOC:-তে]`)

---

### 2.2 Case Allomorphy Rules

| Case | Conditioning Environment | Suffix Allomorph | Example Stem $\rightarrow$ Output |
|---|---|---|---|
| **Nominative (NOM)** | Unmarked / Direct base | `-Ø` | *মানুষ* $\rightarrow$ **মানুষ**, *বই* $\rightarrow$ **বই** |
| **Accusative (ACC)** | [+Animate, +Definite] | `-ke` | *মানুষ* $\rightarrow$ **মানুষকে**, *শিক্ষক* $\rightarrow$ **শিক্ষককে** |
| | [-Animate] or [-Specific] | `-Ø` (Zero) | *বই* $\rightarrow$ **বই**, *চিঠি* $\rightarrow$ **চিঠি** |
| **Genitive (GEN)** | Vowel-kar stem (া, ি, ী, ু, ূ, ে, ো) | `-r` | *বাড়ি* $\rightarrow$ **বাড়ির**, *ঢাকা* $\rightarrow$ **ঢাকার** |
| | Independent vowel stem (ই, উ, ও, য়) | `-yer` | *বই* $\rightarrow$ **বইয়ের**, *ভাই* $\rightarrow$ **ভাইয়ের** |
| | Consonant-final stem | `-er` | *মানুষ* $\rightarrow$ **মানুষের**, *কলম* $\rightarrow$ **কলমের** |
| **Locative (LOC)** | Consonant-final stem | `-e` | *ঘর* $\rightarrow$ **ঘরে**, *দেশ* $\rightarrow$ **দেশে** |
| | Non-a vowel-kar stem (ি, ী, ু, ূ, ে) | `-te` | *বাড়ি* $\rightarrow$ **বাড়িতে**, *নদী* $\rightarrow$ **নদীতে** |
| | -a / -o vowel stem (া, আ, ও) | `-y` | *ঢাকা* $\rightarrow$ **ঢাকায়**, *মাথা* $\rightarrow$ **মাথায়** |
| | Independent vowel stem (ই, উ, য়) | `-ye` | *বই* $\rightarrow$ **বইয়ে** |

---

## 3. Pronominal Paradigm Matrix

### 3.1 Personal Pronouns & Honorificity Tiers

| Person / Tier | Singular (NOM / ACC / GEN) | Plural (NOM / ACC / GEN) | Social Distance / Register |
|---|---|---|---|
| **1st Person** | *আমি* / *আমাকে* / *আমার* | *আমরা* / *আমাদেরকে* / *আমাদের* | Neutral |
| **2nd Person Honorific** | *আপনি* / *আপনাকে* / *আপনার* | *আপনারা* / *আপনাদেরকে* / *আপনাদের* | Formal, Respectful, Distant |
| **2nd Person Familiar** | *তুমি* / *তোমাকে* / *তোমার* | *তোমরা* / *তোমাদেরকে* / *তোমাদের* | Equal status, Informal, Friendly |
| **2nd Person Intimate** | *তুই* / *তোকে* / *তোর* | *তোরা* / *তোদেরকে* / *তোদের* | Intimate, Peer, Lower status |
| **3rd Person Proximal (Ord)** | *এ* / *একে* / *এর* | *এরা* / *এদেরকে* / *এদের* | Proximal (visible/near) |
| **3rd Person Proximal (Hon)** | *ইনি* / *এঁকে* / *এঁর* | *এঁরা* / *এঁদেরকে* / *এঁদের* | Proximal Honorific |
| **3rd Person Medial (Ord)** | *ও* / *ওকে* / *ওর* | *ওরা* / *ওদেরকে* / *ওদের* | Medial (visible/intermediate) |
| **3rd Person Medial (Hon)** | *উনি* / *ওঁকে* / *ওঁর* | *ওঁরা* / *ওঁদেরকে* / *ওঁদের* | Medial Honorific |
| **3rd Person Distal (Ord)** | *সে* / *তাকে* / *তার* | *তারা* / *তাদেরকে* / *তাদের* | Distal (remote/discourse) |
| **3rd Person Distal (Hon)** | *তিনি* / *তাঁকে* / *তাঁর* | *তাঁরা* / *তাঁদেরকে* / *তাঁদের* | Distal Honorific |

---

## 4. Verbal Conjugation System

### 4.1 Tense-Aspect Paradigm Matrix (Root: *কর-*)

| Tense / Aspect | 1st Person | 2nd Ordinary | 2nd Honorific | 2nd Intimate | 3rd Ordinary | 3rd Honorific |
|---|---|---|---|---|---|---|
| **Simple Present** | *করি* | *করো* | *করেন* | *করিস* | *করে* | *করেন* |
| **Present Continuous** | *করছি* | *করছো* | *করছেন* | *করছিস* | *করছে* | *করছেন* |
| **Present Perfect** | *করেছি* | *করেছো* | *করেছেন* | *করেছিস* | *করেছে* | *করেছেন* |
| **Simple Past** | *করলাম* | *করলে* | *করলেন* | *করলি* | *করল* | *করলেন* |
| **Past Continuous** | *করছিলাম* | *করছিলে* | *করছিলেন* | *করছিলি* | *করছিল* | *করছিলেন* |
| **Past Perfect** | *করেছিলাম* | *করেছিলে* | *করেছিলেন* | *করেছিলি* | *করেছিল* | *করেছিলেন* |
| **Past Habitual** | *করতাম* | *করতে* | *করতেন* | *করতিস* | *করত* | *করতেন* |
| **Simple Future** | *করব* | *করবে* | *করবেন* | *করবি* | *করবে* | *করবেন* |
| **Imperative** | — | *করো* | *করুন* | *কর* | — | — |

---

### 4.2 Non-Finite Participles
- **Conjunctive Participle (`-e`)**: *করে* (*kore*), *গিয়ে* (*giye*), *খেয়ে* (*kheye*), *দিয়ে* (*diye*).
- **Conditional Participle (`-le`)**: *করলে* (*korle*), *গেলে* (*gele*), *খেলে* (*khele*), *দিলে* (*dile*).
- **Infinitive Participle (`-te`)**: *করতে* (*korte*), *যেতে* (*jete*), *খেতে* (*khete*), *দিতে* (*dite*).

---

## 5. Machine-Readable Schema & Validation
All generated paradigms conform strictly to `schemas/v0_1/inflectional_paradigm.schema.json` and are verified by `scripts/validate_paradigms.py` and unit test suite `tests/test_morphology.py`.
