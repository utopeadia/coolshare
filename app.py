import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

MAXSHARE = int(os.environ.get('MAXSHARE', 100))

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

db_path = os.path.join(data_dir, 'codes.db')
if not os.path.exists(db_path):
    open(db_path, 'a').close()

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.environ.get('SECRETKEY', 'yoursession')

class CodeSnippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    share_code = db.Column(db.String(10), unique=True, nullable=False)
    code = db.Column(db.Text, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

class ShareLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class DeleteLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/share', methods=['POST'])
def share():
    data = request.json
    code = data.get('code')
    custom_code = data.get('customCode')
    custom_time = data.get('customTime')

    ip_address = request.remote_addr

    one_minute_ago = datetime.now() - timedelta(minutes=1)
    with app.app_context():
        share_count = ShareLog.query.filter(
            ShareLog.ip_address == ip_address,
            ShareLog.timestamp >= one_minute_ago
        ).count()

        if share_count >= MAXSHARE:
            return jsonify({'error': '分享过于频繁，请稍后再试'}), 429

        if custom_code:
            share_code = custom_code
        else:
            share_code = generate_code()

        if custom_time:
            expire_time = int(custom_time)
        else:
            expire_time = 5

        if expire_time > 28800:
            return jsonify({'error': '自定义时间不能超过48小时'}), 400

        expire_at = datetime.now() + timedelta(minutes=expire_time)
        new_snippet = CodeSnippet(share_code=share_code, code=code, expire_at=expire_at)

        db.session.add(new_snippet)
        new_log = ShareLog(ip_address=ip_address)
        db.session.add(new_log)

        db.session.commit()

    return jsonify({'share_code': share_code})

@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.json
    share_code = data.get('share_code')
    with app.app_context():
        snippet = CodeSnippet.query.filter_by(share_code=share_code).first()
        if snippet and snippet.expire_at > datetime.now():
            return jsonify({'code': snippet.code})
        else:
            return jsonify({'error': '无效的分享码或代码片段已过期'}), 404

@app.route('/destroy', methods=['POST'])
def destroy():
    data = request.json
    share_code = data.get('share_code')

    ip_address = request.remote_addr

    five_minutes_ago = datetime.now() - timedelta(minutes=5)
    with app.app_context():
        delete_count = DeleteLog.query.filter(
            DeleteLog.ip_address == ip_address,
            DeleteLog.timestamp >= five_minutes_ago
        ).count()

        if delete_count >= 3:
            return jsonify({'error': '操作过于频繁，请稍后再试'}), 429

        snippet = CodeSnippet.query.filter_by(share_code=share_code).first()
        if snippet:
            db.session.delete(snippet)
            new_log = DeleteLog(ip_address=ip_address)
            db.session.add(new_log)
            db.session.commit()
            return jsonify({'message': '代码片段已删除'})
        else:
            return jsonify({'error': '无效的分享码'}), 404

def delete_expired_snippets():
    with app.app_context():
        now = datetime.now()
        CodeSnippet.query.filter(CodeSnippet.expire_at < now).delete()
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_snippets, 'interval', minutes=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
