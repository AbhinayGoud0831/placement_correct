"""
Pure unit test of the weighted-scoring arithmetic, isolated from
sentence-transformers / DB / network so it can run anywhere.
"""


def weighted_fit_score(skills_score, experience_score, education_score,
                        w_skills=0.5, w_experience=0.3, w_education=0.2):
    return round(
        (skills_score * w_skills + experience_score * w_experience + education_score * w_education) * 100,
        2,
    )


def test_perfect_match():
    assert weighted_fit_score(1.0, 1.0, 1.0) == 100.0


def test_zero_match():
    assert weighted_fit_score(0.0, 0.0, 0.0) == 0.0


def test_weights_sum_to_one():
    assert round(0.5 + 0.3 + 0.2, 2) == 1.0


def test_skills_dominant_weight():
    # Same non-skill scores, higher skills score should always yield a higher fit score
    low_skills = weighted_fit_score(0.2, 0.8, 0.8)
    high_skills = weighted_fit_score(0.9, 0.8, 0.8)
    assert high_skills > low_skills


def test_known_value():
    # skills=0.8, experience=0.6, education=0.5
    # 0.8*0.5 + 0.6*0.3 + 0.5*0.2 = 0.4 + 0.18 + 0.1 = 0.68 -> 68.0
    assert weighted_fit_score(0.8, 0.6, 0.5) == 68.0


if __name__ == "__main__":
    test_perfect_match()
    test_zero_match()
    test_weights_sum_to_one()
    test_skills_dominant_weight()
    test_known_value()
    print("All scoring formula tests passed.")
