from flask import Flask, render_template, request, jsonify
import os
from speech_recognition import file_recognize  # 更新了导入语句
from datetime import datetime

app = Flask(__name__)

# 用于存储识别结果
recognition_results = []

@app.route('/')
def index():
    return render_template('index.html', results=recognition_results)

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 保存上传的文件
    temp_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(temp_path)

    try:
        # 调用语音识别
        result = file_recognize(temp_path)
        print("识别结果:", result)
        
        if result.get('success'):
            recognition_result = {
                'filename': file.filename,
                'text': result['text'],
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            recognition_results.append(recognition_result)
            return jsonify({
                'success': True, 
                'result': result['text'],
                'filename': file.filename,
                'message': result['message']
            })
        else:
            error_message = result.get('error', '未知错误')
            details = result.get('details', {})
            print(f"识别失败: {error_message}, 详细信息: {details}")
            return jsonify({
                'error': error_message,
                'details': details
            }), 500
    except Exception as e:
        print("处理过程中出现错误:", str(e))
        return jsonify({'error': f'处理错误: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 