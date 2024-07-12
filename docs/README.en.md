<p align="center">
<img src="../assets/logo.png" alt="coolshare" width="200">
</p>
<h1 align="center">
  CoolShare
</h1>

<p align="center">
 <a href="docs/README.en.md">English</a> | <a href="README.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/utopeadia/coolshare/blob/main/LICENSE"><img src="../assets/GPL-3.0License.svg" alt="License"></a>
  <a><img src="../assets/PRs-welcome-brightgreen.svg"/></a>
</p>

`CoolShare` is a very lightweight and easy-to-use code snippet sharing tool, aiming to build a platform for personal and team internal code collaboration and sharing through fast means.

### Features

20240622 Update

* Ready to Use
* Simple and lightweight (using Flask may not be lightweight, but it will be simple) `</br>`
  Project directory as follows:
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

### Docker Deployment Method

* Expose Port 5000
* Persist /app/coolshare.db Database (optional)
* Configure environment variables (optional)

Example：

```bash
docker run -d --name coolshare --restart always -p 5000:5000 ghcr.io/utopeadia/coolshare:latest
```

```bash
docker run -d --name coolshare --restart always -p 5000:5000 -v ~/coolshare/coolshare.db:/app/coolshare.db ghcr.io/utopeadia/coolshare:latest
```

```bash
docker run -d --name coolshare --restart always -p 5000:5000 -v ~/coolshare/coolshare.db:/app/coolshare.db -e MAX_SHARE_TIME=100 ghcr.io/utopeadia/coolshare:latest
```

### Environment variables description

| Environment variable name | Environment variable explanation                                                                                               | Is it necessary |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| MAX_SHARE_TIME            | Maximum sharing time, default value 4320, unit minutes                                                                         | false           |
| REQUEST_LIMIT             | Limits the total number of creations and deletions within the time window, with a default value of 24.                         | false           |
| TIME_WINDOW               | Time window, default value 60, unit seconds                                                                                    | false           |
| CLEANUP_INTERVAL_MINUTES  | Execute IP counter and database cleanup tasks on a schedule, default value 30, unit minute                                     | false           |
| PENALTY_DURATION          | The basic penalty duration, each time exceeding the limit, the penalty duration will be doubled, default value 5, unit minutes | false           |
| MAX_CACHE_SIZE            | Counter maximum cache value, default value 1000                                                                                | false           |

![](../assets/index.png)
![](../assets/share.png)
![](../assets/view.png)
![](../assets/404.png)

## ~Under development, not yet available~ Initially usable.

## License Agreement

[GPL](LICENSE): This project is open-sourced under the **GPLv3** license.
