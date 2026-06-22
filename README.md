# 平海干饭🐎 · 国库知识答题助手

一键自动答题，粘贴链接 → 自动匹配答案 → 提交

## 本地运行
```bash
pip install flask gunicorn requests
python cloud_app.py
```

## 部署到 Render（免费）
1. Fork 本仓库
2. 注册 https://render.com
3. New → Web Service → 连接仓库
4. Build: `pip install -r requirements.txt`
5. Start: `gunicorn cloud_app:app --bind 0.0.0.0:$PORT`
6. 部署后获得公网链接，所有人可用
