from dataclasses import asdict
from typing import Any

import numpy as np
import pandas as pd

from .schemas import PartnerRecord
from .statuses import DEFAULT_TIERS, score_to_tier

LEVEL_MAPPING_LINEAR: dict[Any, int] = {
    "1": 20,
    "2": 40,
    "3": 60,
    "4": 80,
    "5": 100,
    1: 20,
    2: 40,
    3: 60,
    4: 80,
    5: 100,
}

PARTNER_TYPE_SCORE_MAP: dict[str, int] = {
    "var": 80,
    "si": 70,
    "isv": 90,
    "conseils": 60,
    "default": 50,
}

DEFAULT_FAMILY_WEIGHTS: dict[str, float] = {
    "quality": 0.30,
    "performance": 0.50,
    "potential": 0.20,
}


def _potential_from_pipe(pipe_total: float) -> float:
    if pipe_total > 100000:
        return 100
    if pipe_total > 50000:
        return 80
    if pipe_total > 20000:
        return 60
    if pipe_total > 5000:
        return 40
    return 20


def calculate_score(row: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    exp_val = str(row.get("expertise_level", "1"))
    mapped = LEVEL_MAPPING_LINEAR.get(exp_val)
    if mapped is None and exp_val.isdigit():
        mapped = LEVEL_MAPPING_LINEAR.get(int(exp_val), 20)
    s_expertise = mapped if mapped is not None else 20

    p_type = str(row.get("partner_type", "default")).lower()
    s_type = PARTNER_TYPE_SCORE_MAP.get(p_type, 50)
    score_quality = (s_expertise + s_type) / 2

    win_rate = min(float(row.get("win_rate", 0)), 100)
    closed_vs_pipe = min(float(row.get("closed_vs_pipe", 0)), 100)
    score_performance = (win_rate * 0.6) + (closed_vs_pipe * 0.4)

    pipe_total = float(row.get("pipe_total", 0))
    score_potential = _potential_from_pipe(pipe_total)

    score_total = (
        (score_quality * weights["quality"])
        + (score_performance * weights["performance"])
        + (score_potential * weights["potential"])
    )
    score_total = round(score_total, 1)

    tier = score_to_tier(score_total, DEFAULT_TIERS)

    return {
        "id": row.get("id"),
        "user_id": row.get("user_id"),
        "partner_name": row.get("partner_name"),
        "score_quality": round(score_quality, 1),
        "score_performance": round(score_performance, 1),
        "score_potential": round(score_potential, 1),
        "score_total": score_total,
        "tier": tier,
    }

def score_label(score_total: float) -> str:
    return score_to_tier(score_total, DEFAULT_TIERS)


def process_and_aggregate(
    df_partners: pd.DataFrame,
    df_opps: pd.DataFrame,
    user_id: str,
    mapping: dict[str, str],
) -> list[dict[str, Any]]:
    df_p = df_partners.copy()
    df_o = df_opps.copy()

    rename_p: dict[str, str] = {}
    if "p_name" in mapping:
        rename_p[mapping["p_name"]] = "partner_name"
    if "p_type" in mapping:
        rename_p[mapping["p_type"]] = "partner_type"
    if "p_sector" in mapping:
        rename_p[mapping["p_sector"]] = "sector"
    if "p_expertise" in mapping:
        rename_p[mapping["p_expertise"]] = "expertise_level"
    df_p = df_p.rename(columns=rename_p)

    rename_o: dict[str, str] = {}
    if "o_partner" in mapping:
        rename_o[mapping["o_partner"]] = "partner_name"
    if "o_amount" in mapping:
        rename_o[mapping["o_amount"]] = "amount"
    if "o_stage" in mapping:
        rename_o[mapping["o_stage"]] = "opp_stage"
    df_o = df_o.rename(columns=rename_o)

    if "partner_name" not in df_p.columns or "partner_name" not in df_o.columns:
        return []

    df_p["join_key"] = df_p["partner_name"].astype(str).str.strip().str.lower()
    df_o["join_key"] = df_o["partner_name"].astype(str).str.strip().str.lower()

    df_o["amount"] = pd.to_numeric(df_o.get("amount", 0), errors="coerce").fillna(0)
    df_o["is_won"] = (
        df_o.get("opp_stage", "")
        .astype(str)
        .str.lower()
        .str.contains("won|win|gagné|signé|closed won", regex=True)
    )

    agg_df = (
        df_o.groupby("join_key")
        .agg(
            opps_brought=("join_key", "count"),
            opps_won=("is_won", "sum"),
            pipe_total=("amount", "sum"),
            amount_won=("amount", lambda x: x[df_o.loc[x.index, "is_won"]].sum()),
        )
        .reset_index()
    )

    final_df = pd.merge(df_p, agg_df, on="join_key", how="left")
    cols_zero = ["opps_brought", "opps_won", "pipe_total", "amount_won"]
    final_df[cols_zero] = final_df[cols_zero].fillna(0)

    final_df["win_rate"] = np.divide(
        final_df["opps_won"],
        final_df["opps_brought"],
        out=np.zeros_like(final_df["opps_won"], dtype=float),
        where=final_df["opps_brought"] != 0,
    ) * 100

    final_df["closed_vs_pipe"] = np.divide(
        final_df["amount_won"],
        final_df["pipe_total"],
        out=np.zeros_like(final_df["amount_won"], dtype=float),
        where=final_df["pipe_total"] != 0,
    ) * 100

    valid_records: list[dict[str, Any]] = []
    for _, row in final_df.iterrows():
        record = PartnerRecord(
            user_id=user_id,
            import_id=user_id,
            partner_name=str(row["partner_name"]),
            expertise_level=str(row.get("expertise_level", "")),
            sector=str(row.get("sector", "")),
            partner_type=str(row.get("partner_type", "")),
            opps_brought=int(row["opps_brought"]),
            opps_won=int(row["opps_won"]),
            amount_won=float(row["amount_won"]),
            pipe_total=float(row["pipe_total"]),
            win_rate=float(row["win_rate"]),
            closed_vs_pipe=float(row["closed_vs_pipe"]),
        )
        valid_records.append(asdict(record))

    return valid_records
