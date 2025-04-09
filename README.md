<div align="center">


# subtitle-processor

**轻松处理视频字幕**

</div>

## 🌟 项目概述

本项目**subtitle-processor**是基于[Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo)项目的二次开发版本，专注于**视频字幕处理和翻译功能**。

原版VideoLingo提供了完整的视频翻译和配音功能，而本版本移除了视频下载和音频配音相关功能，专注于为内容创作者和翻译人员提供专业的字幕处理工具。

**主要功能：**

-   📝 **上传字幕文件**：支持SRT、ASS、SSA、VTT等多种格式
-   **🧠 NLP智能分句**：使用NLP和LLM技术智能分割字幕行，提供更好的翻译上下文
-   **🌍 AI翻译**：利用大语言模型(LLM)进行高质量、上下文感知的翻译，支持自定义术语
-   **✂️ 智能对齐**：根据时间和可读性自动切割和对齐长字幕
-   **⏳ 时间轴生成**：为翻译后的字幕生成准确的时间轴
-   **💾 下载结果**：可下载原始、翻译和双语字幕文件
-   **🚀 一键处理**：简单的Streamlit界面，操作便捷
-   **🌐 多语言界面**：支持多种界面语言
-   **📊 进度跟踪**：处理过程中显示详细进度

## 安装说明

> **注意：** 部分字幕操作仍需要FFmpeg支持，请通过包管理器安装：
> - Windows: ```choco install ffmpeg``` (通过[Chocolatey](https://chocolatey.org/))
> - macOS: ```brew install ffmpeg``` (通过[Homebrew](https://brew.sh/))
> - Linux: ```sudo apt install ffmpeg``` (Debian/Ubuntu)

1. 克隆仓库

```bash
git clone https://github.com/G1deonChan/subtitle-processor.git
cd subtitle-processor
```

2. 安装依赖(需要`python=3.10`或更高版本，测试支持3.10/3.11/3.12)

```bash
# 推荐: 创建虚拟环境
conda create -n subtitle-processor python=3.10 -y
conda activate subtitle-processor
# 或使用venv
# python -m venv venv
# source venv/bin/activate  # Windows使用`venv\Scripts\activate`

# 安装依赖
python install.py
# 或手动安装: pip install -r requirements.txt
```

3. 启动应用

```bash
# 确保在项目根目录
python start.py
# 或直接运行: streamlit run st.py
```

```

## 当前局限性

1.  **复杂格式**：一些高级ASS/SSA样式(如复杂动画、卡拉OK效果)可能在处理过程中被简化或丢失，基本样式(如位置和颜色)通常保留
2.  **LLM依赖**：翻译质量很大程度上取决于所选LLM，较弱的模型可能在上下文理解或翻译准确性上表现不佳
3.  **处理时间**：非常长的字幕文件由于需要NLP分析和多次LLM调用进行翻译，可能需要较长时间处理
4.  **角色风格**：虽然文本会被处理，但完美匹配不同语言间特定角色的说话风格超出了自动翻译的范围

## 📄 许可证

本项目采用Apache 2.0许可证，继承自原版[VideoLingo](https://github.com/Huanshere/VideoLingo)项目。

特别感谢：
-   [**Huanshere/VideoLingo**](https://github.com/Huanshere/VideoLingo) - 本项目的基础
-   [pysubs2](https://github.com/tkarabela/pysubs2) - 强大的字幕文件解析和操作库
-   spaCy、langdetect等依赖库的开发者

## 📬 联系方式(请更新为您的信息)

-   在GitHub提交[Issues](https://github.com/G1deonChan/subtitle-processor/issues)或[Pull Requests](https://github.com/G1deonChan/subtitle-processor/pulls)

---

<p align="center">如果您觉得这个项目有用，请给它一个⭐️！</p>
