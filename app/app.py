from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from functools import wraps
from threading import Timer
import time
from datetime import datetime, timedelta, timezone
import random
import string
import base64
import os

MAX_SHARE_TIME = float(os.environ.get("MAX_SHARE_TIME"))
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "coolshare.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 限速参数
REQUEST_LIMIT = int(os.environ.get("REQUEST_LIMIT"))  # 每分钟允许的请求次数
TIME_WINDOW = float(os.environ.get("TIME_WINDOW"))  # 时间窗口（秒）
# 设置内存回收参数
CLEANUP_INTERVAL_MINUTES = int(
    os.environ.get("CLEANUP_INTERVAL_MINUTES")
)  # 内存清理间隔（分钟）
PENALTY_DURATION = int(os.environ.get("PENALTY_DURATION"))  # 惩罚持续时间（分钟）


rate_limit_data = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
rate_limit_lock = Lock()


def rate_limit(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        ip_address = request.remote_addr
        current_time = time.time()

        with rate_limit_lock:  # 使用锁保护对共享数据的访问
            # 获取该IP的访问记录
            data = rate_limit_data[ip_address]

            # 检查是否处于惩罚状态
            if data["last_reset"] > current_time:
                remaining_penalty = int(data["last_reset"] - current_time)
                abort(
                    429,
                    description=f"Too Many Requests. Try again in {remaining_penalty} seconds.",
                )

            # 如果超过时间窗口，重置计数
            if current_time - data["last_reset"] > TIME_WINDOW:
                data["count"] = 0
                data["last_reset"] = current_time

            # 检查请求次数是否超过限制
            if data["count"] >= REQUEST_LIMIT:
                data["last_reset"] = current_time + (PENALTY_DURATION * 60)
                abort(
                    429,
                    description=f"Too Many Requests. You have been rate limited for {PENALTY_DURATION} minutes.",
                )

            # 更新访问记录
            data["count"] += 1

        return func(*args, **kwargs)

    return decorated_function


#  全局计时器
cleanup_timer = None


def cleanup_rate_limit_data():
    global rate_limit_data, cleanup_timer
    current_time = time.time()

    with rate_limit_lock:
        for ip_address, data in list(rate_limit_data.items()):
            # 清理过期记录，包括惩罚状态的记录
            if current_time - data["last_reset"] > TIME_WINDOW * 2:
                del rate_limit_data[ip_address]

    # 设置定时任务，将分钟转换为秒
    cleanup_timer = Timer(CLEANUP_INTERVAL_MINUTES * 60, cleanup_rate_limit_data)
    cleanup_timer.start()


# 启动时启动清理任务
cleanup_rate_limit_data()


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


@app.errorhandler(429)
def ratelimit_handler(e):
    return (
        jsonify(
            {
                "error": "操作超限，请稍后再试",
                "retry-after": e.description.split("in ")[1],
            }
        ),
        429,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
