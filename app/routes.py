from flask import request, jsonify, render_template, current_app as app
from .models import db, Assessment, Response
# calculator.pyから必要な関数をインポート（※後述のラッパー関数を想定）
from .calculator import run_full_diagnosis 

# ==========================================
# 1. ページ遷移（HTMLレンダリング）のエンドポイント
# ==========================================

@app.route('/', methods=['GET'])
def index():
    """トップページ（診断開始画面）"""
    return render_template('index.html')

@app.route('/quiz', methods=['GET'])
def quiz():
    """110問の診断実行ページ"""
    return render_template('quiz.html')

@app.route('/result', methods=['GET'])
def result():
    """診断結果表示ページ"""
    # URLパラメータから assessment_id を取得 (?id=123)
    assessment_id = request.args.get('id', type=int)
    
    if not assessment_id:
        return "エラー：結果IDが指定されていません", 400
        
    # データベースから診断結果を取得
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # result.htmlにデータを渡してレンダリング
    return render_template('result.html', assessment=assessment)


# ==========================================
# 2. APIエンドポイント（データ受信・計算・保存）
# ==========================================

@app.route('/api/diagnose', methods=['POST'])
def api_diagnose():
    """フロントエンドから回答を受け取り、計算してDBに保存する"""
    data = request.json
    
    session_id = data.get('session_id')
    raw_answers = data.get('answers', []) # [{'q_id': 1, 'value': 3}, ...]
    
    if not session_id or not raw_answers:
        return jsonify({"status": "error", "message": "データが不足しています"}), 400

    try:
        # ------------------------------------------------
        # A. 計算エンジンを呼び出してOSとモディファイアを算出
        # ------------------------------------------------
        # ※ run_full_diagnosisは、raw_answersを受け取って全ての計算を行う想定の関数
        diagnosis_result = run_full_diagnosis(raw_answers)
        
        # ------------------------------------------------
        # B. データベース保存処理（トランザクション）
        # ------------------------------------------------
        # 1. 診断結果サマリー (Assessment) を作成
        new_assessment = Assessment(
            session_id=session_id,
            result_type=diagnosis_result['type'],
            distance=diagnosis_result['distance'],
            vector_f=diagnosis_result['vectors']['f'],
            vector_p=diagnosis_result['vectors']['p'],
            vector_s=diagnosis_result['vectors']['s'],
            vector_v=diagnosis_result['vectors']['v'],
            mod_risk=diagnosis_result['modifiers']['risk'],
            mod_resilience=diagnosis_result['modifiers']['resilience'],
            mod_battery=diagnosis_result['modifiers']['battery']
        )
        
        db.session.add(new_assessment)
        db.session.flush() # IDを発行させるために一旦flush
        
        # 2. 110問の生データ (Response) を作成
        responses_to_insert = []
        for ans in raw_answers:
            responses_to_insert.append(Response(
                assessment_id=new_assessment.id,
                question_id=ans['q_id'],
                answer_value=ans['value']
            ))
            
        # bulk_save_objectsで一括INSERT（高速処理）
        db.session.bulk_save_objects(responses_to_insert)
        
        # 3. コミットして確定
        db.session.commit()
        
        # ------------------------------------------------
        # C. フロントエンドへ成功レスポンスを返す
        # ------------------------------------------------
        return jsonify({
            "status": "success", 
            "assessment_id": new_assessment.id
        }), 200

    except Exception as e:
        db.session.rollback() # エラー時はDBを元に戻す
        app.logger.error(f"Diagnosis Error: {str(e)}")
        return jsonify({"status": "error", "message": "診断処理中にエラーが発生しました"}), 500