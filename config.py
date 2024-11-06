from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class ServerConfig(BaseModel):
    url: str = os.getenv('SERVER_URL', 'http://www.52ai.fun')
    upload_path: str = os.getenv('SERVER_UPLOAD_PATH', '/api/upload')
    admin_key: str = os.getenv('SERVER_ADMIN_KEY', 'dgp432126')

class SpeechConfig(BaseModel):
    appid: str = os.getenv('SPEECH_APPID', '3451204869')
    token: str = os.getenv('SPEECH_TOKEN', 'ZZEUVzi_edwgtQAkaCY5dsfWIvyh4_Q9')
    cluster: str = os.getenv('SPEECH_CLUSTER', 'volc_auc_meeting')
    service_url: str = os.getenv('SPEECH_SERVICE_URL', 'https://openspeech.bytedance.com/api/v1/auc')

class Config:
    SERVER = ServerConfig()
    SPEECH = SpeechConfig()

    # 文本校准配置
    TEXT_CORRECTION = {
        "ark_api_key": os.getenv('ARK_API_KEY'),
        "endpoint": os.getenv('ARK_ENDPOINT', 'ark.cn-beijing.volces.com'),
        "model": os.getenv('ARK_MODEL', 'doubao-pro-4k-240515'),
        "temperature": float(os.getenv('ARK_TEMPERATURE', 0.1)),
        "max_tokens": int(os.getenv('ARK_MAX_TOKENS', 4096))
    }
    
    # 文件上传配置
    UPLOAD = {
        "allowed_extensions": ["wav", "mp3"],
        "max_file_size": int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))
    }

    @staticmethod
    def validate_config():
        """验证必要的配置是否存在"""
        required_vars = [
            'ARK_API_KEY',
            'SERVER_URL',
            'SERVER_UPLOAD_PATH',
            'SERVER_ADMIN_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}") 