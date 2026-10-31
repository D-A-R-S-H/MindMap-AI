from app.mastery import combined_score, get_alpha, get_level, update_mastery


def test_level_boundaries():
    assert get_level(0) == "Weak"
    assert get_level(49.9) == "Weak"
    assert get_level(50) == "Developing"
    assert get_level(74.9) == "Developing"
    assert get_level(75) == "Strong"
    assert get_level(100) == "Strong"


def test_combined_score_is_the_average():
    assert combined_score(80, 60) == 70


def test_alpha_switches_at_three_attempts():
    assert get_alpha(0) == 0.4
    assert get_alpha(2) == 0.4
    assert get_alpha(3) == 0.25
    assert get_alpha(10) == 0.25


def test_mastery_rises_towards_a_high_score():
    # 50 + 0.4 * (100 - 50) = 70
    assert update_mastery(50, 100, 100, attempt_count=0) == 70.0
    # 50 + 0.25 * (100 - 50) = 62.5
    assert update_mastery(50, 100, 100, attempt_count=5) == 62.5


def test_mastery_falls_after_a_poor_answer():
    # 80 + 0.4 * (40 - 80) = 64
    assert update_mastery(80, 40, 40, attempt_count=0) == 64.0


def test_mastery_stays_between_0_and_100():
    assert update_mastery(100, 100, 100, attempt_count=0) == 100.0
    assert update_mastery(0, 0, 0, attempt_count=0) == 0.0