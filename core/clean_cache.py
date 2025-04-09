"""
清理缓存文件，用于强制重新检测语言
"""
import os
import shutil
from rich.console import Console
from rich.panel import Panel  # 添加Panel导入

console = Console()

def clean_translation_cache():
    """清理翻译和语言检测相关的缓存文件"""
    cache_files = [
        "output/log/translation_results.xlsx",
        "output/log/terminology.json",
        "output/log/cleaned_chunks.xlsx",
        "output/log/sentence_splitbymeaning.txt"
    ]
    
    backup_dir = "output/backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    for file_path in cache_files:
        try:
            if os.path.exists(file_path):
                # 创建备份
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.copy2(file_path, backup_path)
                
                # 删除原文件
                os.remove(file_path)
                console.print(f"[green]✓ Cleaned: {file_path}[/green]")
                console.print(f"[blue]  Backup saved to: {backup_path}[/blue]")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to clean {file_path}: {str(e)}[/yellow]")

if __name__ == "__main__":
    console.print("[bold blue]🧹 Cleaning translation cache...[/bold blue]")
    clean_translation_cache()
    console.print(Panel(
        "[green]Cache cleaned successfully![/green]\n\n"
        "You can now restart the application to force language re-detection.\n"
        "Previous files have been backed up to the 'output/backup' directory."
    ))
