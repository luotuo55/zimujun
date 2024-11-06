#coding=utf-8
import requests
import json
import time
import os
import uuid
import logging
from config import Config

s = requests

appid = '3451204869'
token = 'ZZEUVzi_edwgtQAkaCY5dsfWIvyh4_Q9'
cluster = 'volc_auc_meeting'
audio_url = ''
service_url = 'https://openspeech.bytedance.com/api/v1/auc'

headers = {'Authorization': 'Bearer; {}'.format(token)}

def submit_task():
    request = {
        "app": {
            "appid": appid,
            "token": token,
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088_demo"
        },
        "audio": {
            "format": "mp3",
            "url": audio_url
        },
        "additions": {
            'with_speaker_info': 'False',
        }
    }

    r = s.post(service_url + '/submit', data=json.dumps(request), headers=headers)
    resp_dic = json.loads(r.text)
    print("提交任务响应:", resp_dic)
    id = resp_dic['resp']['id']
    return id


def query_task(task_id):
    query_dic = {
        'appid': appid,
        'token': token,
        'id': task_id,
        'cluster': cluster
    }
    query_req = json.dumps(query_dic)
    r = s.post(service_url + '/query', data=query_req, headers=headers)
    resp_dic = json.loads(r.text)
    return resp_dic


def upload_audio(file_path):
    """上传音频文件到服务器"""
    try:
        with open(file_path, 'rb') as audio_file:
            # 设置请求头
            headers = {
                'X-Admin-Key': Config.SERVER['admin_key'],
                'Origin': Config.SERVER['url'],
                'Referer': Config.SERVER['url'],
                'Host': Config.SERVER['url'].replace('http://', '').replace('https://', ''),
                'Accept': '*/*'
            }
            
            # 准备文件数据
            files = {
                'file': (
                    os.path.basename(file_path),
                    audio_file,
                    'audio/mpeg'
                )
            }
            
            logging.info(f"正在上传音频文件: {file_path}")
            logging.info(f"请求头: {headers}")
            
            response = requests.post(
                f"{Config.SERVER['url']}{Config.SERVER['upload_path']}", 
                headers=headers,
                files=files,
                timeout=30
            )
            
            logging.info(f"上传响应状态码: {response.status_code}")
            logging.info(f"响应头: {dict(response.headers)}")
            logging.info(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # 从 data 字段中获取文件 URL
                if 'data' in result and 'file_url' in result['data']:
                    # 拼接完整的URL
                    file_url = f"{Config.SERVER['url']}{result['data']['file_url']}"
                    logging.info(f"文件上传成功，URL: {file_url}")
                    return file_url
                else:
                    logging.error(f"响应格式不正确: {result}")
                    return None
            else:
                logging.error(f"上传失败: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logging.error(f"上传过程中发生错误: {str(e)}")
        return None


def file_recognize(local_audio_path=None):
    global audio_url
    
    if local_audio_path:
        logging.info(f"开始处理音频文件: {local_audio_path}")
        uploaded_url = upload_audio(local_audio_path)
        if uploaded_url:
            audio_url = uploaded_url
            logging.info(f"获取到的音频URL: {audio_url}")
        else:
            return {"error": "音频文件上传失败"}

    try:
        task_id = submit_task()
        logging.info(f"提交任务成功，任务ID: {task_id}")
        start_time = time.time()
        
        while True:
            time.sleep(2)
            resp_dic = query_task(task_id)
            logging.info(f"查询结果: {resp_dic}")
            
            if 'resp' in resp_dic:
                resp = resp_dic['resp']
                if resp['code'] == 1000:  # 任务完成
                    return {
                        "success": True,
                        "text": resp.get('text', ''),
                        "message": "识别成功"
                    }
                elif resp['code'] < 2000:  # 任务失败
                    return {
                        "error": "识别失败",
                        "message": resp.get('message', ''),
                        "details": resp
                    }
            
            if time.time() - start_time > 300:  # 5分钟超时
                return {"error": "识别超时"}
                
    except Exception as e:
        logging.error(f"识别过程发生错误: {e}")
        return {"error": f"识别错误: {str(e)}"}


if __name__ == '__main__':
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 获取当前目录
    current_dir = os.getcwd()
    audio_file_path = os.path.join(current_dir, "2.mp3")
    
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        logging.error(f"文件不存在: {audio_file_path}")
        exit(1)
        
    # 执行识别
    result = file_recognize(audio_file_path)
    logging.info(f"识别结果: {result}")