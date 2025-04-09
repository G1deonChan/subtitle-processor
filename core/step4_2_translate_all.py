import sys, os
from typing import List, Dict, Optional, Union
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import json
import concurrent.futures
from core.translate_once import translate_lines
from core.step4_1_summarize import search_things_to_note_in_prompt
from core.step6_generate_final_timeline import align_timestamp
from core.config_utils import load_key
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from difflib import SequenceMatcher

console = Console()

SENTENCE_SPLIT_FILE = "output/log/sentence_splitbymeaning.txt"
TRANSLATION_RESULTS_FILE = "output/log/translation_results.xlsx"
TERMINOLOGY_FILE = "output/log/terminology.json"
CLEANED_CHUNKS_FILE = "output/log/cleaned_chunks.xlsx"

# Function to split text into chunks
def split_chunks_by_chars(chunk_size=400, max_i=8): 
    """Split text into chunks based on character count, return a list of multi-line text chunks"""
    with open(SENTENCE_SPLIT_FILE, "r", encoding="utf-8") as file:
        sentences = file.read().strip().split('\n')

    chunks = []
    chunk = ''
    sentence_count = 0
    for sentence in sentences:
        if len(chunk) + len(sentence + '\n') > chunk_size or sentence_count == max_i:
            chunks.append(chunk.strip())
            chunk = sentence + '\n'
            sentence_count = 1
        else:
            chunk += sentence + '\n'
            sentence_count += 1
    chunks.append(chunk.strip())
    return chunks

# Get context from surrounding chunks
def get_previous_content(chunks, chunk_index):
    return None if chunk_index == 0 else chunks[chunk_index - 1].split('\n')[-3:] # Get last 3 lines
def get_after_content(chunks, chunk_index):
    return None if chunk_index == len(chunks) - 1 else chunks[chunk_index + 1].split('\n')[:2] # Get first 2 lines

# 🔍 Translate a single chunk
def translate_chunk(chunk, chunks, theme_prompt, i):
    things_to_note_prompt = search_things_to_note_in_prompt(chunk)
    previous_content_prompt = get_previous_content(chunks, i)
    after_content_prompt = get_after_content(chunks, i)
    translation, english_result = translate_lines(chunk, previous_content_prompt, after_content_prompt, things_to_note_prompt, theme_prompt, i)
    return i, english_result, translation

# Add similarity calculation function
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 🚀 Main function to translate all chunks
def translate_all(texts: List[str] = None):
    """翻译处理主函数
    Args:
        texts: 要处理的文本列表。如果为None，则尝试从文件读取
    """
    # 检查是否存在翻译结果文件
    if os.path.exists(TRANSLATION_RESULTS_FILE):
        try:
            # 尝试读取已有的翻译结果
            df = pd.read_excel(TRANSLATION_RESULTS_FILE)
            if 'Translation' in df.columns:
                console.print(Panel("📝 Found existing translation, loading from file...", title="Info", border_style="blue"))
                return df['Translation'].tolist()
            else:
                raise ValueError("Invalid translation file format")
        except Exception as e:
            # 如果读取失败，备份并重新翻译
            backup_file = f"{TRANSLATION_RESULTS_FILE}.bak"
            os.rename(TRANSLATION_RESULTS_FILE, backup_file)
            console.print(f"[yellow]Warning: Failed to load existing translation: {str(e)}[/yellow]")
            console.print(f"[yellow]Original file backed up to: {backup_file}[/yellow]")
    
    console.print("[bold green]Start Translating All...[/bold green]")
    
    # 获取要处理的文本
    if texts is None:
        # 如果没有提供文本，尝试从文件读取（向后兼容）
        try:
            with open(SENTENCE_SPLIT_FILE, "r", encoding="utf-8") as file:
                sentences = file.read().strip().split('\n')
        except FileNotFoundError:
            console.print("[red]Error: No input text provided and cannot read from file[/red]")
            return None
    else:
        sentences = texts
    
    # 分块处理
    chunks = []
    chunk = ''
    sentence_count = 0
    chunk_size = 500
    max_i = 10
    
    for sentence in sentences:
        if len(chunk) + len(str(sentence) + '\n') > chunk_size or sentence_count == max_i:
            chunks.append(chunk.strip())
            chunk = str(sentence) + '\n'
            sentence_count = 1
        else:
            chunk += str(sentence) + '\n'
            sentence_count += 1
    chunks.append(chunk.strip())
    with open(TERMINOLOGY_FILE, 'r', encoding='utf-8') as file:
        theme_prompt = json.load(file).get('theme')

    # 🔄 Use concurrent execution for translation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Translating chunks...", total=len(chunks))
        with concurrent.futures.ThreadPoolExecutor(max_workers=load_key("max_workers")) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(translate_chunk, chunk, chunks, theme_prompt, i)
                futures.append(future)

            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                progress.update(task, advance=1)

    results.sort(key=lambda x: x[0])  # Sort results based on original order
    
    # 💾 Save results to lists and Excel file
    src_text, trans_text = [], []
    for i, chunk in enumerate(chunks):
        chunk_lines = chunk.split('\n')
        src_text.extend(chunk_lines)
        
        # Calculate similarity between current chunk and translation results
        chunk_text = ''.join(chunk_lines).lower()
        matching_results = [(r, similar(''.join(r[1].split('\n')).lower(), chunk_text)) 
                          for r in results]
        best_match = max(matching_results, key=lambda x: x[1])
        
        # Check similarity and handle exceptions
        if best_match[1] < 0.9:
            console.print(f"[yellow]Warning: No matching translation found for chunk {i}[/yellow]")
            raise ValueError(f"Translation matching failed (chunk {i})")
        elif best_match[1] < 1.0:
            console.print(f"[yellow]Warning: Similar match found (chunk {i}, similarity: {best_match[1]:.3f})[/yellow]")
            
        trans_text.extend(best_match[0][2].split('\n'))
    
    # Save translation results and return
    df_translate = pd.DataFrame({'Source': src_text, 'Translation': trans_text})
    df_translate.to_excel(TRANSLATION_RESULTS_FILE, index=False)
    console.print("[bold green]✅ Translation completed and results saved.[/bold green]")
    return trans_text

if __name__ == '__main__':
    translate_all()
