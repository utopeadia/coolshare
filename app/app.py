import os
import random
import string
import base64
import time
import threading
from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict, defaultdict
from functools import wraps
from datetime import datetime, timedelta, timezone

MAX_SHARE_TIME = float(os.environ.get("MAX_SHARE_TIME", 4320))
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "coolshare.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 限速参数
REQUEST_LIMIT = int(os.environ.get("REQUEST_LIMIT", 24))  # 每分钟允许的请求次数
TIME_WINDOW = float(os.environ.get("TIME_WINDOW", 60))  # 时间窗口（秒）
# 设置内存回收参数
CLEANUP_INTERVAL_MINUTES = int(
    os.environ.get("CLEANUP_INTERVAL_MINUTES", 30)
)  # 内存清理间隔（分钟）
PENALTY_DURATION = int(os.environ.get("PENALTY_DURATION", 5))  # 惩罚持续时间（分钟）
MAX_CACHE_SIZE = int(os.environ.get("MAX_CACHE_SIZE", 1000))  # 设置最大缓存大小

# 使用 defaultdict 和 threading.Lock 实现线程安全的限速数据存储
rate_limit_data = defaultdict(lambda: {"count": 0, "last_reset": 0})
rate_limit_lock = threading.Lock()


def rate_limit(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        ip_address = request.remote_addr
        current_time = time.time()

        with rate_limit_lock:
            data = rate_limit_data[ip_address]

            # 检查是否处于惩罚状态, 修正判断条件
            if data["last_reset"] >= current_time:
                remaining_penalty = int(data["last_reset"] - current_time)
                abort(
                    429,
                    description=f"Too Many Requests. Try again in {remaining_penalty} seconds.",
                )

            # 如果是第一次请求或者超过时间窗口，重置计数
            if current_time - data["last_reset"] > TIME_WINDOW:
                data["count"] = 0
                data["last_reset"] = current_time

            # 检查请求次数是否超过限制
            if data["count"] >= REQUEST_LIMIT:
                # 指数退避算法
                penalty_duration = PENALTY_DURATION * (
                    2 ** (data["count"] - REQUEST_LIMIT)
                )
                data["last_reset"] = current_time + penalty_duration
                remaining_penalty = int(data["last_reset"] - current_time)
                abort(
                    429,
                    description=f"Too Many Requests. Try again in {remaining_penalty} seconds. "
                    f"Your penalty duration will increase exponentially with repeated violations.",
                )

            # 更新访问记录
            data["count"] += 1

        return func(*args, **kwargs)

    return decorated_function


def cleanup_rate_limit_data():
    global rate_limit_data
    while True:
        current_time = time.time()
        with rate_limit_lock:
            for ip_address, data in list(rate_limit_data.items()):
                if current_time - data["last_reset"] > TIME_WINDOW * 2:
                    del rate_limit_data[ip_address]
        time.sleep(CLEANUP_INTERVAL_MINUTES * 60)


# 在单独的线程中启动清理任务
cleanup_thread = threading.Thread(target=cleanup_rate_limit_data)
cleanup_thread.daemon = True  # 设置为守护线程
cleanup_thread.start()


class CodeShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    share_code = db.Column(db.String(6), unique=True, nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)


def generate_share_code():
    while True:
        code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        if not CodeShare.query.filter_by(share_code=code).first():
            return code


def cleanup_expired_shares():
    while True:
        with app.app_context():
            current_time = datetime.now(timezone.utc)
            expired_shares = CodeShare.query.filter(
                CodeShare.expiration_time < current_time
            ).all()
            for share in expired_shares:
                db.session.delete(share)
            db.session.commit()
        time.sleep(CLEANUP_INTERVAL_MINUTES * 60)


# 在单独的线程中启动清理任务
cleanup_thread = threading.Thread(target=cleanup_expired_shares)
cleanup_thread.daemon = True  # 设置为守护线程
cleanup_thread.start()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/share", methods=["POST"])
@rate_limit
def share_code():
    data = request.json
    code_content = data.get("code")
    custom_code = data.get("customCode")
    share_time = data.get("shareTime")

    if not code_content or not share_time:
        return jsonify({"error": "缺少必要参数"}), 400

    try:
        share_time = int(share_time)
        if share_time <= 0 or share_time > MAX_SHARE_TIME:
            return (
                jsonify({"error": f"分享时间必须在 1 到 {MAX_SHARE_TIME} 分钟之间"}),
                400,
            )
    except ValueError:
        return jsonify({"error": "无效的分享时间"}), 400

    share_code = custom_code if custom_code else generate_share_code()

    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=share_time)

    new_share = CodeShare(
        share_code=share_code,
        code_content=code_content,
        expiration_time=expiration_time,
    )
    db.session.add(new_share)
    db.session.commit()

    return jsonify({"share_code": share_code})


@app.route("/<share_code>", methods=["GET"])
def view_code(share_code):
    share = CodeShare.query.filter_by(share_code=share_code).first()

    if not share:
        return render_template("404.html"), 404

    expiration_time_aware = share.expiration_time.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expiration_time_aware:
        db.session.delete(share)
        db.session.commit()
        abort(404)

    expiration_timestamp_ms = int(expiration_time_aware.timestamp() * 1000)
    code_base64 = base64.b64encode(share.code_content.encode("utf-8")).decode("utf-8")
    return render_template(
        "view.html", code_base64=code_base64, expiration_time=expiration_timestamp_ms
    )


@app.route("/destroy", methods=["POST"])
@rate_limit
def destroy_code():
    data = request.json
    share_code = data.get("share_code")

    if not share_code:
        return jsonify({"error": "缺少分享码"}), 400

    share = CodeShare.query.filter_by(share_code=share_code).first()

    if not share:
        return jsonify({"error": "找不到对应的分享"}), 404

    try:
        db.session.delete(share)
        db.session.commit()
        return jsonify({"message": "分享已成功销毁"})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error destroying share {share_code}: {str(e)}")
        return jsonify({"error": "销毁过程中发生错误"}), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
