import streamlit as st
import os
import sys
from st_components.imports_and_utils import *
from core.config_utils import load_key
from st_components.subtitle_upload_section import subtitle_upload_section, get_subtitle_file

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="VideoLingo", page_icon="docs/logo.svg")


def text_processing_section():
    st.header(t("b. Translate and Generate Subtitles"))
    with st.container(border=True):
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("Sentence segmentation using NLP and LLM")}<br>
            2. {t("Summarization and multi-step translation")}<br>
            3. {t("Cutting and aligning long subtitles")}<br>
            4. {t("Generating timeline and subtitles")}
        """, unsafe_allow_html=True)

        subtitle_filename = get_subtitle_file()
        if subtitle_filename:
            subtitle_file = os.path.join("output", "subtitles", subtitle_filename)
            if os.path.exists(subtitle_file):
                st.success(f"📝 {t('Current subtitle file')}: {subtitle_filename}")
                
                # 添加处理按钮
                if st.button(t("Start Processing Subtitles"), key="start_processing_button"):
                    with st.spinner(t("Processing subtitles...")):
                        process_text(subtitle_file)
                    download_subtitle_zip_button(text=t("Download Translated Subtitles"))
                
                if st.button(t("Archive to 'history'"), key="cleanup_in_text_processing"):
                    cleanup()
                    st.rerun()
                return True
        return False

def process_text(subtitle_path: str):
    """处理字幕文件
    
    Args:
        subtitle_path (str): 字幕文件路径
    """
    with st.spinner(t("Processing subtitle file...")):
        from core.text_processor import TextProcessor
        processor = TextProcessor()
        processor.process_subtitle_file(subtitle_path)
    
    st.success(t("Subtitle processing complete! 🎉"))
    st.balloons()

def main():
    logo_col, _ = st.columns([1,1])
    with logo_col:
        st.image("docs/logo.png", use_column_width=True)
    st.markdown(button_style, unsafe_allow_html=True)
    welcome_text = t("Hello, welcome to VideoLingo. If you encounter any issues, feel free to get instant answers with our Free QA Agent <a href=\"https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh\" target=\"_blank\">here</a>! You can also try out our SaaS website at <a href=\"https://videolingo.io\" target=\"_blank\">videolingo.io</a> for free!")
    st.markdown(f"<p style='font-size: 20px; color: #808080;'>{welcome_text}</p>", unsafe_allow_html=True)
    # add settings
    with st.sidebar:
        page_setting()
        st.markdown(give_star_button, unsafe_allow_html=True)
    subtitle_upload_section()
    text_processing_section()

if __name__ == "__main__":
    main()
