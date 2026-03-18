# app/pages/6_Parametres.py

import time
import streamlit as st

from app import supabase_client
from app.config_runtime import get_mode

st.set_page_config(page_title="Paramètres", layout="centered")

mode = get_mode()

st.title("Paramètres")
st.caption(f"Mode actif : **{mode}**")

st.divider()

# -----------------------
# MODE DEMO (local only)
# -----------------------
if mode == "demo":
    st.info("Mode démo : les données sont stockées localement (session Streamlit).")

    st.subheader("Zone de Danger (Démo)")
    st.markdown("Réinitialise la session de démo (imports + scoring).")

    with st.expander("🧹 Réinitialiser la démo", expanded=False):
        confirm = st.checkbox("Je confirme vouloir réinitialiser la démo.")
        if st.button("🔴 RÉINITIALISER", type="primary", disabled=not confirm):
            for k in [
                "demo_import_name",
                "demo_ready_data",
                "demo_df_partners",
                "demo_df_opps",
                "demo_scored_partners",
            ]:
                st.session_state.pop(k, None)

            st.success("Démo réinitialisée.")
            time.sleep(1)
            st.switch_page("Home.py")

    st.divider()
    st.write("Aucune déconnexion nécessaire en mode démo.")
    st.stop()

# -----------------------
# MODE SAAS (Supabase)
# -----------------------
if not supabase_client.get_auth_status():
    st.warning("Veuillez vous connecter.")
    st.stop()

st.write(f"Compte connecté : **{supabase_client.get_user_email()}**")

st.subheader("Zone de Danger")
st.markdown("""
Cette section vous permet de réinitialiser votre compte.  
**Attention : cette action est irréversible.**
""")

with st.expander("🗑️ Supprimer toutes mes données", expanded=False):
    st.warning("Cette action effacera tous vos imports, partenaires, scores et décisions.")
    confirm = st.checkbox("Je confirme vouloir tout effacer définitivement.")

    if st.button("🔴 TOUT SUPPRIMER", type="primary", disabled=not confirm):
        user_id = supabase_client.get_user_id()

        with st.spinner("Nettoyage de la base de données..."):
            success = supabase_client.delete_all_user_data(user_id)

        if success:
            st.success("Toutes vos données ont été effacées.")
            time.sleep(1)
            st.switch_page("Home.py")
        else:
            st.error("Une erreur est survenue lors de la suppression.")

st.divider()

if st.button("Se déconnecter"):
    supabase_client.sign_out()