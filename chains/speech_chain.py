from typing import Dict, Any, List
import logging
import os

class SpeechProcessingChain:
    """语音处理链，包含文件上传、语音识别和字幕生成"""
    
    def __init__(self, upload_tool, recognition_tool, subtitle_tool):
        """初始化处理链"""
        self.upload_tool = upload_tool
        self.recognition_tool = recognition_tool
        self.subtitle_tool = subtitle_tool

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行处理链"""
        try:
            # 1. 上传文件
            file_path = inputs["file_path"]
            logging.info(f"开始处理文件: {file_path}")
            
            audio_url = self.upload_tool.run(file_path)
            logging.info(f"文件上传成功: {audio_url}")
            
            # 2. 语音识别
            logging.info("开始语音识别")
            recognition_result = self.recognition_tool.run(audio_url)
            
            # 检查返回类型
            if isinstance(recognition_result, dict):
                text = recognition_result.get('text', '')
                timestamps = recognition_result.get('timestamps', None)
            else:
                text = recognition_result
                timestamps = None
                
            logging.info(f"语音识别完成: {text}")
            
            # 3. 生成字幕
            logging.info("开始生成字幕")
            subtitle = self.subtitle_tool.run({
                "text": text,
                "timestamps": timestamps
            })
            logging.info("字幕生成完成")
            
            # 4. 保存字幕文件
            output_path = self._save_subtitle(inputs["file_path"], subtitle)
            logging.info(f"字幕已保存到: {output_path}")
            
            return {
                "text": text,
                "audio_url": audio_url,
                "subtitle": subtitle,
                "subtitle_path": output_path
            }
            
        except Exception as e:
            logging.error(f"处理链执行失败: {str(e)}")
            raise

    def _save_subtitle(self, audio_path: str, subtitle: str) -> str:
        """保存字幕文件"""
        try:
            # 生成字幕文件路径
            base_path = os.path.splitext(audio_path)[0]
            subtitle_path = f"{base_path}.srt"
            
            # 保存字幕文件
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(subtitle)
                
            return subtitle_path
            
        except Exception as e:
            logging.error(f"保存字幕文件失败: {str(e)}")
            raise