# app/pages/2_Partenaires.py

import os
import sys

import pandas as pd
import streamlit as st

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import supabase_client
from app.config_runtime import get_mode

st.set_page_config(page_title="Partenaires", layout="wide")

mode = get_mode()

st.title("📁 Classement Partenaires")

# --- DATA SOURCE ---
if mode == "demo":
    # En démo, on lit la session
    data = st.session_state.get("demo_scored_partners") or st.session_state.get("demo_ready_data") or []
    if not data:
        st.info("Mode démo : aucune donnée. Commence par importer tes fichiers.")
        if st.button("Aller à l'import", type="primary"):
            st.switch_page("pages/5_Imports.py")
        st.stop()
else:
    if not supabase_client.get_auth_status():
        st.warning("Veuillez vous connecter.")
        st.stop()

    user_id = supabase_client.get_user_id()
    data = supabase_client.get_user_partners(user_id)

    if not data:
        st.info("Aucune donnée.")
        st.stop()

df = pd.DataFrame(data)


# Vérifier si le scoring a été fait
if "score_total" not in df.columns or df["score_total"].fillna(0).sum() == 0:
    st.warning("Les scores n'ont pas encore été calculés.")
    if st.button("Aller au Scoring", type="primary"):
        st.switch_page("pages/4_Scoring.py")
    st.stop()

# # Debug
# st.write("DEBUG tiers:", df["tier"].dropna().unique().tolist())
# st.write("DEBUG columns:", df.columns.tolist())

# --- Filtres & Tri ---
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    search = st.text_input("Rechercher un partenaire", "")
with col2:
    min_score = st.slider("Score min.", 0, 100, 0)
with col3:
    tier_filter = st.selectbox("Tier", ["Tous", "Prioritaire", "Solide", "Moyen", "Faible"])

# # Debug
# st.write("DEBUG tiers:", df["tier"].dropna().unique().tolist())
# st.write("DEBUG columns:", df.columns.tolist())

# Filtrage
if "partner_name" in df.columns and search:
    df = df[df["partner_name"].astype(str).str.contains(search, case=False, na=False)]

df = df[df["score_total"] >= min_score]

if tier_filter != "Tous" and "tier" in df.columns:
    df = df[df["tier"] == tier_filter]

# Tri par défaut par score décroissant
df = df.sort_values(by="score_total", ascending=False)

st.divider()

# --- Export ---
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Télécharger le classement (CSV)",
    data=csv,
    file_name="squorum_partenaires_scored.csv",
    mime="text/csv",
)

# --- Affichage Tableau ---
display_cols = [
    "partner_name",
    "tier",
    "score_total",
    "score_quality",
    "score_performance",
    "score_potential",
    "win_rate",
    "amount_won",
]

# Garder uniquement les colonnes présentes
display_cols = [c for c in display_cols if c in df.columns]

st.dataframe(
    df[display_cols],
    column_config={
        "score_total": st.column_config.ProgressColumn("Global", min_value=0, max_value=100, format="%d"),
        "score_quality": st.column_config.ProgressColumn("Qualité", min_value=0, max_value=100, format="%d"),
        "score_performance": st.column_config.ProgressColumn("Perf.", min_value=0, max_value=100, format="%d"),
        "score_potential": st.column_config.ProgressColumn("Potentiel", min_value=0, max_value=100, format="%d"),
        "amount_won": st.column_config.NumberColumn("CA Signé", format="%d €"),
        "win_rate": st.column_config.NumberColumn("Win Rate", format="%.1f %%"),
    },
    use_container_width=True,
    hide_index=True,
)

with st.sidebar:
    st.caption(f"Mode: {mode}")
    if mode == "demo":
        if st.button("🧹 Réinitialiser la démo"):
            for k in ["demo_import_name", "demo_ready_data", "demo_df_partners", "demo_df_opps", "demo_scored_partners"]:
                st.session_state.pop(k, None)
            st.rerun()
    else:
        st.write(f"👤 {supabase_client.get_user_email()}")