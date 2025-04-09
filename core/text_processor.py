import os
from typing import List, Dict
from .subtitle_utils import SubtitleProcessor
from .spacy_utils.load_nlp_model import load_model, detect_language
from .step4_1_summarize import get_summary
from .step4_2_translate_all import translate_all
from .config_utils import load_key, update_key

class TextProcessor:
    def __init__(self):
        self.subtitle_processor = SubtitleProcessor()
        self.nlp = load_model()
        self.output_dir = "output"
        self.processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)

    def process_subtitle_file(self, subtitle_path: str):
        """处理字幕文件的主函数"""
        # 加载并解析字幕
        subtitle_data = self.subtitle_processor.load_subtitle(subtitle_path)
        
        # 提取纯文本用于处理
        texts = self.subtitle_processor.extract_text_only(subtitle_data)
        
        # 如果源语言设置为auto，尝试检测语言
        if load_key("source_language") == "auto":
            # 使用第一个字幕文本进行语言检测
            detected_lang = detect_language(texts[0])
            update_key("detected_language", detected_lang)
            # 重新加载对应语言的NLP模型
            self.nlp = load_model()

        # 分句和分段处理
        processed_texts = self._process_sentences(texts)
        
        # 保存处理后的文本
        log_dir = os.path.join(self.output_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        
        # 获取摘要
        get_summary(processed_texts)
        
        # 翻译处理
        translated_texts = translate_all(processed_texts)
        if translated_texts is None:
            raise ValueError("Translation failed: No translated texts returned. Check the logs for more details.")
        
        # 检查每个字幕的长度并在需要时调整
        processed_translations = []
        for sub, text in zip(subtitle_data, translated_texts):
            duration = (sub['end_time'] - sub['start_time']) / 1000.0  # 转换为秒
            processed_text = self.subtitle_processor.check_text_length(text, duration)
            processed_translations.append(processed_text)
        
        # 创建翻译后的字幕
        translated_subs = self.subtitle_processor.create_translated_subtitles(
            subtitle_data, processed_translations
        )
        
        # 保存处理后的字幕
        self._save_processed_subtitles(subtitle_data, translated_subs)
        
    def _process_sentences(self, texts: List[str]) -> List[str]:
        """使用NLP处理句子"""
        processed_texts = []
        
        for text in texts:
            doc = self.nlp(text)
            
            # 使用spaCy进行句子分割
            sentences = [sent.text.strip() for sent in doc.sents]
            
            # 合并处理后的句子
            processed_text = ' '.join(sentences)
            processed_texts.append(processed_text)
            
        return processed_texts
    
    def _save_processed_subtitles(self, 
                                original_subs: List[Dict],
                                translated_subs: List[Dict]) -> None:
        """保存处理后的字幕文件"""
        # 保存原文字幕
        self.subtitle_processor.save_subtitle(
            original_subs,
            os.path.join(self.processed_dir, "original.srt"),
            format_type="srt"
        )
        
        # 保存翻译字幕
        self.subtitle_processor.save_subtitle(
            translated_subs,
            os.path.join(self.processed_dir, "translated.srt"),
            format_type="srt"
        )
        
        # 保存双语字幕（垂直排列）
        self.subtitle_processor.merge_subtitle_files(
            os.path.join(self.processed_dir, "original.srt"),
            os.path.join(self.processed_dir, "translated.srt"),
            os.path.join(self.processed_dir, "bilingual_vertical.srt"),
            format_type="srt",
            dual_mode="vertical"
        )
        
        # 保存双语字幕（水平排列）
        self.subtitle_processor.merge_subtitle_files(
            os.path.join(self.processed_dir, "original.srt"),
            os.path.join(self.processed_dir, "translated.srt"),
            os.path.join(self.processed_dir, "bilingual_horizontal.srt"),
            format_type="srt",
            dual_mode="horizontal"
        )
