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
|变量名|说明|是否必须|
|-|-|-|
|MAX_SHARE_TIME|最长分享时间，默认值4320，单位分钟|false|
|REQUEST_LIMIT|时间窗口内限制创建和删除总数量，默认值20|false|
|TIME_WINDOW|时间窗口，默认值60，单位秒|false|
|CLEANUP_INTERVAL_MINUTES|执行ip计数清理任务定时，默认值30，单位分钟|false|
|PENALTY_DURATION|超过请求限制罚时，默认值5，单位分钟|false|


![1719061304782](assets/1719061304782.png)
![1719061332849](assets/1719061332849.png)
![1719061384535](assets/1719061384535.png)
![1719061402241](assets/1719061402241.png)
![1719061415916](assets/1719061415916.png)
![1719061427768](assets/1719061427768.png)

## ~Under development, not yet available~ 初步可用

## **开源许可证**

本项目采用 **MIT 许可证**，并附加以下条款：

**附加条款：**

任何基于本软件进行的二次开发，无论是商业用途还是非商业用途，都必须在以下位置明确标注原项目的名称、作者以及本许可证的链接：

* **软件的显著位置:** 例如软件的启动界面、关于页面、设置页面等。
* **相关文档:** 包括但不限于 README 文件、用户手册、技术文档等。
  **示例：**

```
本软件基于 [原项目名称] ([链接]) 开发，原作者为 [作者姓名]。
```
