"""
预下载所需的spacy模型到本地
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spacy.cli import download
from rich import print
from core.config_utils import load_key
from core.spacy_utils.load_nlp_model import MODELS_DIR, safe_download_model

def download_all_models():
    """下载所有配置中定义的spacy模型"""
    print("[blue]🚀 Starting to download spaCy models...[/blue]")
    
    # 确保模型目录存在
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # 获取所有需要的模型
    models = load_key("spacy_model_map", {}).values()
    if not models:
        print("[yellow]Warning: No models defined in config.yaml[/yellow]")
        models = ["en_core_web_md"]  # 至少下载英语模型作为后备
    
    # 下载每个模型
    success_count = 0
    for model in models:
        print(f"\n[blue]⏳ Downloading model: {model}...[/blue]")
        if safe_download_model(model):
            success_count += 1
            print(f"[green]✅ Successfully downloaded {model}[/green]")
        else:
            print(f"[red]❌ Failed to download {model}[/red]")
    
    print(f"\n[blue]📊 Download summary: {success_count}/{len(models)} models downloaded successfully[/blue]")

if __name__ == "__main__":
    download_all_models()
