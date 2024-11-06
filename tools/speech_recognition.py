from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests
import json
import time
import logging
from config import Config

class SpeechRecognitionInput(BaseModel):
    audio_url: str

class SpeechRecognitionTool(BaseTool):
    name: str = Field(default="speech_recognition")
    description: str = Field(default="将音频转换为文本")
    args_schema: Type[BaseModel] = Field(default=SpeechRecognitionInput)

    def _run(self, audio_url: str) -> str:
        """执行语音识别"""
        try:
            # 提交任务
            task_id = self._submit_task(audio_url)
            logging.info(f"提交任务成功，任务ID: {task_id}")
            
            # 轮询结果
            start_time = time.time()
            while True:
                time.sleep(2)
                result = self._query_task(task_id)
                logging.info(f"查询结果: {result}")
                
                if result.get('code') == 1000:
                    text = result.get('text', '')
                    logging.info(f"识别成功: {text}")
                    return text
                elif result.get('code') < 2000:
                    error_msg = f"识别失败: {result.get('message')}"
                    logging.error(error_msg)
                    raise Exception(error_msg)
                    
                if time.time() - start_time > 300:
                    raise Exception("识别超时")
                    
        except Exception as e:
            logging.error(f"语音识别错误: {str(e)}")
            raise

    def _submit_task(self, audio_url: str) -> str:
        """提交识别任务"""
        try:
            # 修正认证头格式
            headers = {'Authorization': f'Bearer; {Config.SPEECH.token}'}
            
            request = {
                "app": {
                    "appid": Config.SPEECH.appid,
                    "token": Config.SPEECH.token,
                    "cluster": Config.SPEECH.cluster
                },
                "user": {
                    "uid": "388808087185088_demo"
                },
                "audio": {
                    "format": "mp3",
                    "url": audio_url
                },
                "additions": {
                    "with_speaker_info": "False"
                }
            }
            
            logging.info(f"提交任务请求: {json.dumps(request, ensure_ascii=False)}")
            
            # 使用 data=json.dumps(request) 而不是 json=request
            response = requests.post(
                f"{Config.SPEECH.service_url}/submit",
                data=json.dumps(request),
                headers=headers,
                timeout=30
            )
            
            logging.info(f"提交任务响应: {response.text}")
            
            if response.status_code != 200:
                raise Exception(f"提交任务失败: {response.status_code} - {response.text}")
                
            result = response.json()
            if 'resp' not in result:
                raise Exception(f"无效的响应格式: {result}")
                
            return result['resp']['id']
            
        except Exception as e:
            logging.error(f"提交任务错误: {str(e)}")
            raise

    def _query_task(self, task_id: str) -> dict:
        """查询任务结果"""
        try:
            # 修正认证头格式
            headers = {'Authorization': f'Bearer; {Config.SPEECH.token}'}
            
            request = {
                'appid': Config.SPEECH.appid,
                'token': Config.SPEECH.token,
                'id': task_id,
                'cluster': Config.SPEECH.cluster
            }
            
            logging.info(f"查询任务请求: {json.dumps(request, ensure_ascii=False)}")
            
            # 使用 data=json.dumps(request) 而不是 json=request
            response = requests.post(
                f"{Config.SPEECH.service_url}/query",
                data=json.dumps(request),
                headers=headers,
                timeout=30
            )
            
            logging.info(f"查询任务响应: {response.text}")
            
            if response.status_code != 200:
                raise Exception(f"查询任务失败: {response.status_code} - {response.text}")
                
            result = response.json()
            if 'resp' not in result:
                raise Exception(f"无效的响应格式: {result}")
                
            return result['resp']
            
        except Exception as e:
            logging.error(f"查询任务错误: {str(e)}")
            raise

    async def _arun(self, audio_url: str) -> str:
        """异步实现（如果需要）"""
        raise NotImplementedError("异步识别暂未实现")