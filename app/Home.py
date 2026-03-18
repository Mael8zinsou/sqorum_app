import streamlit as st
import pandas as pd

from app import supabase_client
from app.config_runtime import clear_mode, get_default_mode, get_mode, set_mode

APP_TITLE = "Sqorum"

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")


def reset_demo():
    for k in [
        "demo_import_name",
        "demo_ready_data",
        "demo_df_partners",
        "demo_df_opps",
        "demo_scored_partners",
    ]:
        st.session_state.pop(k, None)


def show_mode_selector():
    st.title(f"Bienvenue sur {APP_TITLE}")
    st.markdown("Choisissez le mode à utiliser pour cette session.")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Mode Démo")
        st.write("Test local sans compte, sans base, avec import CSV, scoring, décisions et export.")
        if st.button("Utiliser le mode Démo", type="primary"):
            set_mode("demo")
            st.rerun()

    with c2:
        st.subheader("Mode SaaS")
        st.write("Connexion avec compte, stockage Supabase, espace persistant.")
        if st.button("Utiliser le mode SaaS"):
            set_mode("saas")
            st.rerun()

    st.caption(f"Mode par défaut du déploiement : {get_default_mode()}")


def show_demo_home():
    st.title(f"{APP_TITLE} (Démo)")
    st.info("Mode démo : pas de compte, pas de base. Import CSV → scoring → décisions → export.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📥 Import", type="primary"):
            st.switch_page("pages/5_Imports.py")
    with c2:
        if st.button("🧮 Scoring"):
            st.switch_page("pages/4_Scoring.py")
    with c3:
        if st.button("📁 Partenaires"):
            st.switch_page("pages/2_Partenaires.py")
    with c4:
        if st.button("🧭 Décisions"):
            st.switch_page("pages/3_Decisions_d_activation.py")

    st.divider()

    if "demo_ready_data" in st.session_state:
        st.success(f"Import démo chargé : {len(st.session_state.demo_ready_data)} partenaires.")
    else:
        st.warning("Aucun import en mémoire pour le moment.")

def show_saas_home():
    st.title(f"{APP_TITLE} (SaaS)")
    st.info("Mode SaaS : compte utilisateur, stockage Supabase, espace persistant.")

    user_id = supabase_client.get_user_id()
    user_email = supabase_client.get_user_email()
    partners = supabase_client.get_user_partners(user_id)

    st.write(f"Connecté en tant que **{user_email}**")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📥 Import", type="primary"):
            st.switch_page("pages/5_Imports.py")
    with c2:
        if st.button("🧮 Scoring"):
            st.switch_page("pages/4_Scoring.py")
    with c3:
        if st.button("📁 Partenaires"):
            st.switch_page("pages/2_Partenaires.py")
    with c4:
        if st.button("🧭 Décisions"):
            st.switch_page("pages/3_Decisions_d_activation.py")

    st.divider()

    if not partners:
        st.warning("Votre espace est vide. Commencez par importer vos données.")
        if st.button("Aller à l'import des données"):
            st.switch_page("pages/5_Imports.py")
        return

def show_auth_form():
    st.title(f"Bienvenue sur {APP_TITLE} 👋")
    st.write("Connectez-vous pour accéder à votre espace partenaire.")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        with st.form("login"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Mot de passe", type="password", key="login_pass")
            if st.form_submit_button("Se connecter", type="primary"):
                if supabase_client.sign_in(email, password):
                    st.success("Connexion réussie")
                    st.rerun()

    with tab2:
        with st.form("signup"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Mot de passe", type="password", key="signup_pass")
            if st.form_submit_button("S'inscrire"):
                supabase_client.sign_up(email, password)


def show_welcome_screen():
    st.header("Démarrez avec Sqorum")
    st.info("Votre espace est vide. Commencez par importer vos données.")
    if st.button("Aller à l'Import", type="primary"):
        st.switch_page("pages/5_Imports.py")


# --- Sélection initiale du mode ---
if "mode" not in st.session_state:
    show_mode_selector()
    st.stop()

mode = get_mode()

# --- ROUTING ---
if mode == "demo":
    show_demo_home()

elif mode == "saas":
    if not supabase_client.is_supabase_configured():
        st.error("Le mode SaaS a été choisi, mais Supabase n'est pas configuré sur ce déploiement.")
        if st.button("Revenir au choix du mode"):
            clear_mode()
            st.rerun()
        st.stop()

    if not supabase_client.get_auth_status():
        show_auth_form()
    else:
        show_saas_home()

with st.sidebar:
    st.caption(f"Mode courant : {mode}")

    if st.button("Changer de mode"):
        clear_mode()
        st.rerun()

    if mode == "demo":
        if st.button("⚙️ Paramètres"):
            st.switch_page("pages/6_Parametres.py")
        if st.button("🧹 Reset démo"):
            reset_demo()
            st.success("Démo réinitialisée.")
            st.rerun()

    if mode == "saas" and supabase_client.get_auth_status():
        st.write(f"👤 {supabase_client.get_user_email()}")
        if st.button("⚙️ Paramètres"):
            st.switch_page("pages/6_Parametres.py")
        if st.button("Déconnexion"):
            supabase_client.sign_out()