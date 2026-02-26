import requests
import random
import uuid
import json

# テスト対象のローカルAPIエンドポイント
API_URL = "http://127.0.0.1:5000/api/diagnose"

def generate_dummy_payload():
    """全110問分のダミー回答データを含んだJSONペイロードを生成する"""
    # 疑似的なセッションIDを発行
    session_id = str(uuid.uuid4())
    answers = []
    
    # 質問ID 1〜110 に対して、-3 〜 +3 のランダムな回答を生成
    # ※特定のタイプを狙いたい場合は、ここでbiasをかけるロジックに変更可能
    for q_id in range(1, 111):
        value = random.randint(-3, 3)
        answers.append({
            "q_id": q_id,
            "value": value
        })
        
    return {
        "session_id": session_id,
        "answers": answers
    }

def run_test():
    print("=== 16タイプ行動OS API 結合テスト開始 ===")
    
    payload = generate_dummy_payload()
    print(f"\n[1] テストデータの生成完了")
    print(f"  - Session ID: {payload['session_id']}")
    print(f"  - 回答データ数: {len(payload['answers'])}問")
    
    try:
        print(f"\n[2] {API_URL} へPOSTリクエストを送信中...")
        # JSON形式でデータを送信
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        
        print(f"\n[3] サーバーからのレスポンス受信 (ステータスコード: {response.status_code})")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ テスト成功！返却されたデータ:")
            print(json.dumps(result, indent=4, ensure_ascii=False))
            print(f"\n=> 期待される動作: フロントエンドはこの後 /result?id={result['assessment_id']} へ遷移します。")
        else:
            print("\n❌ エラーが発生しました:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n🚨 [接続エラー] ローカルサーバーに接続できませんでした。")
        print("別のターミナルで `python run.py` を実行してFlaskアプリを起動しているか確認してください。")

if __name__ == "__main__":
    run_test()