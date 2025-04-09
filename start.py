"""
启动subtitle-processor，并在启动前检查必要的依赖和模型
"""
import os
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

def check_dependencies():
    """检查必要的依赖是否安装"""
    try:
        import streamlit
        import spacy
        import spacy_langdetect  # 语言检测依赖
        import langdetect  # 日语检测依赖
        return True
    except ImportError as e:
        console.print(f"[red]Missing dependencies: {e}[/red]")
        console.print("[yellow]Please run: python install.py[/yellow]")
        return False

def init_spacy_language_detector():
    """初始化spacy语言检测器"""
    try:
        import spacy
        from spacy.language import Language
        from spacy_langdetect import LanguageDetector

        def get_lang_detector(nlp, name):
            return LanguageDetector()

        # 注册语言检测器
        if not Language.has_factory("language_detector"):
            Language.factory("language_detector", func=get_lang_detector)
            console.print("[green]✓ Language detector initialized[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to initialize language detector: {str(e)}[/yellow]")

def check_spacy_models():
    """检查并尝试下载必要的spaCy模型"""
    from core.download_models import download_all_models
    try:
        download_all_models()
        return True
    except Exception as e:
        console.print(f"[red]Error checking spaCy models: {str(e)}[/red]")
        return False

def main():
    console.print(Panel("[bold blue]🚀 Starting subtitle-processor[/bold blue]"))

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 检查spaCy模型
    # 初始化语言检测器
    init_spacy_language_detector()
    
    console.print("[blue]🔍 Checking spaCy models...[/blue]")
    if not check_spacy_models():
        console.print(Panel(
            "[yellow]Warning: Some models might be missing.\n"
            "You can try downloading them manually:\n"
            "python -m spacy download en_core_web_md[/yellow]"
        ))
        if not console.input("\nContinue anyway? (y/N): ").lower().startswith('y'):
            sys.exit(1)

    # 启动Streamlit
    console.print("[green]✨ Starting Streamlit server...[/green]")
    try:
        subprocess.run(["streamlit", "run", "st.py"], check=True)
    except KeyboardInterrupt:
        console.print("\n[blue]👋 Thank you for using subtitle-processor![/blue]")
    except Exception as e:
        console.print(f"[red]Error starting Streamlit: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
