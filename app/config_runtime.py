import os
import streamlit as st

VALID_MODES = ("demo", "saas")


def _safe_get_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_default_mode() -> str:
    mode = _safe_get_secret("SQUORUM_MODE")

    if not mode:
        mode = os.getenv("SQUORUM_MODE", "demo")

    mode = str(mode).strip().lower()
    return mode if mode in VALID_MODES else "demo"


def get_mode() -> str:
    session_mode = st.session_state.get("mode")
    if session_mode in VALID_MODES:
        return session_mode
    return get_default_mode()


def set_mode(mode: str) -> None:
    mode = str(mode).strip().lower()
    if mode in VALID_MODES:
        st.session_state["mode"] = mode


def clear_mode() -> None:
    st.session_state.pop("mode", None)