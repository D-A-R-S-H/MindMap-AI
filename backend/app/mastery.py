def get_level(score: float) -> str:
    """Turn a 0-100 mastery score into Weak / Developing / Strong."""
    if score < 50:
        return "Weak"
    if score < 75:
        return "Developing"
    return "Strong"