from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import requests
import json
import re
import os
import logging
import pandas as pd  # 添加pandas库用于处理Excel文件
import io  # 添加io库用于处理上传的文件流

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chen1995')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Cookie配置模型
class CookieConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    e2mf = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# 初始化数据库和创建管理员账户
with app.app_context():
    db.create_all()
    # 检查是否已存在管理员账户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建管理员账户
        admin = User(username='admin', password='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("管理员账户创建成功！")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            logger.info(f"尝试登录用户: {username}")
            
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:  # 实际应用中请使用密码哈希
                login_user(user)
                logger.info(f"用户 {username} 登录成功")
                return redirect(url_for('admin' if user.is_admin else 'index'))
            else:
                logger.warning(f"用户 {username} 登录失败: 用户名或密码错误")
        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            return render_template('login.html', error="服务器错误，请稍后再试")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    cookie_config = CookieConfig.query.first()
    return render_template('admin.html', cookie_config=cookie_config)

@app.route('/update_cookie', methods=['POST'])
@login_required
def update_cookie():
    if not current_user.is_admin:
        return jsonify({'error': '未授权'}), 403
    
    e2mf = request.form.get('e2mf')
    if not e2mf:
        return jsonify({'error': 'e2mf不能为空'}), 400
    
    cookie_config = CookieConfig.query.first()
    if cookie_config:
        cookie_config.e2mf = e2mf
        cookie_config.updated_at = datetime.utcnow()
    else:
        cookie_config = CookieConfig(e2mf=e2mf)
        db.session.add(cookie_config)
    
    db.session.commit()
    return jsonify({'message': '更新成功'})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    student_code = request.form.get('student_code')
    goods_codes = request.form.get('goods_codes').split('、')
    
    cookie_config = CookieConfig.query.first()
    if not cookie_config:
        return jsonify({'error': '系统未配置Cookie'}), 500
    
    url = 'https://gateway.xdf.cn/web_reg_eapi/assistCart/assistAdd'
    headers = {
        'Host': 'gateway.xdf.cn',
        'Content-Type': 'application/json',
        'Origin': 'https://xubantool.xdf.cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': f'U2AT=; accessToken=; appVersion=5.2.45; e2e=E9EA4CE45CFDC27561245F32249BAF1A; e2mf={cookie_config.e2mf}; email=chenzhanhong@xdf.cn; teacherCode=U0000289451; XDFUUID=489f5bb5-144d-805e-ea29-2865f2264bf0',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 XdfWoXueApp/5.2.45 XdfWoXueRia/3.5 XdfWoXueFullScreen/false XdfWoXueTeacher/5.2.45 xdfBridge/3.5 xdfAppVer/5.2.45 xdfAppName/woxue xdfAppOther/teacher',
        'Referer': f'https://xubantool.xdf.cn/purchaseStudent?appId=xdfTeacherApp&systemSource=xdfTeacher&schoolId=3&studentCode={student_code}',
        'Accept-Language': 'zh-cn'
    }
    
    request_data = {
        "marketingSources": "",
        "marketingSourcesExt": "",
        "systemSource": "xdfTeacher",
        "appId": "xdfTeacherApp",
        "agentName": "",
        "schoolId": "3",
        "list": [{
            "goodsCode": code,
            "goodsType": 1,
            "students": [{
                "studentCode": student_code,
                "userId": "xdf006889962"
            }]
        } for code in goods_codes]
    }
    
    try:
        response = requests.post(url, json=request_data, headers=headers)
        response_data = response.json()
        
        if response_data.get('code') == 10000:
            courses_count = len(goods_codes)
            return jsonify({
                'success': True,
                'message': f'加购成功！已将{courses_count}科添加至购物车～'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'加购失败: {response_data.get("message", "未知错误")}',
                'response': response_data
            })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/import_curl', methods=['POST'])
@login_required
def import_curl():
    if not current_user.is_admin:
        return jsonify({'error': '未授权'}), 403
    
    curl_command = request.form.get('curl_command')
    if not curl_command:
        return jsonify({'error': 'CURL命令不能为空'}), 400
    
    # 提取e2mf
    e2mf_match = re.search(r'e2mf: ([^\s\']+)', curl_command)
    if not e2mf_match:
        return jsonify({'error': '未找到e2mf值'}), 400
    e2mf = e2mf_match.group(1)
    
    # 更新数据库
    cookie_config = CookieConfig.query.first()
    if cookie_config:
        cookie_config.e2mf = e2mf
        cookie_config.updated_at = datetime.utcnow()
    else:
        cookie_config = CookieConfig(e2mf=e2mf)
        db.session.add(cookie_config)
    
    db.session.commit()
    
    return jsonify({
        'e2mf': e2mf
    })

@app.route('/batch_upload', methods=['POST'])
def batch_upload():
    try:
        # 检查是否有上传的文件
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'message': '未找到上传的文件'}), 400
        
        file = request.files['excel_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        # 获取cookie配置
        cookie_config = CookieConfig.query.first()
        if not cookie_config:
            return jsonify({'success': False, 'message': '系统未配置Cookie'}), 500
        
        # 读取Excel文件
        try:
            # header=None 确保不会将第一行作为标题，而是作为数据
            df = pd.read_excel(io.BytesIO(file.read()), header=None)
        except Exception as e:
            return jsonify({'success': False, 'message': f'无法读取Excel文件: {str(e)}'}), 400
        
        # 验证Excel格式
        if len(df.columns) < 2:
            return jsonify({'success': False, 'message': 'Excel文件格式错误，至少需要两列：学员号和班号'}), 400
        
        # 重命名列以确保一致性 - 不再使用原始列名
        df.columns = ['student_code', 'goods_code'] + [f'column_{i}' for i in range(2, len(df.columns))]
        
        # 清理数据
        df = df.dropna(subset=['student_code', 'goods_code'])
        
        # 处理每一行
        results = []
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            student_code = str(row['student_code']).strip()
            goods_code = str(row['goods_code']).strip()
            
            # 构建请求
            url = 'https://gateway.xdf.cn/web_reg_eapi/assistCart/assistAdd'
            headers = {
                'Host': 'gateway.xdf.cn',
                'Content-Type': 'application/json',
                'Origin': 'https://xubantool.xdf.cn',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': f'U2AT=; accessToken=; appVersion=5.2.45; e2e=E9EA4CE45CFDC27561245F32249BAF1A; e2mf={cookie_config.e2mf}; email=chenzhanhong@xdf.cn; teacherCode=U0000289451; XDFUUID=489f5bb5-144d-805e-ea29-2865f2264bf0',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 XdfWoXueApp/5.2.45 XdfWoXueRia/3.5 XdfWoXueFullScreen/false XdfWoXueTeacher/5.2.45 xdfBridge/3.5 xdfAppVer/5.2.45 xdfAppName/woxue xdfAppOther/teacher',
                'Referer': f'https://xubantool.xdf.cn/purchaseStudent?appId=xdfTeacherApp&systemSource=xdfTeacher&schoolId=3&studentCode={student_code}',
                'Accept-Language': 'zh-cn'
            }
            
            request_data = {
                "marketingSources": "",
                "marketingSourcesExt": "",
                "systemSource": "xdfTeacher",
                "appId": "xdfTeacherApp",
                "agentName": "",
                "schoolId": "3",
                "list": [{
                    "goodsCode": goods_code,
                    "goodsType": 1,
                    "students": [{
                        "studentCode": student_code,
                        "userId": "xdf006889962"
                    }]
                }]
            }
            
            try:
                response = requests.post(url, json=request_data, headers=headers)
                response_data = response.json()
                
                result = {
                    'student_code': student_code,
                    'goods_code': goods_code,
                    'success': response_data.get('code') == 10000,
                    'message': response_data.get('message', '成功') if response_data.get('code') == 10000 else response_data.get('message', '未知错误')
                }
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                
                results.append(result)
            except Exception as e:
                results.append({
                    'student_code': student_code,
                    'goods_code': goods_code,
                    'success': False,
                    'message': f'请求异常: {str(e)}'
                })
                error_count += 1
        
        # 返回处理结果
        return jsonify({
            'success': True,
            'message': f'批量处理完成，成功: {success_count}，失败: {error_count}',
            'details': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'处理Excel文件时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 