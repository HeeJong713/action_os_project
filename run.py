from app import create_app

# create_app関数を呼び出してアプリケーションを構築
app = create_app()

if __name__ == '__main__':
    # debug=True にすることで、コードを書き換えた際に自動でサーバーがリロードされます
    app.run(host='0.0.0.0', port=5000, debug=True)