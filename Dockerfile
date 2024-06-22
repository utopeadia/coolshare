# 使用 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露 Flask 应用端口
EXPOSE 5000

# 设置启动命令, 假设 app.py 中 Flask app 实例名为 app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
