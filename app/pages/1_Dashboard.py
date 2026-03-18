# app/pages/1_Dashboard.py

import os
import sys

import pandas as pd
import streamlit as st

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import supabase_client
from app.config_runtime import get_mode

st.set_page_config(page_title="Dashboard", layout="wide")

mode = get_mode()

st.title("Tableau de Bord Sqorum")
st.markdown("Vue d'ensemble de votre écosystème partenaires.")

# --- DATA SOURCE ---
if mode == "demo":
    data = st.session_state.get("demo_scored_partners") or st.session_state.get("demo_ready_data") or []
    if not data:
        st.info("Mode démo : aucune donnée trouvée. Commence par importer tes fichiers.")
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
        st.info("Aucune donnée trouvée. Commencez par importer vos fichiers.")
        if st.button("Aller à l'import", type="primary"):
            st.switch_page("pages/5_Imports.py")
        st.stop()

df = pd.DataFrame(data)

# --- KPIs ---
st.divider()
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_partners = len(df)

# Colonnes pouvant ne pas exister en démo selon ton pipeline
total_pipe = df["pipe_total"].sum() if "pipe_total" in df.columns else 0
avg_win_rate = df["win_rate"].mean() if "win_rate" in df.columns else 0
total_won = df["amount_won"].sum() if "amount_won" in df.columns else 0

with kpi1:
    st.metric("Total Partenaires", total_partners)
with kpi2:
    st.metric("Pipeline Total", f"{total_pipe:,.0f} €")
with kpi3:
    st.metric("Win Rate Moyen", f"{avg_win_rate:.1f} %")
with kpi4:
    st.metric("CA Signé (Won)", f"{total_won:,.0f} €")

st.divider()

# --- Graphiques ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Répartition par Type")
    if "partner_type" in df.columns:
        st.bar_chart(df["partner_type"].value_counts())
    else:
        st.write("Pas de données de type.")

with col_right:
    st.subheader("Performance : Win Rate vs Pipeline")
    if not df.empty and "pipe_total" in df.columns and "win_rate" in df.columns:
        st.scatter_chart(
            df,
            x="pipe_total",
            y="win_rate",
            color="partner_type" if "partner_type" in df.columns else None,
            size="amount_won" if "amount_won" in df.columns else None,
        )
    else:
        st.write("Données insuffisantes pour le graphique.")

# --- Tableau détaillé ---
st.subheader("Détail des Partenaires")
cols_to_hide = [
    "id",
    "user_id",
    "import_id",
    "created_at",
    "score_profil",
    "score_relation",
    "status",
]
display_df = df.drop(columns=[c for c in cols_to_hide if c in df.columns])

st.dataframe(display_df, use_container_width=True)

with st.sidebar:
    st.caption(f"Mode: {mode}")