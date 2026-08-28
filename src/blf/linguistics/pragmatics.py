"""
BLF Conversational Register, Pragmatics & Social Deixis Engine.

Provides models and engines for:
1. Social deixis and 3-tier addressee honorificity (Apni, Tumi, Tui).
2. Polyfunctional pragmatic particle and clitic semantics (-i, -o, to, na, je, ba, ki).
3. Context-sensitive and syntactic-frame disambiguation between polar 'ki' and Wh-pronoun 'kee'.
4. Register transformations (Formal, Colloquial, Familiar, Intimate).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class HonorificTier(str, Enum):
    HONORIFIC = "HONORIFIC"  # আপনি / তিনি (-en)
    FAMILIAR = "FAMILIAR"    # তুমি / সে (-o / -e)
    INTIMATE = "INTIMATE"    # তুই / সে (-is / -e)


class Register(str, Enum):
    FORMAL_STANDARD = "FORMAL_STANDARD"
    COLLOQUIAL_STANDARD = "COLLOQUIAL_STANDARD"
    FAMILIAR = "FAMILIAR"
    INTIMATE = "INTIMATE"


PRONOUN_MAP: Dict[str, Dict[HonorificTier, str]] = {
    "2": {
        HonorificTier.HONORIFIC: "আপনি",
        HonorificTier.FAMILIAR: "তুমি",
        HonorificTier.INTIMATE: "তুই",
    },
    "3": {
        HonorificTier.HONORIFIC: "তিনি",
        HonorificTier.FAMILIAR: "সে",
        HonorificTier.INTIMATE: "সে",
    },
}

VERB_SLOT_MAP: Dict[str, Dict[HonorificTier, str]] = {
    "2": {
        HonorificTier.HONORIFIC: "2_HON",
        HonorificTier.FAMILIAR: "2_ORD",
        HonorificTier.INTIMATE: "2_INT",
    },
    "3": {
        HonorificTier.HONORIFIC: "3_HON",
        HonorificTier.FAMILIAR: "3_ORD",
        HonorificTier.INTIMATE: "3_ORD",
    },
}


@dataclass
class ParticleSense:
    sense_id: str
    syntactic_position: str
    scope: str
    discourse_function: str
    register: str
    confidence: float


@dataclass
class PragmaticParticleSpec:
    particle: str
    is_clitic: bool
    senses: List[ParticleSense]


POLYFUNCTIONAL_PARTICLES: Dict[str, PragmaticParticleSpec] = {
    "ই": PragmaticParticleSpec(
        particle="ই",
        is_clitic=True,
        senses=[
            ParticleSense(
                sense_id="SENSE-I-EXCLUSIVE",
                syntactic_position="Clitic attached to NP/PP/Adv",
                scope="Constituent",
                discourse_function="Exclusive/restrictive identification (X alone / precisely X).",
                register="ALL",
                confidence=1.0,
            ),
            ParticleSense(
                sense_id="SENSE-I-EMPHATIC",
                syntactic_position="Clitic attached to finite/non-finite verb",
                scope="Predicate",
                discourse_function="Emphatic certainty or inevitable consequence (yabei).",
                register="ALL",
                confidence=0.95,
            ),
        ],
    ),
    "ও": PragmaticParticleSpec(
        particle="ও",
        is_clitic=True,
        senses=[
            ParticleSense(
                sense_id="SENSE-O-ADDITIVE",
                syntactic_position="Clitic attached to NP/PP/Adv",
                scope="Constituent",
                discourse_function="Inclusive/additive focus (X also / in addition).",
                register="ALL",
                confidence=1.0,
            ),
            ParticleSense(
                sense_id="SENSE-O-SCALAR-CONCESSIVE",
                syntactic_position="Clitic on numerals / minimal quantities",
                scope="Constituent",
                discourse_function="Scalar extreme / concessive minimization ('even one').",
                register="ALL",
                confidence=0.95,
            ),
        ],
    ),
    "তো": PragmaticParticleSpec(
        particle="তো",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-TO-TOPIC-CONTRAST",
                syntactic_position="Post-subject or post-topic constituent",
                scope="Topic constituent",
                discourse_function="Contrastive topic or personal stance ('As for me...').",
                register="COLLOQUIAL_AND_STANDARD",
                confidence=0.95,
            ),
            ParticleSense(
                sense_id="SENSE-TO-PRESUPPOSITION",
                syntactic_position="Pre-verbal or clause-final",
                scope="Clause",
                discourse_function="Appeals to shared common ground or prior consensus.",
                register="COLLOQUIAL_AND_STANDARD",
                confidence=0.95,
            ),
        ],
    ),
    "না": PragmaticParticleSpec(
        particle="না",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-NA-NEGATOR",
                syntactic_position="Post-verbal",
                scope="Predicate",
                discourse_function="Standard propositional clausal negator.",
                register="ALL",
                confidence=1.0,
            ),
            ParticleSense(
                sense_id="SENSE-NA-TAG-QUESTION",
                syntactic_position="Clause-final with rising intonation",
                scope="Clause",
                discourse_function="Confirmation seeking / tag question ('isn't it?').",
                register="COLLOQUIAL_STANDARD",
                confidence=0.95,
            ),
            ParticleSense(
                sense_id="SENSE-NA-DIRECTIVE-SOFTENER",
                syntactic_position="Post-imperative verb",
                scope="Directive act",
                discourse_function="Softens imperative into polite plea or encouragement.",
                register="COLLOQUIAL_STANDARD",
                confidence=0.95,
            ),
        ],
    ),
    "যে": PragmaticParticleSpec(
        particle="যে",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-JE-EMOTIVE-ASSERTION",
                syntactic_position="Post-subject or pre-verbal in assertion",
                scope="Proposition",
                discourse_function="Emotive emphasis, unexpected assertion, or evidential surprise.",
                register="COLLOQUIAL_STANDARD",
                confidence=0.95,
            ),
            ParticleSense(
                sense_id="SENSE-JE-COMPLEMENTIZER",
                syntactic_position="Clause-initial in subordinate clause",
                scope="Subordinate clause",
                discourse_function="Declarative finite complementizer ('that').",
                register="FORMAL_AND_STANDARD",
                confidence=1.0,
            ),
        ],
    ),
    "বা": PragmaticParticleSpec(
        particle="বা",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-BA-DISJUNCTION",
                syntactic_position="Between coordinating nominals/clauses",
                scope="Coordinated items",
                discourse_function="Disjunctive alternative coordinator ('or').",
                register="ALL",
                confidence=1.0,
            ),
            ParticleSense(
                sense_id="SENSE-BA-DUBITATIVE-QUESTION",
                syntactic_position="Post-Wh pronoun or post-clitic -i (e.g. ke-i ba)",
                scope="Interrogative focus",
                discourse_function="Dubitative counter-expectation or rhetorical helplessness.",
                register="COLLOQUIAL_AND_LITERARY",
                confidence=0.95,
            ),
        ],
    ),
    "কি": PragmaticParticleSpec(
        particle="কি",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-KI-POLAR-PARTICLE",
                syntactic_position="Pre-verbal, post-topic, or clause-final",
                scope="Proposition truth-value",
                discourse_function="Neutral yes/no polar interrogative marker.",
                register="ALL",
                confidence=1.0,
            ),
            ParticleSense(
                sense_id="SENSE-KI-RAW-SPELLING-WH",
                syntactic_position="Direct object or predicate nominal slot",
                scope="Argument slot",
                discourse_function="Colloquial/informal digital spelling variant of Wh-pronoun 'কী' ('what').",
                register="INFORMAL_DIGITAL",
                confidence=0.90,
            ),
        ],
    ),
}


class PragmaticsEngine:
    """Pragmatic analysis, register transformation, and particle disambiguation."""

    def __init__(self):
        pass

    def disambiguate_ki(self, text: str) -> Dict[str, Any]:
        """
        Disambiguates whether 'কি' is used as a Polar Question Particle or Wh-Pronoun 'কী'.
        Takes into account syntactic valency, overt arguments, and raw digital spelling habits.
        """
        norm = normalize_bangla_text(text)
        # Strip trailing sentence punctuation
        clean_text = norm.replace("?", "").replace("।", "").replace("!", "").replace(",", "")
        tokens = clean_text.split()
        
        results = []
        for idx, token in enumerate(tokens):
            if token in ["কিসের", "কিসে", "কীসে"]:
                results.append({
                    "token": token,
                    "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "orthography_standard": "CORRECT",
                    "reason": "Overt oblique/locative case-marked interrogative Wh-pronoun.",
                })
            elif token == "কী":
                results.append({
                    "token": token,
                    "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "orthography_standard": "CORRECT",
                    "reason": "Standard orthographic substantive Wh-pronoun ('what').",
                })
            elif token == "কি":
                # Check syntactic context:
                # If preceding verb is transitive and has no other overt object, or if following word is transitive verb needing object:
                # e.g. "তুমি কি চাও?" vs "তুমি কি ভাত খাবে?" vs "তুমি কি যাবে?"
                has_transitive_verb_missing_obj = False
                if "চাও" in tokens or "চান" in tokens or "বলছ" in tokens or "বলছেন" in tokens:
                    if "ভাত" not in tokens and "কথা" not in tokens and "বই" not in tokens and "চিঠি" not in tokens:
                        has_transitive_verb_missing_obj = True

                if has_transitive_verb_missing_obj:
                    results.append({
                        "token": token,
                        "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                        "orthography_standard": "NONSTANDARD_DIGITAL_SPELLING",
                        "intended_standard_form": "কী",
                        "reason": "Token fills mandatory direct object thematic slot; normatively spelled 'কী'.",
                    })
                else:
                    results.append({
                        "token": token,
                        "syntactic_function": "POLAR_INTERROGATIVE_PARTICLE",
                        "orthography_standard": "CORRECT",
                        "reason": "Polar yes/no truth-value interrogative particle.",
                    })

        return {"text": text, "disambiguations": results}

    def transform_addressee_register(
        self,
        verb_root: str,
        tense_base: str,
        target_tier: HonorificTier,
        include_subject: bool = True,
        object_np: Optional[str] = None,
    ) -> str:
        """
        Synthesizes an addressee-directed clause transformed into the specified Honorific Tier.
        """
        pronoun = PRONOUN_MAP["2"][target_tier]
        slot = VERB_SLOT_MAP["2"][target_tier]
        
        key = f"{tense_base}.{slot}"
        conj_table = conjugator.conjugate_root(verb_root)
        verb_form = conj_table.get(key, verb_root)

        elements = []
        if include_subject:
            elements.append(pronoun)
        if object_np:
            elements.append(object_np)
        elements.append(verb_form)

        return " ".join(elements)

    def attach_focus_clitic(self, word: str, clitic: str) -> str:
        """
        Attaches restrictive (-i) or additive (-o) focus clitic conforming to Bangla orthography.
        """
        norm = normalize_bangla_text(word)
        c = normalize_bangla_text(clitic)
        
        if c == "ই":
            return norm + "ই"
        elif c == "ও":
            return norm + "ও"
        return norm + c
