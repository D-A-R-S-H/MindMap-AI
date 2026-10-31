ALPHA_EARLY = 0.4   # used while a student has fewer than 3 attempts on a concept
ALPHA_LATER = 0.25  # used afterwards
EARLY_ATTEMPTS = 3


def get_level(score: float) -> str:
    """Turn a 0-100 mastery score into Weak / Developing / Strong."""
    if score < 50:
        return "Weak"
    if score < 75:
        return "Developing"
    return "Strong"


def combined_score(recall: float, understanding: float) -> float:
    """S = the average of the recall and understanding scores."""
    return (recall + understanding) / 2


def get_alpha(attempt_count: int) -> float:
    """attempt_count = attempts the student had made BEFORE this one."""
    return ALPHA_EARLY if attempt_count < EARLY_ATTEMPTS else ALPHA_LATER


def update_mastery(old_score: float, recall: float, understanding: float, attempt_count: int) -> float:
    """M_new = M_old + alpha * (S - M_old), kept within 0-100 and rounded."""
    s = combined_score(recall, understanding)
    alpha = get_alpha(attempt_count)
    new_score = old_score + alpha * (s - old_score)
    return round(max(0.0, min(100.0, new_score)), 1)