# app/pages/3_Decisions_d_activation.py

import os
import sys

import pandas as pd
import streamlit as st

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import supabase_client
from app.config_runtime import get_mode

st.set_page_config(page_title="Décisions", layout="wide")

mode = get_mode()

st.title("Plan d'Activation")
st.markdown("Transformez vos scores en actions concrètes.")

# --- DATA SOURCE ---
if mode == "demo":
    data = st.session_state.get("demo_scored_partners") or st.session_state.get("demo_ready_data") or []
    if not data:
        st.info("Mode démo : aucune donnée. Commence par importer, puis scorer.")
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

# --- Vérification du scoring ---
if "tier" not in df.columns or df["tier"].isnull().all():
    st.warning("Les segments (tiers) ne sont pas définis. Lance le Scoring d'abord.")
    if st.button("Aller au Scoring", type="primary"):
        st.switch_page("pages/4_Scoring.py")
    st.stop()

# --- Segmentation (standard Squorum) ---
prio = df[df["tier"] == "Prioritaire"]
solide = df[df["tier"] == "Solide"]
moyen = df[df["tier"] == "Moyen"]
faible = df[df["tier"] == "Faible"]

# --- Vue d'ensemble ---
st.subheader("Répartition du Portefeuille")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Prioritaire (Accélérer)", len(prio))
    st.caption("Co-sell, MDF, PAM, QBR")

with col2:
    st.metric("Solide (Consolider)", len(solide))
    st.caption("Rythme régulier, playbooks")

with col3:
    st.metric("Moyen (Réactiver)", len(moyen))
    st.caption("Enablement, incentives, relances")

with col4:
    st.metric("Faible (Programmatic)", len(faible))
    st.caption("Automatisation, rationalisation")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Prioritaire", "Solide", "Moyen", "Faible"])

with tab1:
    st.success(f"Stratégie : Co-sell & Marketing ({len(prio)} partenaires)")
    st.markdown("""
    **Actions recommandées :**
    * - PAM dédié / points réguliers
    * - MDF prioritaires
    * - QBR trimestrielle
    """)
    if not prio.empty:
        cols = [c for c in ["partner_name", "score_total", "amount_won", "win_rate"] if c in prio.columns]
        st.dataframe(prio[cols].sort_values("score_total", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun partenaire Prioritaire.")

with tab2:
    st.info(f"Stratégie : Consolider & Industrialiser ({len(solide)} partenaires)")
    st.markdown("""
    **Actions recommandées :**
    * - Playbook commun (ICP, pitch, offres)
    * - Co-marketing léger mais régulier
    * - Revue pipeline mensuelle
    """)
    if not solide.empty:
        cols = [c for c in ["partner_name", "score_total", "pipe_total", "win_rate"] if c in solide.columns]
        st.dataframe(solide[cols].sort_values("score_total", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun partenaire Solide.")

with tab3:
    st.warning(f"Stratégie : Réactiver & Former ({len(moyen)} partenaires)")
    st.markdown("""
    **Actions recommandées :**
    * - Webinars / certifications
    * - Incentives sur 1er deal
    * - Séquences de relance
    """)
    if not moyen.empty:
        cols = [c for c in ["partner_name", "score_total", "pipe_total", "expertise_level"] if c in moyen.columns]
        st.dataframe(moyen[cols].sort_values("score_total", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun partenaire Moyen.")

with tab4:
    st.error(f"Stratégie : Programmatic / Rationaliser ({len(faible)} partenaires)")
    st.markdown("""
    **Actions recommandées :**
    * - Self-service + newsletter automatisée
    * - Nurturing léger
    * - Review désactivation si inactif
    """)
    if not faible.empty:
        cols = [c for c in ["partner_name", "score_total", "opps_brought", "last_activity_date"] if c in faible.columns]
        st.dataframe(faible[cols].sort_values("score_total", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun partenaire Faible.")

# --- Export ---
st.divider()
st.subheader("📥 Exporter le plan d'action")

export_cols = [c for c in ["partner_name", "tier", "score_total"] if c in df.columns]
csv = df[export_cols].to_csv(index=False).encode("utf-8")

st.download_button(
    label="Télécharger la liste segmentée (CSV)",
    data=csv,
    file_name="plan_activation_sqorum.csv",
    mime="text/csv",
)