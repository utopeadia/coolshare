# 使用 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 暴露 Flask 应用端口
EXPOSE 5000

RUN pip install flask
RUN pip install gunicorn
RUN pip install flask_sqlalchemy

# 设置启动命令, 假设 app.py 中 Flask app 实例名为 app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
