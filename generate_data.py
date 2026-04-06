import random
from pathlib import Path

import pandas as pd

NB_PARTENAIRES = 50
MIN_OPPS = 3
MAX_OPPS = 15
MIN_MONTANT = 4000
MAX_MONTANT = 50000

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

company_names = [
    "Accenture", "Capgemini", "Atos", "Sopra Steria", "IBM",
    "Deloitte", "PwC", "KPMG", "EY", "Bain & Company",
    "McKinsey", "BCG", "Salesforce", "Microsoft", "Google Cloud",
    "AWS Partner", "Oracle", "SAP", "Cisco Systems", "Dell Technologies",
    "HP Enterprise", "Lenovo", "Sony Professional", "Samsung B2B", "LG Business",
    "Panasonic", "Toshiba", "Hitachi Vantara", "Siemens", "General Electric",
    "Schneider Electric", "Legrand", "Orange Business", "SFR Business", "Bouygues Telecom",
    "Free Pro", "TotalEnergies", "Engie Solutions", "EDF Entreprises", "Veolia",
    "Suez", "Vinci Energies", "Eiffage", "Spie", "Saint-Gobain",
    "Thales", "Dassault Systèmes", "Airbus", "Safran", "Renault Group",
]

stages_list = ["F", "E", "D", "C", "B", "A", "Win", "Lost"]

partners_data = {
    "partner_name": company_names,
    "expertise_level": [random.randint(1, 5) for _ in range(len(company_names))],
    "sector": [random.choice(["IT", "Consulting", "Industrie", "Energie", "Telco"]) for _ in range(len(company_names))],
    "partner_type": [random.choice(["SI", "VAR", "ISV", "Distributeur"]) for _ in range(len(company_names))],
}

df_partners = pd.DataFrame(partners_data)
partners_path = OUTPUT_DIR / "dataset_50_partenaires.csv"
df_partners.to_csv(partners_path, index=False)
print(f"Generated {partners_path} with {len(df_partners)} rows")

opps_data = []
for partner in company_names:
    nb_opps = random.randint(MIN_OPPS, MAX_OPPS)
    for _ in range(nb_opps):
        opps_data.append(
            {
                "partner_name": partner,
                "opp_stage": random.choice(stages_list),
                "amount": random.randint(MIN_MONTANT, MAX_MONTANT),
            }
        )

df_opps = pd.DataFrame(opps_data)
opps_path = OUTPUT_DIR / "dataset_500_opportunites.csv"
df_opps.to_csv(opps_path, index=False)
print(f"Generated {opps_path} with {len(df_opps)} rows")
