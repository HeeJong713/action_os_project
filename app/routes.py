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
    
# ==========================================
# 3. 深堀ページ（タイプ別詳細データベース）のエンドポイント
# ==========================================

def get_detailed_os_info(os_type):
    """ 指定されたOSタイプの詳細な強み、弱み、相性、組織での役割を生成する """
    engine = os_type[:2] # VP, VB, EP, EB
    focus = os_type[3]   # S, H
    value = os_type[4]   # A, C
    
    # 1. 組織階層におけるポジションと役割
    roles = {
        "VP": {"position": "Top (意思決定・ゼロイチ創出)", "role_desc": "前例のない課題に対して直感とスピードで切り込み、新しいシステムや市場の種を生み出す突破口の役割を担います。"},
        "VB": {"position": "Supporter A (戦略の翻訳・設計)", "role_desc": "Topが描いた抽象的なビジョンを、中長期的なロードマップや強固な構造へと翻訳し、実現可能な計画に落とし込みます。"},
        "EP": {"position": "Supporter B (現場の適応・改善)", "role_desc": "計画通りに進まない現場の摩擦やエラーを即座に検知し、柔軟な試行錯誤でシステムをチューニングし続けます。"},
        "EB": {"position": "Bottom (実装・遂行・防衛)", "role_desc": "確立された計画と実証データに基づき、確実かつ正確に業務を遂行し、組織の土台と信頼性を守り抜きます。"}
    }
    
    # 2. 強みと弱み（武器とボトルネック）
    strengths_weaknesses = {
        "VP": {"s": ["圧倒的なゼロイチ推進力", "未知の領域への恐怖の欠如", "本質を見抜く直感"], "w": ["ルーティンワークへの極度な嫌悪", "細部の詰めの甘さ", "周囲を置いてけぼりにするスピード"]},
        "VB": {"s": ["未来を構造化する構想力", "破綻のないシステム設計", "長期的なリスクヘッジ"], "w": ["実行に移すまでの遅さ", "想定外のトラブルへの硬直", "完璧主義によるリソース浪費"]},
        "EP": {"s": ["現場のリアルな課題解決力", "変化に対する高い適応性", "実用的なツールのハック"], "w": ["長期的なビジョンの欠如", "場当たり的な対応になりがち", "理論や体系化の軽視"]},
        "EB": {"s": ["ミスを許さない正確な遂行力", "既存システムの安定稼働", "データに基づく堅実な判断"], "w": ["前例のない事象へのフリーズ", "過度な保守性と変化への抵抗", "直感的なアイデアへの拒絶"]}
    }

    # 3. 相性（インピーダンス整合）のアルゴリズム計算
    # 相性の良い翻訳者（エンジンが隣接しているタイプ）
    translator_engine = "VB" if engine == "VP" else "EP" if engine == "EB" else "VP" if engine == "VB" else "EB"
    # 対極のタイプ（エンジンが完全に逆）
    opposite_engine = "EB" if engine == "VP" else "VP" if engine == "EB" else "EP" if engine == "VB" else "VB"

    return {
        "type_id": os_type,
        "role": roles[engine],
        "sw": strengths_weaknesses[engine],
        "matches": {
            "translator": f"{translator_engine}-{focus}{value}",
            "translator_desc": "あなたの言語を理解し、次の階層へ翻訳してくれる最高のパートナーです。",
            "opposite": f"{opposite_engine}-{focus}{value}",
            "opposite_desc": "思考プロセスが真逆であるため、直接やり取りするとインピーダンス（摩擦）が最大化しますが、間を繋ぐ人がいれば強力な補完関係になります。"
        }
    }

@app.route('/type/<os_id>', methods=['GET'])
def type_detail(os_id):
    """ 指定されたOSの詳細解説ページを表示する """
    # 存在するタイプかどうかの簡易バリデーション
    valid_engines = ['VP', 'VB', 'EP', 'EB']
    valid_focus = ['S', 'H']
    valid_value = ['A', 'C']
    
    if len(os_id) != 5 or os_id[:2] not in valid_engines or os_id[2] != '-' or os_id[3] not in valid_focus or os_id[4] not in valid_value:
        return "存在しないOSタイプです", 404

    # 既存の generate_os_description (概要) と新しい get_detailed_os_info (詳細) を合体させる
    basic_info = generate_os_description(os_id)
    detailed_info = get_detailed_os_info(os_id)
    
    return render_template('type_detail.html', basic=basic_info, detail=detailed_info)