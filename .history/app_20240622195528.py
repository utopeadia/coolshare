from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime, timedelta
import sqlite3
import random
import string

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('coolshare.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shares
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  share_code TEXT UNIQUE,
                  code TEXT,
                  expiration_time DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# 生成随机分享码
def generate_share_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# 分享代码
@app.route('/share', methods=['POST'])
def share_code():
    data = request.json
    code = data.get('code')
    custom_code = data.get('customCode')
    share_time = data.get('shareTime')

    if not code or not share_time:
        return jsonify({'error': '缺少必要参数'}), 400

    share_code = custom_code if custom_code else generate_share_code()
    expiration_time = datetime.now() + timedelta(minutes=int(share_time))

    conn = sqlite3.connect('coolshare.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO shares (share_code, code, expiration_time) VALUES (?, ?, ?)",
                  (share_code, code, expiration_time))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': '自定义分享码已存在'}), 400
    finally:
        conn.close()

    return jsonify({'share_code': share_code})

# 查看代码
@app.route('/<share_code>')
def view_code(share_code):
    conn = sqlite3.connect('coolshare.db')
    c = conn.cursor()
    c.execute("SELECT code, expiration_time FROM shares WHERE share_code = ?", (share_code,))
    result = c.fetchone()
    conn.close()

    if result is None:
        abort(404)

    code, expiration_time = result
    expiration_time = datetime.strptime(expiration_time, '%Y-%m-%d %H:%M:%S.%f')

    if datetime.now() > expiration_time:
        # 删除过期的分享
        conn = sqlite3.connect('coolshare.db')
        c = conn.cursor()
        c.execute("DELETE FROM shares WHERE share_code = ?", (share_code,))
        conn.commit()
        conn.close()
        abort(404)

    return render_template('view.html', code=code, expiration_time=expiration_time.isoformat())

# 销毁代码
@app.route('/destroy', methods=['POST'])
def destroy_code():
    data = request.json
    share_code = data.get('share_code')

    if not share_code:
        return jsonify({'error': '缺少分享码'}), 400

    conn = sqlite3.connect('coolshare.db')
    c = conn.cursor()
    c.execute("DELETE FROM shares WHERE share_code = ?", (share_code,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()

    if deleted:
        return jsonify({'message': '代码已成功销毁'})
    else:
        return jsonify({'error': '未找到对应的分享码'}), 404

# 定期清理过期的分享
def cleanup_expired_shares():
    conn = sqlite3.connect('coolshare.db')
    c = conn.cursor()
    c.execute("DELETE FROM shares WHERE expiration_time < ?", (datetime.now(),))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_expired_shares, 'interval', minutes=5)
    scheduler.start()

    app.run(debug=True)