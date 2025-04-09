import streamlit as st
import os
import shutil
import re
from time import sleep
from translations.translations import translate as t

OUTPUT_DIR = "output"
SUBTITLE_DIR = os.path.join(OUTPUT_DIR, "subtitles")

def is_valid_subtitle_file(filename):
    """检查是否为支持的字幕文件格式"""
    valid_extensions = ['.srt', '.ass', '.ssa', '.vtt']
    return os.path.splitext(filename)[1].lower() in valid_extensions

def get_subtitle_file():
    """获取已上传的字幕文件"""
    if not os.path.exists(SUBTITLE_DIR):
        return None
    
    files = [f for f in os.listdir(SUBTITLE_DIR) if is_valid_subtitle_file(f)]
    return files[0] if files else None

def subtitle_upload_section():
    st.header(t("a. Upload Subtitle File"))
    with st.container(border=True):
        try:
            subtitle_file = get_subtitle_file()
            if subtitle_file:
                st.success(f"📝 {t('Current subtitle file')}: {subtitle_file}")
                
                # 显示字幕文件内容预览
                with open(os.path.join(SUBTITLE_DIR, subtitle_file), 'r', encoding='utf-8') as f:
                    preview_content = ''.join(f.readlines()[:10])  # 只预览前10行
                with st.expander(t("Preview subtitle content")):
                    st.code(preview_content, language='text')
                
                if st.button(t("Delete and Reupload"), key="delete_subtitle_button"):
                    if os.path.exists(SUBTITLE_DIR):
                        shutil.rmtree(SUBTITLE_DIR)
                    sleep(1)
                    st.rerun()
                return True
            
        except Exception as e:
            st.error(f"Error loading subtitle file: {str(e)}")
            if os.path.exists(SUBTITLE_DIR):
                shutil.rmtree(SUBTITLE_DIR)
            return False
            
        # 上传新字幕文件
        uploaded_file = st.file_uploader(
            t("Upload a subtitle file"), 
            type=['srt', 'ass', 'ssa', 'vtt'],
            help=t("Supported formats: SRT, ASS, SSA, VTT")
        )

        if uploaded_file:
            if not os.path.exists(SUBTITLE_DIR):
                os.makedirs(SUBTITLE_DIR, exist_ok=True)
            
            # 清理文件名
            raw_name = uploaded_file.name.replace(' ', '_')
            name, ext = os.path.splitext(raw_name)
            clean_name = re.sub(r'[^\w\-_\.]', '', name) + ext.lower()
            
            # 保存文件
            save_path = os.path.join(SUBTITLE_DIR, clean_name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(t("Subtitle file uploaded successfully!"))
            st.rerun()
        else:
            st.info(t("Please upload a subtitle file to begin."))
            return False
