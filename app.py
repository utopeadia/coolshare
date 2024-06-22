from flask import Flask, request, jsonify, render_template, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coolshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CodeShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    share_code = db.Column(db.String(6), unique=True, nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)

def generate_share_code():
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not CodeShare.query.filter_by(share_code=code).first():
            return code

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/share', methods=['POST'])
def share_code():
    data = request.json
    code_content = data.get('code')
    custom_code = data.get('customCode')
    share_time = data.get('shareTime')

    if not code_content or not share_time:
        return jsonify({'error': '缺少必要参数'}), 400

    share_code = custom_code if custom_code else generate_share_code()
    expiration_time = datetime.utcnow() + timedelta(minutes=int(share_time))

    new_share = CodeShare(share_code=share_code, code_content=code_content, expiration_time=expiration_time)
    db.session.add(new_share)
    db.session.commit()

    return jsonify({'share_code': share_code})

@app.route('/<share_code>', methods=['GET'])
def view_code(share_code):
    share = CodeShare.query.filter_by(share_code=share_code).first()
    
    if not share:
        abort(404)
    
    if datetime.utcnow() > share.expiration_time:
        db.session.delete(share)
        db.session.commit()
        abort(404)
    
    return render_template('view.html', code=share.code_content, expiration_time=share.expiration_time)

@app.route('/destroy', methods=['POST'])
def destroy_code():
    data = request.json
    share_code = data.get('share_code')

    if not share_code:
        return jsonify({'error': '缺少分享码'}), 400

    share = CodeShare.query.filter_by(share_code=share_code).first()

    if not share:
        return jsonify({'error': '找不到对应的分享'}), 404

    db.session.delete(share)
    db.session.commit()

    return jsonify({'message': '分享已成功销毁'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)