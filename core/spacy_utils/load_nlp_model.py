import os,sys
import spacy
from spacy.cli import download
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from rich import print
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.config_utils import load_key

SPACY_MODEL_MAP = load_key("spacy_model_map")

def get_spacy_model(language: str):
    model = SPACY_MODEL_MAP.get(language.lower(), "en_core_web_md")
    if language not in SPACY_MODEL_MAP:
        print(f"[yellow]Spacy model does not support '{language}', using en_core_web_md model as fallback...[/yellow]")
    return model

def get_lang_detector(nlp, name):
    """返回语言检测器工厂"""
    return LanguageDetector(language_detection_kwargs={'seed': 42})

# 注册语言检测器工厂
Language.factory("language_detector", func=get_lang_detector)

def detect_language(text: str) -> str:
    """检测文本的语言，使用langdetect和spacy_langdetect"""
    text_sample = text[:1000]  # 只使用前1000个字符

    # 首先使用langdetect检测，它对日语支持较好
    try:
        from langdetect import detect
        lang = detect(text_sample)
        if lang == 'ja':
            print("[blue]✨ Detected Japanese language[/blue]")
            return 'ja'
    except Exception as e:
        print(f"[yellow]langdetect detection failed: {str(e)}[/yellow]")

    # 如果不是日语或检测失败，使用spacy的langdetect进行双重验证
    try:
        nlp = spacy.load("en_core_web_md")
        nlp.add_pipe('language_detector', last=True)
        doc = nlp(text_sample)
        detected_lang = doc._.language['language']
        confidence = doc._.language['score']
        print(f"[blue]✨ Detected language: {detected_lang} (confidence: {confidence:.2f})[/blue]")
        return detected_lang
    except Exception as e:
        print(f"[yellow]Warning: Language detection failed: {str(e)}[/yellow]")
        print("[yellow]Falling back to English...[/yellow]")
        return "en"

MODELS_DIR = os.path.expanduser("~/.cache/spacy/models")
os.makedirs(MODELS_DIR, exist_ok=True)

def check_local_model(model_name: str) -> bool:
    """检查模型是否已在本地下载"""
    try:
        spacy.load(model_name)
        return True
    except OSError:
        return False

def safe_download_model(model_name: str, max_retries: int = 3, retry_delay: int = 5) -> bool:
    """安全下载模型，带有重试机制和网络错误处理

    Args:
        model_name: 要下载的模型名称
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）

    Returns:
        bool: 下载是否成功
    """
    import time
    import requests.exceptions
    network_errors = (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RequestException
    )

    for attempt in range(max_retries):
        try:
            download(model_name)
            return True
        except network_errors as e:
            if attempt < max_retries - 1:
                print(f"[yellow]Network error on attempt {attempt + 1}: {str(e)}[/yellow]")
                print(f"[blue]Waiting {retry_delay} seconds before retrying...[/blue]")
                time.sleep(retry_delay)
                continue
            else:
                print(f"[red]Network error after {max_retries} attempts.[/red]")
                print("[yellow]Please check your network connection and proxy settings.[/yellow]")
                return False
        except Exception as e:
            print(f"[red]Unexpected error downloading model: {str(e)}[/red]")
            return False

def load_model():
    try:
        # 获取源语言设置
        source_lang = load_key("source_language", "auto")
        
        # 如果是auto，则尝试从detected_language获取
        if source_lang == "auto":
            detected_lang = load_key("detected_language", "")
            language = detected_lang if detected_lang else "en"
        else:
            language = source_lang
        
        # 获取Spacy模型名称
        model = get_spacy_model(language)
        print(f"[blue]⏳ Loading NLP Spacy model: <{model}> ...[/blue]")
        
        # 检查并加载模型
        if not check_local_model(model):
            print(f"[yellow]Model {model} not found locally, attempting to download...[/yellow]")
            if not safe_download_model(model):
                print("[yellow]Download failed, falling back to en_core_web_md...[/yellow]")
                model = "en_core_web_md"
                if not check_local_model(model) and not safe_download_model(model):
                    raise ValueError("Unable to download spaCy models. Please check your network connection.")

        # 加载模型并添加语言检测
        nlp = spacy.load(model)
        if not nlp.has_pipe("language_detector"):
            try:
                nlp.add_pipe('language_detector', last=True)
            except Exception as e:
                print(f"[yellow]Warning: Language detector initialization failed: {str(e)}[/yellow]")
        print(f"[green]✅ NLP model {model} loaded successfully![/green]")
        return nlp
        
    except Exception as e:
        print(f"[red]Critical error loading NLP models: {str(e)}[/red]")
        raise ValueError(f"❌ Failed to initialize NLP: {str(e)}")

# 保留init_nlp作为别名以保持向后兼容
init_nlp = load_model
