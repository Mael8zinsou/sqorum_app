from dataclasses import dataclass


@dataclass
class PartnerRecord:
    user_id: str
    import_id: str
    partner_name: str
    expertise_level: str = ""
    sector: str = ""
    partner_type: str = ""
    opps_brought: int = 0
    opps_won: int = 0
    amount_won: float = 0.0
    pipe_total: float = 0.0
    win_rate: float = 0.0
    closed_vs_pipe: float = 0.0
