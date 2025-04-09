import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from st_components.imports_and_utils import ask_gpt
import streamlit as st
from core.config_utils import update_key, load_key
from translations.translations import translate as t
from translations.translations import DISPLAY_LANGUAGES

def config_input(label, key, help=None):
    """Generic config input handler"""
    val = st.text_input(label, value=load_key(key), help=help)
    if val != load_key(key):
        update_key(key, val)
    return val

def page_setting():

    display_language = st.selectbox("Display Language 🌐", 
                                  options=list(DISPLAY_LANGUAGES.keys()),
                                  index=list(DISPLAY_LANGUAGES.values()).index(load_key("display_language")))
    if DISPLAY_LANGUAGES[display_language] != load_key("display_language"):
        update_key("display_language", DISPLAY_LANGUAGES[display_language])
        st.rerun()

    # with st.expander(t("Youtube Settings"), expanded=True):
    #     config_input(t("Cookies Path"), "youtube.cookies_path")

    with st.expander(t("LLM Configuration"), expanded=True):
        config_input(t("API_KEY"), "api.key")
        config_input(t("BASE_URL"), "api.base_url", help=t("Openai format, will add /v1/chat/completions automatically"))
        
        c1, c2 = st.columns([4, 1])
        with c1:
            config_input(t("MODEL"), "api.model", help=t("click to check API validity")+ " 👉")
        with c2:
            if st.button("📡", key="api"):
                st.toast(t("API Key is valid") if check_api() else t("API Key is invalid"), 
                        icon="✅" if check_api() else "❌")
    
    with st.expander(t("Subtitles Settings"), expanded=True):
        # Source language setting
        source_language = st.text_input(
            t("Source Lang"), 
            value=load_key("source_language"),
            help=t("Input the source language of the subtitles")
        )
        if source_language != load_key("source_language"):
            update_key("source_language", source_language)
            st.rerun()

        # Show detected language if source language is auto
        if load_key("source_language") == "auto" and load_key("detected_language"):
            st.info(f"{t('Detected language')}: {load_key('detected_language')}")
            
        # Target language setting
        target_language = st.text_input(
            t("Target Lang"),
            value=load_key("target_language"),
            help=t("Input any language in natural language, as long as llm can understand")
        )
        if target_language != load_key("target_language"):
            update_key("target_language", target_language)
            st.rerun()

        burn_subtitles = st.toggle(t("Burn-in Subtitles"), value=load_key("burn_subtitles"), help=t("Whether to burn subtitles into the video, will increase processing time"))
        if burn_subtitles != load_key("burn_subtitles"):
            update_key("burn_subtitles", burn_subtitles)
            st.rerun()
        
def check_api():
    try:
        resp = ask_gpt("This is a test, response 'message':'success' in json format.", 
                      response_json=True, log_title='None')
        return resp.get('message') == 'success'
    except Exception:
        return False
