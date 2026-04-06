# app/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SupabaseNotConfigured(RuntimeError):
    pass


def _safe_secret_get(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _safe_secret_section(section: str):
    try:
        return st.secrets.get(section, {})
    except Exception:
        return {}


# def _get_supabase_credentials() -> tuple[str | None, str | None]:
#     """
#     Ordre de priorité :
#     1. Variables d'environnement (Render / Docker / local)
#     2. st.secrets[supabase]
#     3. st.secrets racine
#     """
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")

#     if not url or not key:
#         supabase_section = _safe_secret_section("supabase")
#         if isinstance(supabase_section, dict):
#             url = url or supabase_section.get("SUPABASE_URL")
#             key = key or supabase_section.get("SUPABASE_KEY")

#     if not url or not key:
#         url = url or _safe_secret_get("SUPABASE_URL")
#         key = key or _safe_secret_get("SUPABASE_KEY")

#     url = url.strip() if isinstance(url, str) else url
#     key = key.strip() if isinstance(key, str) else key

#     # DEBUG TEMPORAIRE
#     st.write(f"DEBUG - Source Env: {'Présente' if os.getenv('SUPABASE_URL') else 'Absente'}")
    #     st.write(f"DEBUG - Source Secrets: {'Présente' if _safe_secret_get('SUPABASE_URL') else 'Absente'}")
#     return url, key

def _get_supabase_credentials() -> tuple[str | None, str | None]:
    """
    Ordre de priorité :
    1. Variables d'environnement (Render / Docker / local via .env)
    2. st.secrets[supabase]
    3. st.secrets racine
    """
    # 1. Variables d'environnement (Priorité pour Docker/Render)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    # 2. Section [supabase] dans secrets.toml (Pour le dev local)
    if not url or not key:
        supabase_section = _safe_secret_section("supabase")
        # CORRECTION : On vérifie juste que la section existe, sans forcer le type 'dict'
        if supabase_section: 
            url = url or supabase_section.get("SUPABASE_URL")
            key = key or supabase_section.get("SUPABASE_KEY")

    # 3. Racine du secrets.toml (Au cas où)
    if not url or not key:
        url = url or _safe_secret_get("SUPABASE_URL")
        key = key or _safe_secret_get("SUPABASE_KEY")

    # Nettoyage
    url = url.strip() if isinstance(url, str) else url
    key = key.strip() if isinstance(key, str) else key

    return url, key

def is_supabase_configured() -> bool:
    url, key = _get_supabase_credentials()
    return bool(url) and bool(key) and str(url).startswith("http")


@st.cache_resource
def init_supabase_client() -> Client:
    url, key = _get_supabase_credentials()

    if not url or not key:
        raise SupabaseNotConfigured("SUPABASE_URL / SUPABASE_KEY manquantes.")
    if not str(url).startswith("http"):
        raise SupabaseNotConfigured(f"URL Supabase invalide : {url}")

    return create_client(url, key)


def get_authenticated_client() -> Client:
    supabase = init_supabase_client()

    if "session" in st.session_state and st.session_state.session is not None:
        try:
            supabase.postgrest.auth(st.session_state.session.access_token)
        except Exception:
            pass

    return supabase


# --- AUTH ---

def sign_up(email, password):
    try:
        supabase = init_supabase_client()
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Compte créé ! Vérifiez vos emails.")
            return True
    except SupabaseNotConfigured as e:
        st.warning(f"Mode démo : Supabase non configuré ({e})")
    except Exception as e:
        st.error(f"Erreur inscription : {e}")
    return False


def sign_in(email, password):
    try:
        supabase = init_supabase_client()
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user and response.session:
            st.session_state.user = response.user
            st.session_state.session = response.session
            return True
    except SupabaseNotConfigured as e:
        st.warning(f"Mode démo : Supabase non configuré ({e})")
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
    return False


def sign_out():
    try:
        supabase = init_supabase_client()
        supabase.auth.sign_out()
    except SupabaseNotConfigured:
        pass

    st.session_state.user = None
    st.session_state.session = None
    st.rerun()


def get_auth_status():
    return "user" in st.session_state and st.session_state.user is not None


def get_user_id():
    return st.session_state.user.id if get_auth_status() else None


def get_user_email():
    return st.session_state.user.email if get_auth_status() else ""


# --- DATA ---

def bulk_insert_partners(user_id: str, filename: str, data: list) -> bool:
    try:
        supabase = get_authenticated_client()

        import_payload = {
            "user_id": user_id,
            "filename": filename,
            "row_count": len(data),
        }
        import_response = supabase.table("imports").insert(import_payload).execute()

        if not import_response.data:
            st.error("Erreur : l'import n'a pas renvoyé de données.")
            return False

        new_import_id = import_response.data[0]["id"]

        for row in data:
            row["import_id"] = new_import_id
            row["user_id"] = user_id

        supabase.table("partners").insert(data).execute()
        return True

    except SupabaseNotConfigured as e:
        st.warning(f"Mode démo : insertion DB indisponible ({e})")
        return False
    except Exception as e:
        st.error(f"Erreur lors de l'insertion en base : {e}")
        return False


def get_user_partners(user_id: str) -> list:
    try:
        supabase = get_authenticated_client()
        response = supabase.table("partners").select("*").eq("user_id", user_id).execute()
        return response.data
    except SupabaseNotConfigured:
        return []
    except Exception as e:
        st.error(f"Erreur récupération : {e}")
        return []


def delete_all_user_data(user_id: str) -> bool:
    try:
        supabase = get_authenticated_client()
        supabase.table("partners").delete().eq("user_id", user_id).execute()
        supabase.table("imports").delete().eq("user_id", user_id).execute()
        st.cache_resource.clear()
        return True
    except SupabaseNotConfigured:
        st.warning("Mode démo : rien à supprimer en base.")
        return True
    except Exception as e:
        st.error(f"Erreur suppression : {e}")
        return False