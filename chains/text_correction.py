import requests
import json
import logging
from config import Config

class TextCorrector:
    def __init__(self):
        self.endpoint = f"https://{Config.TEXT_CORRECTION['endpoint']}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.TEXT_CORRECTION['ark_api_key']}"
        }
        logging.info(f"初始化TextCorrector，endpoint: {self.endpoint}")

    def correct_text(self, text):
        try:
            payload = {
                "model": Config.TEXT_CORRECTION['model'],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional text proofreader. Please help proofread and correct the text while maintaining its original meaning."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }

            api_url = f"{self.endpoint}/api/v3/chat/completions"
            
            logging.info(f"调用API: {api_url}")
            logging.info(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logging.info(f"请求体: {json.dumps(payload, ensure_ascii=False)}")

            response = requests.post(
                api_url,
                headers=self.headers,
                json=payload,
                verify=True,  # 确保SSL验证
                timeout=30
            )
            
            logging.info(f"响应状态码: {response.status_code}")
            logging.info(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                corrected_text = result['choices'][0]['message']['content'].strip()
                return {
                    "original": text,
                    "corrected": corrected_text,
                    "success": True,
                    "message": "校准成功"
                }
            else:
                error_msg = f"API错误 {response.status_code}: {response.text}"
                logging.error(error_msg)
                return {
                    "original": text,
                    "corrected": text,
                    "success": False,
                    "error": error_msg,
                    "message": "校准失败，返回原文"
                }

        except Exception as e:
            error_msg = f"文本校准过程出错: {str(e)}"
            logging.error(error_msg)
            return {
                "original": text,
                "corrected": text,
                "success": False,
                "error": error_msg,
                "message": "校准失败，返回原文"
            }

def process_audio_with_correction(audio_file_path):
    """处理音频文件并进行文本校准"""
    try:
        # 1. 语音识别
        recognition_result = file_recognize(audio_file_path)
        if not recognition_result or not recognition_result.get("success"):
            return {
                "error": "语音识别失败",
                "details": recognition_result
            }
        
        recognized_text = recognition_result.get("text", "")
        if not recognized_text:
            return {
                "error": "未能识别出文本"
            }
            
        # 2. 文本校准
        corrector = TextCorrector()
        correction_result = corrector.correct_text(recognized_text)
        
        return {
            "success": correction_result["success"],
            "original_text": correction_result["original"],
            "corrected_text": correction_result["corrected"],
            "error": correction_result.get("error")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"处理过程出错: {str(e)}"
        }

if __name__ == "__main__":
    # 使用示例
    audio_file = "path/to/your/audio.mp3"
    
    print("开始处理音频文件...")
    result = process_audio_with_correction(audio_file)
    
    if result.get("success"):
        print("\n原始识别文本:")
        print(result["original_text"])
        print("\n校准后文本:")
        print(result["corrected_text"])
    else:
        print("\n处理失败:")
        print(result.get("error")) 