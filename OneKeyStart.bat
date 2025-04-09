@echo off
call conda activate subtitle-processor
python -m streamlit run st.py
pause
