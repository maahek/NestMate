"""
NestMate — AI Roommate Matching Engine
Feature 1: Personality + Budget + Lifestyle Compatibility

Algorithm Overview:
  - 8 weighted dimensions are scored independently (0–100 each)
  - Weighted sum gives final compatibility score (0–100)
  - Each dimension uses domain-specific scoring logic
  - Result includes: score, breakdown, verdict, highlights, conflicts

Dimension Weights (must sum to 1.0):
  budget           → 25%  (most critical — must overlap financially)
  sleep_schedule   → 18%  (daily rhythm compatibility)
  smoking          → 15%  (hard preference — non-negotiable for many)
  pets             → 10%  (allergies and cleanliness impact)
  cleanliness      → 10%  (scale 1–5, closeness matters)
  guests_frequency →  8%  (social habits)
  work_schedule    →  7%  (home overlap affects harmony)
  diet             →  7%  (kitchen sharing implications)
"""

"""
NestMate — Roommate Compatibility Engine
8-dimension weighted scoring algorithm.
"""

WEIGHTS = {
    'budget':           0.25,
    'sleep_schedule':   0.18,
    'smoking':          0.15,
    'pets':             0.10,
    'cleanliness':      0.10,
    'guests_frequency': 0.08,
    'work_schedule':    0.07,
    'diet':             0.07,
}

# ── Dimension scorers ──────────────────────────────────────────────────────────

def score_budget(a, b) -> float:
    """Overlap of budget ranges → 0 to 100"""
    try:
        a_min = float(getattr(a, 'budget_min', 0) or 0)
        a_max = float(getattr(a, 'budget_max', 0) or 0)
        b_min = float(getattr(b, 'budget_min', 0) or 0)
        b_max = float(getattr(b, 'budget_max', 0) or 0)

        # If either has no budget set, give neutral score
        if a_max == 0 or b_max == 0:
            return 70.0

        overlap_start = max(a_min, b_min)
        overlap_end   = min(a_max, b_max)

        if overlap_end < overlap_start:
            # No overlap — score based on how far apart they are
            gap   = overlap_start - overlap_end
            scale = max(a_max, b_max)
            return max(0.0, 100.0 - (gap / scale) * 200)

        # Overlap exists
        overlap = overlap_end - overlap_start
        total   = max(a_max, b_max) - min(a_min, b_min)
        if total == 0:
            return 100.0
        return min(100.0, (overlap / total) * 100 + 40)

    except Exception:
        return 70.0


def score_exact(val_a, val_b) -> float:
    """Exact match → 100, no match → 0"""
    if val_a is None or val_b is None:
        return 70.0
    return 100.0 if str(val_a) == str(val_b) else 0.0


def score_boolean(val_a, val_b) -> float:
    """Boolean match → 100, mismatch → 20"""
    a = bool(val_a)
    b = bool(val_b)
    return 100.0 if a == b else 20.0


def score_cleanliness(a, b) -> float:
    """Numeric 1-5 closeness"""
    try:
        diff = abs(float(a or 3) - float(b or 3))
        return max(0.0, 100.0 - diff * 25)
    except Exception:
        return 70.0


def score_sleep(a, b) -> float:
    order = {'early_bird': 0, 'flexible': 1, 'night_owl': 2}
    va    = order.get(str(a), 1)
    vb    = order.get(str(b), 1)
    diff  = abs(va - vb)
    return [100.0, 50.0, 10.0][diff]


def score_guests(a, b) -> float:
    order = {'never': 0, 'rarely': 1, 'sometimes': 2, 'often': 3}
    va    = order.get(str(a), 1)
    vb    = order.get(str(b), 1)
    diff  = abs(va - vb)
    return max(0.0, 100.0 - diff * 33)


def score_work(a, b) -> float:
    if a == b:
        return 100.0
    compatible = {
        ('day_shift', 'wfh'),
        ('wfh', 'day_shift'),
        ('student', 'wfh'),
        ('wfh', 'student'),
    }
    if (str(a), str(b)) in compatible:
        return 70.0
    if 'night_shift' in (str(a), str(b)):
        return 30.0
    return 50.0


def score_diet(a, b) -> float:
    if a == b:
        return 100.0
    if 'any' in (str(a), str(b)):
        return 80.0
    if set([str(a), str(b)]) == {'veg', 'vegan'}:
        return 85.0
    return 20.0


# ── Main function ──────────────────────────────────────────────────────────────

def calculate_compatibility(profile_a, profile_b) -> dict:
    """
    Calculate compatibility score between two RoommateProfile objects.
    Returns score 0-100 plus breakdown and highlights.
    """

    def get(profile, field, default=None):
        return getattr(profile, field, default)

    scores = {
        'budget':           score_budget(profile_a, profile_b),
        'sleep_schedule':   score_sleep(
                                get(profile_a, 'sleep_schedule', 'flexible'),
                                get(profile_b, 'sleep_schedule', 'flexible')
                            ),
        'smoking':          score_boolean(
                                get(profile_a, 'smoking', False),
                                get(profile_b, 'smoking', False)
                            ),
        'pets':             score_boolean(
                                get(profile_a, 'pets', False),
                                get(profile_b, 'pets', False)
                            ),
        'cleanliness':      score_cleanliness(
                                get(profile_a, 'cleanliness', 3),
                                get(profile_b, 'cleanliness', 3)
                            ),
        'guests_frequency': score_guests(
                                get(profile_a, 'guests_frequency', 'rarely'),
                                get(profile_b, 'guests_frequency', 'rarely')
                            ),
        'work_schedule':    score_work(
                                get(profile_a, 'work_schedule', 'day_shift'),
                                get(profile_b, 'work_schedule', 'day_shift')
                            ),
        'diet':             score_diet(
                                get(profile_a, 'diet', 'any'),
                                get(profile_b, 'diet', 'any')
                            ),
    }

    # Weighted total
    total = sum(scores[dim] * WEIGHTS[dim] for dim in WEIGHTS)
    total = round(min(100.0, max(0.0, total)), 1)

    # Verdict
    if total >= 85:
        verdict = '🌟 Exceptional Match'
    elif total >= 70:
        verdict = '✅ Great Match'
    elif total >= 55:
        verdict = '👍 Good Match'
    elif total >= 40:
        verdict = '🤔 Moderate Match'
    else:
        verdict = '⚠️ Low Compatibility'

    # Highlights (top scoring dimensions)
    highlights = []
    conflicts  = []

    labels = {
        'budget':           'Budget range',
        'sleep_schedule':   'Sleep schedule',
        'smoking':          'Smoking preference',
        'pets':             'Pet preference',
        'cleanliness':      'Cleanliness level',
        'guests_frequency': 'Guest tolerance',
        'work_schedule':    'Work schedule',
        'diet':             'Diet preference',
    }

    for dim, score in sorted(scores.items(), key=lambda x: -x[1]):
        label = labels.get(dim, dim)
        if score >= 80:
            highlights.append(f'{label} compatible')
        elif score <= 30:
            conflicts.append(f'{label} mismatch')

    return {
        'score':      total,
        'verdict':    verdict,
        'highlights': highlights[:3],
        'conflicts':  conflicts[:2],
        'breakdown':  {k: round(v, 0) for k, v in scores.items()},
    }