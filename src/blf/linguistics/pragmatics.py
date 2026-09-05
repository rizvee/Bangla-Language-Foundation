"""
BLF Pragmatics, Register & Conversational Deixis Engine.

Models addressee social deixis (3-tier honorificity), speech act intent,
multi-sense pragmatic particles, and structured interrogative valency disambiguation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class HonorificTier(str, Enum):
    HONORIFIC = "HONORIFIC"        # আপনি / তিনি / উনি
    ORDINARY = "ORDINARY"          # তুমি / সে / ও
    INTIMATE = "INTIMATE"          # তুই / এ / ও


class SocialDistance(str, Enum):
    FORMAL = "FORMAL"
    FAMILIAR = "FAMILIAR"
    INTIMATE = "INTIMATE"


class PowerRelation(str, Enum):
    SUPERIOR = "SUPERIOR"
    EQUAL = "EQUAL"
    SUBORDINATE = "SUBORDINATE"


class VerbValency(str, Enum):
    INTRANSITIVE = "INTRANSITIVE"
    TRANSITIVE = "TRANSITIVE"
    DITRANSITIVE = "DITRANSITIVE"
    UNKNOWN = "UNKNOWN"


# Registered verb valency lexicon for BDSB
VERB_VALENCY_LEXICON: Dict[str, Dict[str, Any]] = {
    # Intransitives
    "যা": {"valency": VerbValency.INTRANSITIVE, "forms": ["যাই", "যাও", "যান", "যাস", "যায়", "যাচ্ছ", "যাচ্ছেন", "যাচ্ছি", "গেলাম", "গেলে", "গেলেন", "গেল", "যাবে", "যাবেন", "যাবি", "গেছে", "গিয়েছে", "গিয়েছেন", "গিয়েছি", "গেছি", "গেছ", "গিয়ে"]},
    "আস": {"valency": VerbValency.INTRANSITIVE, "forms": ["আসি", "আসো", "আসেন", "আসিস", "আসে", "আসছি", "আসছেন", "এলাম", "এলেন", "এলে", "এলো", "এল", "আসবে", "আসবেন", "এসেছে", "এসেছেন", "এসেছি", "এসেছ", "এসে"]},
    "থাক": {"valency": VerbValency.INTRANSITIVE, "forms": ["থাকি", "থাকো", "থাকেন", "থাকিস", "থাকে", "থাকছি", "থাকছেন", "থাকলাম", "থাকলেন", "থাকবে", "থাকবেন", "থেকে", "থেকেছে"]},
    "ঘুম": {"valency": VerbValency.INTRANSITIVE, "forms": ["ঘুমাও", "ঘুমান", "ঘুমায়", "ঘুমাচ্ছি", "ঘুমাচ্ছেন", "ঘুমাল", "ঘুমালেন", "ঘুমাবে", "ঘুমাবেন"]},
    "বস": {"valency": VerbValency.INTRANSITIVE, "forms": ["বসি", "বসো", "বসেন", "বসিস", "বসে", "বসলাম", "বসলেন", "বসল", "বসবে", "বসবেন"]},
    "দাঁড়া": {"valency": VerbValency.INTRANSITIVE, "forms": ["দাঁড়াও", "দাঁড়ান", "দাঁড়ায়", "দাঁড়িয়েছে", "দাঁড়াল", "দাঁড়ালেন"]},
    "হ": {"valency": VerbValency.INTRANSITIVE, "forms": ["হই", "হও", "হন", "হস", "হয়", "হচ্ছে", "হচ্ছেন", "হলাম", "হলেন", "হলো", "হবে", "হবেন", "হোন"]},

    # Transitives
    "খা": {"valency": VerbValency.TRANSITIVE, "forms": ["খাই", "খাও", "খান", "খাস", "খায়", "খাচ্ছি", "খাচ্ছেন", "খেলাম", "খেলে", "খেলেন", "খেল", "খাবে", "খাবেন", "খাবি", "খাইনি", "খায়নি"]},
    "চা": {"valency": VerbValency.TRANSITIVE, "forms": ["চাই", "চাও", "চান", "চাস", "চায়", "চাচ্ছি", "চাচ্ছেন", "চাইলাম", "চাইলেন", "চাইবে", "চাইবেন"]},
    "বল": {"valency": VerbValency.TRANSITIVE, "forms": ["বলি", "বলো", "বলেন", "বলিস", "বলে", "বলছি", "বলছেন", "বললাম", "বললেন", "বলল", "বলবে", "বলবেন", "বলিনি", "বলেনি"]},
    "লিখ": {"valency": VerbValency.TRANSITIVE, "forms": ["লিখি", "লেখো", "লেখেন", "লেখিস", "লেখে", "লিখছি", "লিখছেন", "লিখলাম", "লিখলেন", "লিখল", "লিখবে", "লিখবেন", "লিখিনি", "লেখেনি"]},
    "পড়": {"valency": VerbValency.TRANSITIVE, "forms": ["পড়ি", "পড়ো", "পড়েন", "পড়িস", "পড়ে", "পড়ছি", "পড়ছেন", "পড়লাম", "পড়লেন", "পড়ল", "পড়ল", "পড়বে", "পড়বেন", "পড়িনি", "পড়েনি"]},
    "দেখ": {"valency": VerbValency.TRANSITIVE, "forms": ["দেখি", "দেখো", "দেখেন", "দেখিস", "দেখে", "দেখছি", "দেখছেন", "দেখলাম", "দেখলেন", "দেখল", "দেখবে", "দেখবেন", "দেখিনি", "দেখেনি"]},
    "জান": {"valency": VerbValency.TRANSITIVE, "forms": ["জানি", "জানো", "জানেন", "জানিস", "জানে", "জানলাম", "জানলেন", "জানল", "জানবে", "জানবেন", "জানিনি", "জানেনি"]},
    "বোঝ": {"valency": VerbValency.TRANSITIVE, "forms": ["বুঝি", "বোঝো", "বোঝেন", "বোঝিস", "বোঝে", "বুঝলাম", "বুঝলেন", "বুঝল", "বুঝবে", "বুঝবেন", "বুঝিনি", "বোঝেনি"]},
    "কর": {"valency": VerbValency.TRANSITIVE, "forms": ["করি", "করো", "করেন", "করিস", "করে", "করছি", "করছেন", "করলাম", "করলেন", "করল", "করবে", "করবেন", "করিনি", "করেনি"]},

    # Ditransitives
    "দে": {"valency": VerbValency.DITRANSITIVE, "forms": ["দিই", "দাও", "দেন", "দিস", "দেয়", "দিচ্ছি", "দিচ্ছেন", "দিলাম", "দিলেন", "দিল", "দেবে", "দেবেন", "দিবি", "দিইনি", "দেয়নি"]},
    "নে": {"valency": VerbValency.DITRANSITIVE, "forms": ["নিই", "নাও", "নেন", "নিস", "নেয়", "নিচ্ছি", "নিচ্ছেন", "নিলাম", "নিলেন", "নিল", "নেবে", "নেবেন", "নিবি", "নিইনি", "নেয়নি"]},
    "পাঠা": {"valency": VerbValency.DITRANSITIVE, "forms": ["পাঠাই", "পাঠাও", "পাঠান", "পাঠায়", "পাঠাচ্ছি", "পাঠালেন", "পাঠাল", "পাঠাবে", "পাঠাবেন"]},
}


@dataclass
class ParticleSense:
    """Represents an attested semantic/pragmatic sense of a polyfunctional particle."""
    sense_id: str
    syntactic_position: str
    scope: str
    discourse_function: str
    register: str
    confidence: str  # HIGH, MEDIUM, LOW
    confidence_basis: str
    host_position: Optional[str] = None
    speaker_commitment: Optional[str] = None
    common_ground_relation: Optional[str] = None
    evaluation: Optional[str] = None
    mirativity: Optional[bool] = None
    illocution_type: Optional[str] = None
    evidence_strength: Optional[str] = "HIGH"
    review_status: Optional[str] = "VERIFIED"


@dataclass
class PragmaticParticleSpec:
    particle: str
    is_clitic: bool
    senses: List[ParticleSense]


PRAGMATIC_PARTICLE_REGISTRY: Dict[str, PragmaticParticleSpec] = {
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
                confidence="HIGH",
                confidence_basis="Descriptive consensus in BA-GRAM-2011 and Thompson 2012.",
            ),
            ParticleSense(
                sense_id="SENSE-I-EMPHATIC",
                syntactic_position="Clitic attached to finite/non-finite verb",
                scope="Predicate",
                discourse_function="Emphatic certainty or inevitable consequence (yabei).",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Universal spoken and written BDSB attestation.",
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
                confidence="HIGH",
                confidence_basis="Descriptive consensus in reference grammars.",
            ),
            ParticleSense(
                sense_id="SENSE-O-SCALAR-CONCESSIVE",
                syntactic_position="Clitic on numerals / minimal quantities",
                scope="Constituent",
                discourse_function="Scalar extreme / concessive minimization ('even one').",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Attested in Thompson 2012 p. 188.",
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
                confidence="HIGH",
                confidence_basis="Attested in BA-GRAM-2011 Vol. 2 p. 260.",
            ),
            ParticleSense(
                sense_id="SENSE-TO-PRESUPPOSITION",
                syntactic_position="Pre-verbal or clause-final",
                scope="Clause",
                discourse_function="Appeals to shared common ground or prior consensus.",
                register="COLLOQUIAL_AND_STANDARD",
                confidence="HIGH",
                confidence_basis="Attested in Azad 1984.",
            ),
        ],
    ),
    "না": PragmaticParticleSpec(
        particle="না",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-NA-NEGATION",
                syntactic_position="Post-verbal",
                scope="Predicate/Clause",
                discourse_function="Standard finite clause truth-value negation.",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Universal grammatical invariant.",
            ),
            ParticleSense(
                sense_id="SENSE-NA-CONFIRMATION-TAG",
                syntactic_position="Clause-final",
                scope="Utterance",
                discourse_function="Appeals for addressee confirmation/tag question ('right?').",
                register="COLLOQUIAL_AND_CONVERSATIONAL",
                confidence="HIGH",
                confidence_basis="Attested in Thompson 2012.",
            ),
        ],
    ),
    "যে": PragmaticParticleSpec(
        particle="যে",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-JE-COMPLEMENTIZER",
                syntactic_position="Clause-initial or post-matrix verb",
                scope="Subordinate clause",
                discourse_function="Finite clause complementation ('that...').",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Standard syntactic complementation across formal and colloquial BDSB.",
                host_position="CLAUSE_INITIAL_OR_POST_MATRIX",
                speaker_commitment="NEUTRAL",
                common_ground_relation="INTRODUCES_SUBORDINATE_PROPOSITION",
                evaluation=None,
                mirativity=False,
                illocution_type="DECLARATIVE_COMPLEMENTATION",
                evidence_strength="HIGH",
                review_status="VERIFIED",
            ),
            ParticleSense(
                sense_id="SENSE-JE-EMOTIVE-MIRATIVE",
                syntactic_position="Post-topic / pre-predicate",
                scope="Proposition / Clause",
                discourse_function="Emotive astonishment, mirative discovery, or evidential reminder ('Look, ...!').",
                register="COLLOQUIAL_STANDARD",
                confidence="HIGH",
                confidence_basis="Attested in BA-GRAM-2011 and Bangladesh Accessible Dictionary.",
                host_position="POST_TOPIC_PRE_PREDICATE",
                speaker_commitment="HIGH",
                common_ground_relation="NEW_INFORMATION_ASSERTION",
                evaluation="POSITIVE_OR_NEGATIVE_SURPRISE",
                mirativity=True,
                illocution_type="MIRATIVE_ASSERTION",
                evidence_strength="HIGH",
                review_status="VERIFIED",
            ),
            ParticleSense(
                sense_id="SENSE-JE-CLAUSE-FINAL-EVALUATIVE",
                syntactic_position="Clause-final",
                scope="Clause / Utterance",
                discourse_function="Clause-final evaluative assertion, reminder, mild reproach, or appeal for recognition ('..., you see! / don't you see?').",
                register="COLLOQUIAL_AND_CONVERSATIONAL",
                confidence="HIGH",
                confidence_basis="Documented in Bangladesh Accessible Dictionary (disgust, disappointment, enquiry, remonstrance) and conversational BDSB.",
                host_position="CLAUSE_FINAL",
                speaker_commitment="HIGH",
                common_ground_relation="APPEAL_TO_COMMON_GROUND_OR_RECOGNITION",
                evaluation="EVALUATIVE_REPROACH_OR_REMINDER",
                mirativity=False,
                illocution_type="EVALUATIVE_EXCLAMATIVE",
                evidence_strength="HIGH",
                review_status="VERIFIED",
            ),
            ParticleSense(
                sense_id="SENSE-JE-EMPHATIC-STANCE",
                syntactic_position="Topic-adjacent or pre-verbal",
                scope="Constituent / Proposition",
                discourse_function="Emphatic affirmation, speaker stance, or contrastive focus against doubt.",
                register="COLLOQUIAL_STANDARD",
                confidence="MEDIUM",
                confidence_basis="Attested in Bangladesh Accessible Dictionary (emphasis, disagreement/disapproval) and literary/spoken usage.",
                host_position="TOPIC_ADJACENT",
                speaker_commitment="STRONG_AFFIRMATION",
                common_ground_relation="COUNTER_PRESUPPOSITION",
                evaluation="EMPHATIC_ASSERTION",
                mirativity=False,
                illocution_type="EMPHATIC_ASSERTION",
                evidence_strength="MEDIUM",
                review_status="VERIFIED",
            ),
        ],
    ),
    "বা": PragmaticParticleSpec(
        particle="বা",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-BA-DISJUNCTION",
                syntactic_position="Between coordinating nominals or clauses",
                scope="Coordinated constituents",
                discourse_function="Exclusive or inclusive disjunctive coordination ('or').",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Standard dictionary coordination.",
            ),
            ParticleSense(
                sense_id="SENSE-BA-RHETORICAL-SKEPTICISM",
                syntactic_position="Post-interrogative or post-subject",
                scope="Interrogative clause",
                discourse_function="Rhetorical skepticism or resigned futility ('Why on earth...?').",
                register="LITERARY_AND_COLLOQUIAL",
                confidence="HIGH",
                confidence_basis="Attested in Azad 1984 p. 112.",
            ),
        ],
    ),
    "কি": PragmaticParticleSpec(
        particle="কি",
        is_clitic=False,
        senses=[
            ParticleSense(
                sense_id="SENSE-KI-POLAR-INTERROGATIVE",
                syntactic_position="Pre-verbal, post-topic, or clause-final",
                scope="Proposition",
                discourse_function="Neutral or focused polar (yes/no) truth-value interrogation.",
                register="ALL",
                confidence="HIGH",
                confidence_basis="Universal grammar consensus for BDSB.",
            ),
            ParticleSense(
                sense_id="SENSE-KI-DISJUNCTION",
                syntactic_position="Correlative (ki ... ki ...)",
                scope="Coordinated items",
                discourse_function="Correlative inclusion ('whether X or Y').",
                register="COLLOQUIAL_AND_LITERARY",
                confidence="HIGH",
                confidence_basis="Attested in Thompson 2012.",
            ),
        ],
    ),
}

PRONOUN_MAP = {
    "2": {
        HonorificTier.HONORIFIC: "আপনি",
        HonorificTier.ORDINARY: "তুমি",
        HonorificTier.INTIMATE: "তুই",
    },
    "3": {
        HonorificTier.HONORIFIC: "তিনি",
        HonorificTier.ORDINARY: "সে",
        HonorificTier.INTIMATE: "এ",
    },
}

VERB_SLOT_MAP = {
    "2": {
        HonorificTier.HONORIFIC: "2_HON",
        HonorificTier.ORDINARY: "2_ORD",
        HonorificTier.INTIMATE: "2_INT",
    },
    "3": {
        HonorificTier.HONORIFIC: "3_HON",
        HonorificTier.ORDINARY: "3_ORD",
        HonorificTier.INTIMATE: "3_INT",
    },
}


class PragmaticsEngine:
    """Conversational Pragmatics and Register Realization Engine for BDSB."""

    def __init__(self):
        self.valency_lexicon = VERB_VALENCY_LEXICON

    def disambiguate_ki(self, text: str) -> Dict[str, Any]:
        """
        Disambiguates 'কি' / 'কী' using structured syntactic valency analysis,
        overt argument accounting, and positional context.

        Returns explicit token-level breakdowns with epistemic confidence and review requirements.
        Unknown verb valency yields AMBIGUOUS rather than guessed answers.
        """
        norm = normalize_bangla_text(text)
        clean_text = norm.replace("?", "").replace("।", "").replace("!", "").replace(",", "")
        tokens = clean_text.split()

        results = []
        for idx, token in enumerate(tokens):
            if token in ["কিসের", "কিসে", "কীসে", "কিসেতে"]:
                results.append({
                    "raw_token": token,
                    "normalized_standard_form": token,
                    "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "position_type": self._infer_position_type(idx, len(tokens)),
                    "confidence": "HIGH",
                    "confidence_basis": "Overt oblique/locative case morphology on Wh-stem.",
                    "review_required": False,
                    "reason": "Overt oblique/locative case-marked interrogative Wh-pronoun.",
                })
            elif token == "কী":
                results.append({
                    "raw_token": token,
                    "normalized_standard_form": "কী",
                    "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                    "position_type": self._infer_position_type(idx, len(tokens)),
                    "confidence": "HIGH",
                    "confidence_basis": "Canonical orthographic standard for substantive Wh-pronoun ('what').",
                    "review_required": False,
                    "reason": "Standard orthographic substantive Wh-pronoun ('what').",
                })
            elif token == "কি":
                analysis = self._analyze_ki_valency(tokens, idx)
                results.append(analysis)

        return {"text": text, "disambiguations": results}

    def _infer_position_type(self, idx: int, total_tokens: int) -> str:
        if idx == 0:
            return "CLAUSE_INITIAL"
        elif idx == total_tokens - 1:
            return "SENTENCE_FINAL"
        elif idx == 1:
            return "TOPIC_ADJACENT"
        else:
            return "PRE_VERBAL"

    def _analyze_ki_valency(self, tokens: List[str], ki_idx: int) -> Dict[str, Any]:
        position_type = self._infer_position_type(ki_idx, len(tokens))

        # Detect candidate verb in clause
        detected_verb_root = None
        detected_valency = VerbValency.UNKNOWN
        for t in tokens:
            for root, info in self.valency_lexicon.items():
                if t in info["forms"] or t == root:
                    detected_verb_root = root
                    detected_valency = info["valency"]
                    break
            if detected_verb_root:
                break

        # 1. Unknown Valency Fallback -> AMBIGUOUS
        if detected_valency == VerbValency.UNKNOWN:
            return {
                "raw_token": "কি",
                "normalized_standard_form": "কি / কী (AMBIGUOUS)",
                "syntactic_function": "AMBIGUOUS",
                "position_type": position_type,
                "confidence": "LOW",
                "confidence_basis": "Verb root is unregistered in valency lexicon; argument structure cannot be computed deterministically.",
                "review_required": True,
                "reason": "Unregistered verb valency; context is ambiguous between polar question particle and direct object Wh-pronoun.",
            }

        # 2. Intransitive Verb -> Must be POLAR_INTERROGATIVE_PARTICLE
        if detected_valency == VerbValency.INTRANSITIVE:
            return {
                "raw_token": "কি",
                "normalized_standard_form": "কি",
                "syntactic_function": "POLAR_INTERROGATIVE_PARTICLE",
                "position_type": position_type,
                "confidence": "HIGH",
                "confidence_basis": f"Intransitive verb root '{detected_verb_root}' does not license direct object.",
                "review_required": False,
                "reason": f"Clause predicate '{detected_verb_root}' is intransitive; 'কি' can only function as polar truth-value interrogative.",
            }

        # 3. Transitive / Ditransitive Verb -> Check for overt direct object
        # Overt object candidates: nouns/pronouns other than subject/pronouns
        other_tokens = [t for i, t in enumerate(tokens) if i != ki_idx and t not in ["আমি", "আমরা", "তুমি", "তোমরা", "আপনি", "আপনারা", "সে", "তারা", "তিনি", "তাঁরা", "গতকাল", "আজ", "এখন", "এখনও", "না", "তো"]]
        
        # Check if overt non-verb nominals exist that can serve as direct object
        # (e.g. ভাত, বই, চিঠি, কথা, টাকা, or accusative markers -কে, -টা, -গুলো)
        has_overt_direct_object = False
        for t in other_tokens:
            # If token is not the detected verb and is a substantial nominal
            is_verb_form = any(t in info["forms"] for info in self.valency_lexicon.values())
            if not is_verb_form and len(t) >= 2:
                has_overt_direct_object = True
                break

        if has_overt_direct_object:
            return {
                "raw_token": "কি",
                "normalized_standard_form": "কি",
                "syntactic_function": "POLAR_INTERROGATIVE_PARTICLE",
                "position_type": position_type,
                "confidence": "HIGH",
                "confidence_basis": f"Transitive verb root '{detected_verb_root}' has overt direct object argument; 'কি' is non-argumental polar particle.",
                "review_required": False,
                "reason": "Overt direct object is present; 'কি' functions as truth-value polar question operator.",
            }
        else:
            return {
                "raw_token": "কি",
                "normalized_standard_form": "কী",
                "syntactic_function": "INTERROGATIVE_PRONOUN_SUBSTANTIVE",
                "position_type": position_type,
                "confidence": "HIGH",
                "confidence_basis": f"Transitive verb root '{detected_verb_root}' lacks overt direct object; token fills the direct object thematic slot.",
                "review_required": True,
                "reason": "Token fills mandatory direct object slot of transitive predicate; normatively spelled 'কী' in standard BDSB orthography.",
            }

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

    def analyze_particle_je(self, text: str, token_idx: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyzes the polyfunctional particle 'যে' across syntactic position,
        discourse anchoring, mirativity, and illocutionary force.
        Avoids reduction of particle surface form to deterministic meaning.
        Returns AMBIGUOUS with candidate senses when context permits multiple readings.
        """
        norm = normalize_bangla_text(text)
        clean = norm.replace("!", "").replace("?", "").replace("।", "").replace(",", "")
        tokens = clean.split()

        je_indices = [i for i, t in enumerate(tokens) if t == "যে"]
        if not je_indices:
            return {
                "text": text,
                "particle_present": False,
                "senses": [],
                "is_ambiguous": False,
                "reason": "Particle 'যে' not found in text.",
            }

        target_idx = token_idx if token_idx is not None else je_indices[0]
        total = len(tokens)

        # 1. Clause-Initial or Subordinate Complementizer
        # e.g. "আমি জানি যে সে আসবে"
        matrix_verbs = ["জানি", "জানেন", "জানে", "মনে", "বলে", "বলল", "বললেন", "দেখল", "দেখলেন"]
        if target_idx == 0 or (target_idx > 0 and any(tokens[target_idx - 1].startswith(mv) for mv in matrix_verbs)):
            return {
                "text": text,
                "target_token": "যে",
                "position_type": "CLAUSE_INITIAL_OR_COMPLEMENTIZER",
                "candidate_senses": ["SENSE-JE-COMPLEMENTIZER"],
                "primary_sense": "SENSE-JE-COMPLEMENTIZER",
                "is_ambiguous": False,
                "mirativity": False,
                "confidence": "HIGH",
                "reason": "Syntactic complementizer introducing subordinate declarative proposition.",
            }

        # 2. Clause-Final Position
        # e.g. "আরে, সে এসে গেছে যে!"
        if target_idx == total - 1:
            return {
                "text": text,
                "target_token": "যে",
                "position_type": "CLAUSE_FINAL",
                "candidate_senses": [
                    "SENSE-JE-CLAUSE-FINAL-EVALUATIVE",
                    "SENSE-JE-EMPHATIC-STANCE",
                ],
                "primary_sense": "SENSE-JE-CLAUSE-FINAL-EVALUATIVE",
                "is_ambiguous": False,
                "mirativity": False,
                "confidence": "HIGH",
                "reason": "Clause-final evaluative particle encoding reminder, mild reproach, or evaluative conclusion.",
            }

        # 3. Topic-Adjacent / Pre-Predicate Exclamative (Mirative)
        # e.g. "আরে, সে যে এসে গেছে!"
        has_exclamative_context = any(m in norm for m in ["আরে", "বাহ", "বাঃ", "ওমা", "দেখ"]) or ("!" in norm)
        if has_exclamative_context and target_idx in [1, 2]:
            return {
                "text": text,
                "target_token": "যে",
                "position_type": "TOPIC_ADJACENT_EXCLAMATIVE",
                "candidate_senses": [
                    "SENSE-JE-EMOTIVE-MIRATIVE",
                    "SENSE-JE-EMPHATIC-STANCE",
                ],
                "primary_sense": "SENSE-JE-EMOTIVE-MIRATIVE",
                "is_ambiguous": False,
                "mirativity": True,
                "confidence": "HIGH",
                "reason": "Topic-adjacent exclamative particle encoding speaker astonishment / evidential mirativity.",
            }

        # 4. Unknown or Underspecified Context -> AMBIGUOUS fallback (never guess single sense)
        return {
            "text": text,
            "target_token": "যে",
            "position_type": "MEDIAL_UNDERSPECIFIED",
            "candidate_senses": [
                "SENSE-JE-COMPLEMENTIZER",
                "SENSE-JE-EMOTIVE-MIRATIVE",
                "SENSE-JE-EMPHATIC-STANCE",
            ],
            "primary_sense": "AMBIGUOUS",
            "is_ambiguous": True,
            "mirativity": None,
            "confidence": "LOW",
            "reason": "Context lacks sufficient syntactic or prosodic markers to force a single deterministic discourse sense; requires human review.",
        }

    def analyze_wh_construction(self, text: str) -> Dict[str, Any]:
        """
        Distinguishes Wh-orthography ('কী' vs 'কি') from argument structure construction types
        (e.g. nominative-agentive transitive vs genitive-experiencer modal).
        """
        norm = normalize_bangla_text(text)
        clean = norm.replace("?", "").replace("।", "").replace("!", "").replace(",", "")
        tokens = clean.split()

        has_ki_orthography = "কি" in tokens
        has_kee_orthography = "কী" in tokens
        has_genitive_subject = any(t in ["তোমার", "আমার", "তার", "তাঁর", "আপনার", "তোমাদের", "আমাদের", "তাদের"] for t in tokens)
        has_chai_predicate = "চাই" in tokens

        # Construction type
        if has_genitive_subject and has_chai_predicate:
            construction_type = "GENITIVE_EXPERIENCER_MODAL_WH"
            is_grammatical = True
            register_note = "Structurally valid genitive-experiencer construction with modal/defective predicate 'চাই'."
        elif any(t in ["তুমি", "আমি", "সে", "তিনি", "আপনি"] for t in tokens) and any(t in ["চাও", "চাই", "চায়", "চান"] for t in tokens):
            construction_type = "NOMINATIVE_AGENTIVE_TRANSITIVE_WH"
            is_grammatical = True
            register_note = "Standard nominative-subject transitive Wh-question with finite verb 'চা'."
        else:
            construction_type = "GENERAL_INTERROGATIVE"
            is_grammatical = True
            register_note = "Standard interrogative clause."

        # Orthographic evaluation
        if has_ki_orthography and not has_kee_orthography:
            orthography_status = "NONCANONICAL_OR_POLAR_AMBIGUOUS"
            orthography_note = "Uses 'কি'; standard BDSB substantive Wh-pronoun is 'কী', though 'কি' is common in digital informal writing and polar questions."
        elif has_kee_orthography:
            orthography_status = "CANONICAL_STANDARD_WH"
            orthography_note = "Canonical standard BDSB spelling for substantive Wh-pronoun ('what')."
        else:
            orthography_status = "NO_WH_PARTICLE"
            orthography_note = "No 'কি' or 'কী' token detected."

        return {
            "text": text,
            "construction_type": construction_type,
            "is_grammatical": is_grammatical,
            "orthography_status": orthography_status,
            "register_note": register_note,
            "orthography_note": orthography_note,
        }

