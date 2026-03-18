from typing import Any


def explain_score(row: dict[str, Any], weights: dict[str, float]) -> list[str]:
    reasons: list[str] = []

    win_rate = float(row.get("win_rate", 0))
    pipe_total = float(row.get("pipe_total", 0))
    expertise = str(row.get("expertise_level", ""))

    if win_rate >= 50:
        reasons.append("Win rate solide")
    elif win_rate <= 15:
        reasons.append("Win rate faible")

    if pipe_total >= 50000:
        reasons.append("Pipeline élevé")
    elif pipe_total <= 5000:
        reasons.append("Pipeline limité")

    if expertise in {"4", "5"}:
        reasons.append("Expertise partenaire forte")
    elif expertise in {"1", "2"}:
        reasons.append("Expertise partenaire à développer")

    main_weight = max(weights, key=weights.get)
    reasons.append(f"Dimension dominante: {main_weight}")

    return reasons
