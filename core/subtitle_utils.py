import os
import re
import pysubs2
from typing import List, Dict, Optional
from core.ask_gpt import ask_gpt
from core.prompts_storage import get_subtitle_trim_prompt
from core.config_utils import load_key


class SubtitleProcessor:
    """字幕处理工具类"""
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """检测字幕文件格式"""
        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            '.srt': 'srt',
            '.ass': 'ass',
            '.ssa': 'ssa',
            '.vtt': 'vtt'
        }
        return format_map.get(ext, 'unknown')

    @staticmethod
    def load_subtitle(file_path: str) -> List[Dict]:
        """加载字幕文件，转换为统一格式"""
        format_type = SubtitleProcessor.detect_format(file_path)
        
        if format_type == 'unknown':
            raise ValueError(f"Unsupported subtitle format: {file_path}")
            
        subs = pysubs2.load(file_path, encoding='utf-8')
        
        # 转换为统一的内部格式
        subtitle_data = []
        for sub in subs:
            subtitle_data.append({
                'start_time': sub.start,  # 毫秒
                'end_time': sub.end,      # 毫秒
                'text': sub.text.replace('\\N', '\n'),  # 统一换行符
                'style': sub.style        # 保留样式信息
            })
            
        return subtitle_data

    @staticmethod
    def save_subtitle(subtitle_data: List[Dict], output_path: str, format_type: str = 'srt'):
        """保存字幕为指定格式"""
        subs = pysubs2.SSAFile()
        
        for item in subtitle_data:
            sub = pysubs2.SSAEvent(
                start=item['start_time'],
                end=item['end_time'],
                text=item['text'],
                style=item.get('style', 'Default')
            )
            subs.append(sub)
        
        # 根据需要的格式保存
        subs.save(output_path, encoding='utf-8')
        
    @staticmethod
    def merge_subtitle_files(original_path: str, translated_path: str, output_path: str,
                           format_type: str = 'srt', dual_mode: str = 'vertical') -> None:
        """合并原文和翻译字幕"""
        original_subs = SubtitleProcessor.load_subtitle(original_path)
        translated_subs = SubtitleProcessor.load_subtitle(translated_path)
        
        if len(original_subs) != len(translated_subs):
            raise ValueError("Original and translated subtitles have different lengths")
            
        merged_subs = []
        for orig, trans in zip(original_subs, translated_subs):
            if dual_mode == 'vertical':
                merged_text = f"{orig['text']}\n{trans['text']}"
            else:  # horizontal
                merged_text = f"{orig['text']} // {trans['text']}"
                
            merged_subs.append({
                'start_time': orig['start_time'],
                'end_time': orig['end_time'],
                'text': merged_text,
                'style': orig['style']
            })
            
        SubtitleProcessor.save_subtitle(merged_subs, output_path, format_type)

    @staticmethod
    def split_long_lines(subtitle_data: List[Dict], max_length: int = 40) -> List[Dict]:
        """拆分过长的字幕行"""
        result = []
        
        for sub in subtitle_data:
            lines = sub['text'].split('\n')
            new_lines = []
            
            for line in lines:
                if len(line) <= max_length:
                    new_lines.append(line)
                else:
                    # 查找合适的分割点
                    words = line.split()
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 <= max_length:
                            current_line.append(word)
                            current_length += len(word) + 1
                        else:
                            new_lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word) + 1
                    
                    if current_line:
                        new_lines.append(' '.join(current_line))
            
            result.append({
                'start_time': sub['start_time'],
                'end_time': sub['end_time'],
                'text': '\n'.join(new_lines),
                'style': sub['style']
            })
            
        return result

    @staticmethod
    def extract_text_only(subtitle_data: List[Dict]) -> List[str]:
        """提取纯文本内容用于翻译"""
        return [sub['text'] for sub in subtitle_data]

    @staticmethod
    def check_text_length(text: str, duration: float) -> str:
        """检查文本长度是否适合字幕时长，必要时缩短文本"""
        chars_per_second = load_key("subtitle.chars_per_second", 15)  # 默认每秒15个字符
        max_chars = int(duration * chars_per_second)
        
        if len(text) > max_chars:
            # 使用LLM压缩文本
            prompt = get_subtitle_trim_prompt(text, duration)
            try:
                response = ask_gpt(prompt, response_json=True)
                if 'result' in response:
                    return response['result']
            except Exception:
                # 如果LLM处理失败，使用简单的截断方法
                return text[:max_chars].rstrip() + '...'
        
        return text

    @staticmethod
    def create_translated_subtitles(original_subs: List[Dict], 
                                  translated_texts: List[str]) -> List[Dict]:
        """使用翻译后的文本创建新的字幕"""
        if len(original_subs) != len(translated_texts):
            raise ValueError("Original subtitles and translated texts have different lengths")
            
        translated_subs = []
        for orig_sub, trans_text in zip(original_subs, translated_texts):
            translated_subs.append({
                'start_time': orig_sub['start_time'],
                'end_time': orig_sub['end_time'],
                'text': trans_text,
                'style': orig_sub['style']
            })
            
        return translated_subs
