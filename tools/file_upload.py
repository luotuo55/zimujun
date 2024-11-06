from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests
import logging
from config import Config
import os

class FileUploadInput(BaseModel):
    file_path: str

class FileUploadTool(BaseTool):
    name: str = Field(default="file_upload")
    description: str = Field(default="上传音频文件到服务器")
    args_schema: Type[BaseModel] = Field(default=FileUploadInput)

    def _run(self, file_path: str) -> str:
        """上传文件并返回URL"""
        try:
            with open(file_path, 'rb') as audio_file:
                headers = {
                    'X-Admin-Key': Config.SERVER.admin_key,
                    'Origin': Config.SERVER.url,
                    'Referer': Config.SERVER.url,
                    'Host': Config.SERVER.url.replace('http://', '').replace('https://', ''),
                    'Accept': '*/*'
                }
                
                files = {
                    'file': (
                        os.path.basename(file_path),
                        audio_file,
                        'audio/mpeg'
                    )
                }
                
                response = requests.post(
                    f"{Config.SERVER.url}{Config.SERVER.upload_path}",
                    headers=headers,
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and 'file_url' in result['data']:
                        return f"{Config.SERVER.url}{result['data']['file_url']}"
                
                raise Exception(f"上传失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logging.error(f"文件上传错误: {str(e)}")
            raise

    async def _arun(self, file_path: str) -> str:
        """异步上传实现（如果需要）"""
        raise NotImplementedError("异步上传暂未实现")