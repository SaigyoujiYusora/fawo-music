# MaiChart Music Import Assistant

## 快速启动

双击运行 `start_servers.bat` 文件即可一键启动前后端服务器。

## 服务器信息

- **前端应用**: http://127.0.0.1:3000 (会自动在浏览器中打开)
- **后端API**: http://127.0.0.1:8000

## 手动启动

如果需要手动启动：

```bash
# 后端 (需要先安装依赖: pip install -r requirements.txt)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端 (新终端)
python -m http.server 3000
```

## 依赖要求

- Python 3.7+
- 已安装 requirements.txt 中的依赖

## 注意事项

- 确保 MaiChartManager servlet 在端口 5001 上运行
- bat 文件会自动停止所有相关进程