from app import app
import os

# 确保这个变量名是 application
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))