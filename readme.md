<p align="center">
<img src="assets/logo.png" alt="coolshare" width="200">
</p>

## CoolShare--非常轻量级、非常酷的代码片段共享工具

### 特性

20240622更新</br>

* 开箱即用
* 简单轻量（使用了flask或许也不轻量）</br>
  项目目录如下：</br>
  ```
  │  
  ├──app/
  │   ├── app.py
  │   ├── templates/
  │   │   ├── index.html
  │   │   ├── view.html
  │   ├── static/
  │   │   ├── style.css
  │   │   ├── script.js
  ├──readme.md
  ├──requirements.txt
  ├──Dockerfile
  ```
* 部署方便

### docker部署方法

只需要暴露5000端口即可</br>
如果需要持久化只需要持久化sqlite db文件即可</br>
例如：</br>

```bash
docker run -d --name coolshare --restart always -p 5000:5000 -v ~/coolshare/coolshare.db:/app/coolshare.db ghcr.io/utopeadia/coolshare:latest
```

### 环境变量说明

| 变量名                   | 说明                                                          | 是否必须 |
| ------------------------ | ------------------------------------------------------------- | -------- |
| MAX_SHARE_TIME           | 最长分享时间，默认值4320，单位分钟                            | false    |
| REQUEST_LIMIT            | 时间窗口内限制创建和删除总数量，默认值24                      | false    |
| TIME_WINDOW              | 时间窗口，默认值60，单位秒                                    | false    |
| CLEANUP_INTERVAL_MINUTES | 执行ip计数清理任务定时，默认值30，单位分钟                    | false    |
| PENALTY_DURATION         | 基础的惩罚时长，每次超过限制，惩罚时长翻倍，默认值5，单位分钟 | false    |
| MAX_CACHE_SIZE           | 计数器最大缓存值，默认值1000                                  | false    |

![](assets/index.png)
![](assets/share.png)
![](assets/view.png)
![](assets/404.png)

## ~Under development, not yet available~ 初步可用

## 许可协议
[GPL](LICENSE):本项目采用 **GPLv3**协议开源

