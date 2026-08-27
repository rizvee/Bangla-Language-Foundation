"""
Linguistic taxonomy and categorization enums for Bangla Language Foundation.
"""

from enum import Enum


class Register(str, Enum):
    FORMAL_STANDARD = "formal_standard"
    COLLOQUIAL_STANDARD = "colloquial_standard"
    INTIMATE_CONVERSATIONAL = "intimate_conversational"
    SOCIAL_CHAT_SHORTHAND = "social_chat_shorthand"
    ARCHAIC_SADHU = "archaic_sadhu"


class Dialect(str, Enum):
    BDSB_STANDARD = "bdsb_standard"
    DHAKA_COLLOQUIAL = "dhaka_colloquial"
    CHITTAGONG_CHATGAYA = "chittagong_chatgaya"
    SYLHETI = "sylheti"
    NOAKHALI_NOAKHAILLA = "noakhali_noakhailla"
    RANGPUR_RAJBANSHI = "rangpur_rajbanshi"
    BARISAL = "barisal"
    RAJSHAHI_VARENDRA = "rajshahi_varendra"
    WEST_BENGAL_STANDARD = "west_bengal_standard"


class CodeSwitchingType(str, Enum):
    PURE_BANGLA = "pure_bangla"
    LOANWORD_BANGLA_SCRIPT = "loanword_bangla_script"
    CODE_SWITCHED_LATIN = "code_switched_latin"
    ROMANIZED_BANGLISH = "romanized_banglish"
    MIXED_SCRIPT = "mixed_script"


class QualityTier(str, Enum):
    GOLD = "GOLD"
    SILVER = "SILVER"
    SYNTHETIC = "SYNTHETIC"


class SourceTier(str, Enum):
    TIER_A = "TIER_A"
    TIER_B = "TIER_B"
    TIER_C = "TIER_C"
    TIER_D = "TIER_D"
    TIER_E = "TIER_E"


class ValidationStatus(str, Enum):
    PASSED = "passed"
    PROVISIONAL = "provisional"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    REJECTED = "rejected"
