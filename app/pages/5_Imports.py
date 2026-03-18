import os
import sys
import time

import pandas as pd
import streamlit as st

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import supabase_client
from app.config_runtime import get_mode
from squorum_core.io import read_uploaded_file
from squorum_core.scoring import process_and_aggregate

st.set_page_config(page_title="Imports", layout="wide")

mode = get_mode()

st.title("Importer vos Données")

# --- SaaS guard (demo: no auth required) ---
if mode == "saas" and not supabase_client.get_auth_status():
    st.warning("Veuillez vous connecter.")
    st.stop()

c1, c2 = st.columns(2)
file_p = c1.file_uploader("Fichier Partenaires (CSV/Excel)", type=["csv", "xlsx"])
file_o = c2.file_uploader("Fichier Opportunités (CSV/Excel)", type=["csv", "xlsx"])

if file_p and file_o:
    st.divider()
    df_p = read_uploaded_file(file_p)
    df_o = read_uploaded_file(file_o)

    if df_p is not None and df_o is not None:
        st.subheader("Configuration du Mapping")
        st.info("Associez les colonnes de vos fichiers aux champs de Sqorum.")

        col1, col2 = st.columns(2)

        def get_idx(cols, key):
            return next((i for i, c in enumerate(cols) if key.lower() in c.lower()), 0)

        with col1:
            st.markdown("### 1. Colonnes Partenaires")
            p_name = st.selectbox("Nom de l'entreprise *", df_p.columns, index=get_idx(df_p.columns, "partner"))
            p_type = st.selectbox("Type (SI, Reseller...) *", df_p.columns, index=get_idx(df_p.columns, "type"))
            p_sector = st.selectbox("Secteur", df_p.columns, index=get_idx(df_p.columns, "sector"))
            p_expertise = st.selectbox("Niveau d'expertise", df_p.columns, index=get_idx(df_p.columns, "expert"))

        with col2:
            st.markdown("### 2. Colonnes Opportunités")
            o_partner = st.selectbox("Nom du Partenaire (Clé de jointure) *", df_o.columns, index=get_idx(df_o.columns, "partner"))
            o_amount = st.selectbox("Montant de l'opportunité *", df_o.columns, index=get_idx(df_o.columns, "amount"))
            o_stage = st.selectbox("Étape de vente (Stage) *", df_o.columns, index=get_idx(df_o.columns, "stage"))

        st.divider()

        if st.button("Lancer l'Import Flexible", type="primary"):
            mapping_config = {
                "p_name": p_name,
                "p_type": p_type,
                "p_sector": p_sector,
                "p_expertise": p_expertise,
                "o_partner": o_partner,
                "o_amount": o_amount,
                "o_stage": o_stage,
            }

            with st.spinner("Traitement en cours..."):
                # user_id: SaaS needs it, demo can use a fixed placeholder
                user_id = supabase_client.get_user_id() if mode == "saas" else "demo_user"

                ready_data = process_and_aggregate(df_p, df_o, user_id, mapping_config)

                if not ready_data:
                    st.error("Erreur lors de l'agrégation. Vérifiez vos fichiers.")
                    st.stop()

                # --- DEMO path: store locally ---
                if mode == "demo":
                    st.session_state.demo_import_name = f"Import {pd.Timestamp.now().strftime('%d/%m %H:%M')}"
                    st.session_state.demo_ready_data = ready_data
                    st.session_state.demo_df_partners = df_p
                    st.session_state.demo_df_opps = df_o
                    st.success(f"Import démo OK : {len(ready_data)} partenaires prêts.")
                    st.balloons()
                    time.sleep(1)
                    st.switch_page("pages/4_Scoring.py")

                # --- SAAS path: push to DB ---
                else:
                    name = f"Import {pd.Timestamp.now().strftime('%d/%m %H:%M')}"
                    if supabase_client.bulk_insert_partners(user_id, name, ready_data):
                        st.balloons()
                        st.success(f"Succès: {len(ready_data)} partenaires importés.")
                        time.sleep(1)
                        st.switch_page("pages/1_Dashboard.py")
                    else:
                        st.error("Erreur lors de l'insertion en base.")