#coding=utf-8
import requests
import json
import time
import os
import uuid

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
            "format": "wav",
            "url": audio_url
        },
        "additions": {
            'with_speaker_info': 'False',
        }
    }

    r = s.post(service_url + '/submit', data=json.dumps(request), headers=headers)
    resp_dic = json.loads(r.text)
    print(resp_dic)
    id = resp_dic['resp']['id']
    print(id)
    return id


def query_task(task_id):
    query_dic = {}
    query_dic['appid'] = appid
    query_dic['token'] = token
    query_dic['id'] = task_id
    query_dic['cluster'] = cluster
    query_req = json.dumps(query_dic)
    print(query_req)
    r = s.post(service_url + '/query', data=query_req, headers=headers)
    print(r.text)
    resp_dic = json.loads(r.text)
    return resp_dic


def upload_audio(file_path, server_url, api_key):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        return None

    try:
        with open(file_path, 'rb') as audio_file:
            file_extension = os.path.splitext(file_path)[1].lower()
            content_type = 'audio/wav' if file_extension == '.wav' else 'audio/mpeg'
            
            headers = {
                'Content-Type': content_type,
                'X-API-Key': api_key
            }
            
            # 打印请求信息
            print("\n=== 请求信息 ===")
            print(f"上传地址: {server_url}/api/upload")
            print(f"请求头: {headers}")
            print(f"文件路径: {file_path}")
            print(f"文件类型: {content_type}")
            
            response = requests.post(f"{server_url}/api/upload", data=audio_file, headers=headers)
        
            # 打印响应信息
            print("\n=== 响应信息 ===")
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("\n文件上传成功")
            response_json = response.json()
            return response_json.get('file_url')
        else:
            print(f"\n上传失败，状态码: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"\n上传过程中发生错误: {e}")
        return None
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        return None


def file_recognize(local_audio_path=None):
    global audio_url
    
    if local_audio_path:
        # 上传音频文件并获取URL
        server_url = "http://www.52ai.fun"
        api_key = "1F1vmARoSjXRTDvywh9XtbnR8vd74AfffF0t0jn3qhM"
        uploaded_url = upload_audio(local_audio_path, server_url, api_key)
        if uploaded_url:
            audio_url = uploaded_url
            print(f"获取到的音频URL: {audio_url}")
        else:
            print("音频文件上传失败")
            return

    task_id = submit_task()
    start_time = time.time()
    while True:
        time.sleep(2)
        # query result
        resp_dic = query_task(task_id)
        if resp_dic['resp']['code'] == 1000: # task finished
            print("success")
            exit(0)
        elif resp_dic['resp']['code'] < 2000: # task failed
            print("failed")
            exit(0)
        now_time = time.time()
        if now_time - start_time > 300: # wait time exceeds 300s
            print('wait time exceeds 300s')
            exit(0)


if __name__ == '__main__':
    current_dir = os.getcwd()
    audio_file_path = os.path.join(current_dir, "2.mp3")
    file_recognize(audio_file_path)