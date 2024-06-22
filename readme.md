## ~Under development, not yet available~
## 也许现在可以使用了
20240622更新
只需要暴露5000端口即可
如果需要持久化只需要持久化sqlite db文件即可
例如：
```bash
docker run -d --name coolshare --restart always -p 5000:5000 -v ~/coolshare/coolshare.db:/app/coolshare.db ghcr.io/utopeadia/coolshare:latest
```