import logging
from tools.file_upload import FileUploadTool
from tools.speech_recognition import SpeechRecognitionTool
from tools.subtitle_generator import SubtitleGenerator
from chains.speech_chain import SpeechProcessingChain
import os

def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 初始化工具
    upload_tool = FileUploadTool()
    recognition_tool = SpeechRecognitionTool()
    subtitle_tool = SubtitleGenerator()

    # 创建处理链
    chain = SpeechProcessingChain(upload_tool, recognition_tool, subtitle_tool)

    # 获取音频文件路径
    current_dir = os.getcwd()
    audio_file = os.path.join(current_dir, "2.mp3")

    # 检查文件是否存在
    if not os.path.exists(audio_file):
        logging.error(f"文件不存在: {audio_file}")
        return

    # 执行处理链
    result = chain({"file_path": audio_file})
    
    # 输出结果
    if result:
        print("\n处理完成!")
        print(f"识别文本: {result['text']}")
        print(f"音频URL: {result['audio_url']}")
        print(f"字幕文件: {result['subtitle_path']}")

if __name__ == "__main__":
    main() 