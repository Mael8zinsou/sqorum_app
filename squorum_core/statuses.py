from collections.abc import Iterable

DEFAULT_TIERS: list[tuple[float, str]] = [
    (80, "Prioritaire"),
    (60, "Solide"),
    (40, "Moyen"),
    (0, "Faible"),
]


def score_to_tier(score_total: float, thresholds: Iterable[tuple[float, str]] | None = None) -> str:
    rules = list(thresholds or DEFAULT_TIERS)
    for minimum, label in sorted(rules, key=lambda x: x[0], reverse=True):
        if score_total >= minimum:
            return label
    return "Faible"