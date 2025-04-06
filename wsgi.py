from app import app
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保这个变量名是 application
application = app

# 记录WSGI启动信息
logger.info("WSGI应用程序已初始化")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))