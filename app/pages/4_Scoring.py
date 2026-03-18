import os
import sys
import time

import streamlit as st

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import supabase_client
from app.config_runtime import get_mode
from squorum_core.scoring import DEFAULT_FAMILY_WEIGHTS, calculate_score

st.set_page_config(page_title="Scoring", layout="wide")

mode = get_mode()

# --- SaaS guard (demo: no auth required) ---
if mode == "saas" and not supabase_client.get_auth_status():
    st.warning("Veuillez vous connecter.")
    st.stop()

st.title("Configuration du Scoring")
st.markdown("Définissez l'importance de chaque dimension pour classer vos partenaires.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Qualité")
    w_qual = st.slider("Poids Qualité", 0, 100, int(DEFAULT_FAMILY_WEIGHTS["quality"] * 100)) / 100

with col2:
    st.subheader("Performance")
    w_perf = st.slider("Poids Performance", 0, 100, int(DEFAULT_FAMILY_WEIGHTS["performance"] * 100)) / 100

with col3:
    st.subheader("Potentiel")
    w_pot = st.slider("Poids Potentiel", 0, 100, int(DEFAULT_FAMILY_WEIGHTS["potential"] * 100)) / 100

total_weight = w_qual + w_perf + w_pot
if round(total_weight, 6) != 1.0:
    st.warning(f"Le total des poids est de {int(total_weight * 100)}%. (Pense à 100%)")

st.divider()

if mode == "demo":
    if "demo_ready_data" not in st.session_state:
        st.info("Mode démo : commence par importer des fichiers dans l'onglet Imports.")
        if st.button("Aller à l'Import", type="primary"):
            st.switch_page("pages/5_Imports.py")
        st.stop()

if st.button("Lancer le calcul des Scores", type="primary"):
    weights = {"quality": w_qual, "performance": w_perf, "potential": w_pot}

    with st.spinner("Calcul des scores en cours..."):
        # --- DEMO path ---
        if mode == "demo":
            # ready_data = st.session_state.demo_ready_data
            # updates = [calculate_score(p, weights) for p in ready_data if p.get("partner_name")]

            # st.session_state.demo_scored_partners = updates
            # st.success("Scoring démo terminé")
            # st.balloons()
            # time.sleep(1)
            # st.switch_page("pages/2_Partenaires.py")
            
            # Patch de correction
            ready_data = st.session_state.demo_ready_data
            
            scored_full = []
            for p in ready_data:
                if not p.get("partner_name"):
                    continue
                scored = calculate_score(p, weights)   # dict avec score_total, tier, etc.
                merged = dict(p)                       # conserve pipe_total, win_rate, amount_won, etc.
                merged.update(scored)                  # ajoute/écrase avec les scores
                scored_full.append(merged)

            st.session_state.demo_scored_partners = scored_full
            st.success("Scoring démo terminé")
            st.balloons()
            time.sleep(1)
            st.switch_page("pages/2_Partenaires.py")

        # --- SAAS path ---
        else:
            user_id = supabase_client.get_user_id()
            partners = supabase_client.get_user_partners(user_id)

            updates = []
            for partner in partners:
                if partner.get("partner_name"):
                    updates.append(calculate_score(partner, weights))

            if updates:
                try:
                    supabase = supabase_client.init_supabase_client()
                    supabase.table("partners").upsert(updates).execute()
                    st.success("Scoring terminé avec succès")
                    st.balloons()
                    time.sleep(1)
                    st.switch_page("pages/2_Partenaires.py")
                except Exception as exc:
                    st.error(f"Erreur critique lors du Scoring : {exc}")
            else:
                st.error("Aucun partenaire à scorer.")