from flask import request, jsonify, render_template, current_app as app
from .models import db, Assessment, Response
from .calculator import run_full_diagnosis 

# ==========================================
# テキスト動的生成ロジック
# ==========================================
def generate_os_description(os_type):
    """ 'VP-SA' などの文字列から、理論に基づいた解説テキストを動的に生成する """
    engine = os_type[:2] # 最初の2文字 (VP, VB, EP, EB)
    focus = os_type[3]   # 4文字目 (S, H)
    value = os_type[4]   # 5文字目 (A, C)

    # 1. コアエンジンの特性
    engines = {
        "VP": {"title": "破壊と創造のイノベーター", "desc": "直感と試行錯誤を武器に、ゼロからイチを生み出す圧倒的な推進力を持っています。前例のないカオスな状況で最もパフォーマンスを発揮します。"},
        "VB": {"title": "構想と設計のアーキテクト", "desc": "未来のビジョンを強固な構造やロードマップに落とし込む天才です。抽象的なアイデアを、実行可能なシステムへと翻訳します。"},
        "EP": {"title": "現場と適応のリアリスト", "desc": "現実のフィードバックを即座に吸収し、柔軟に改善を繰り返す現場のプロフェッショナルです。変化の激しい環境で素早く適応します。"},
        "EB": {"title": "秩序と安定のガーディアン", "desc": "確かな証拠に基づき、システムの信頼性と規律を守り抜きます。組織の基盤を支え、致命的なリスクを未然に防ぐ要となります。"}
    }

    # 2. 対象軸と価値軸の組み合わせ
    focus_text = "「論理・データ・仕組み」の構築や最適化" if focus == "S" else "「人々の感情・モチベーション・関係性」の調整"
    value_text = "高い専門性を発揮し、自己の裁量で自由に動ける環境" if value == "A" else "他者と協調し、組織や社会全体の調和に貢献できる環境"

    return {
        "title": engines[engine]["title"],
        "core_desc": engines[engine]["desc"],
        "target": f"あなたの関心は主に{focus_text}に向けられており、{value_text}において根源的なモチベーション（Why）が満たされます。"
    }

def generate_modifier_advice(risk, resilience, battery):
    """ 隠し変数のスコアからアドバイスを生成する """
    advice = {}
    advice['risk'] = "ハイリスク・ハイリターンな環境（ベンチャー等）への適性が高いです。" if risk >= 60 else "安定したリソースと予測可能な環境で最大の成果を出します。" if risk <= 40 else "適度な裁量とセーフティネットが両立する環境が適しています。"
    advice['resilience'] = "厳しい批判やカオスな状況でも心が折れにくい強靭なメンタルです。" if resilience >= 60 else "心理的安全性が高く、建設的なフィードバックが得られる文化が必要です。" if resilience <= 40 else "標準的な耐性ですが、定期的なガス抜きは必要です。"
    advice['battery'] = "チームでの議論や対人交流によってエネルギーを充電できるタイプです。" if battery >= 60 else "非同期コミュニケーションを多用し、一人で深く集中できる「聖域」が必須です。" if battery <= 40 else "対面とソロワークのハイブリッド環境が最もバランス良く働けます。"
    return advice

# ==========================================
# 1. ページ遷移（HTMLレンダリング）のエンドポイント
# ==========================================

@app.route('/', methods=['GET'])
def index():
    """トップページ（診断開始画面）"""
    return render_template('index.html')

@app.route('/quiz', methods=['GET'])
def quiz():
    """診断実行ページ"""
    return render_template('quiz.html')

@app.route('/result', methods=['GET'])
def result():
    """診断結果表示ページ"""
    assessment_id = request.args.get('id', type=int)
    
    if not assessment_id:
        return "エラー：結果IDが指定されていません", 400
        
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # ここで動的にテキストを生成
    os_info = generate_os_description(assessment.result_type)
    advices = generate_modifier_advice(assessment.mod_risk, assessment.mod_resilience, assessment.mod_battery)
    
    # result.htmlに全てのデータを渡してレンダリング
    return render_template('result.html', assessment=assessment, os_info=os_info, advices=advices)


# ==========================================
# 2. APIエンドポイント（データ受信・計算・保存）
# ==========================================

@app.route('/api/diagnose', methods=['POST'])
def api_diagnose():
    """フロントエンドから回答を受け取り、計算してDBに保存する"""
    data = request.json
    
    session_id = data.get('session_id')
    raw_answers = data.get('answers', [])
    
    if not session_id or not raw_answers:
        return jsonify({"status": "error", "message": "データが不足しています"}), 400

    try:
        # A. 計算エンジンを呼び出してOSとモディファイアを算出
        diagnosis_result = run_full_diagnosis(raw_answers)
        
        # B. データベース保存処理（トランザクション）
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
        db.session.flush() 
        
        responses_to_insert = []
        for ans in raw_answers:
            responses_to_insert.append(Response(
                assessment_id=new_assessment.id,
                question_id=ans['q_id'],
                answer_value=ans['value']
            ))
            
        db.session.bulk_save_objects(responses_to_insert)
        db.session.commit()
        
        # C. フロントエンドへ成功レスポンスを返す
        return jsonify({
            "status": "success", 
            "assessment_id": new_assessment.id
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Diagnosis Error: {str(e)}")
        return jsonify({"status": "error", "message": "診断処理中にエラーが発生しました"}), 500