import math

# ==========================================
# 1. 16タイプの理想座標（セントロイド）マスタ
# ==========================================
CENTROIDS = {
    "VP-SA": {"name": "VP-SA (破壊と創造/システム/自律)", "f": 1.0, "p": 1.0, "s": 1.0, "v": 1.0},
    "VP-SC": {"name": "VP-SC (破壊と創造/システム/貢献)", "f": 1.0, "p": 1.0, "s": 1.0, "v": -1.0},
    "VP-HA": {"name": "VP-HA (破壊と創造/対人/自律)",    "f": -1.0, "p": 1.0, "s": 1.0, "v": 1.0},
    "VP-HC": {"name": "VP-HC (破壊と創造/対人/貢献)",    "f": -1.0, "p": 1.0, "s": 1.0, "v": -1.0},
    "VB-SA": {"name": "VB-SA (構想と設計/システム/自律)", "f": 1.0, "p": 1.0, "s": -1.0, "v": 1.0},
    "VB-SC": {"name": "VB-SC (構想と設計/システム/貢献)", "f": 1.0, "p": 1.0, "s": -1.0, "v": -1.0},
    "VB-HA": {"name": "VB-HA (構想と設計/対人/自律)",    "f": -1.0, "p": 1.0, "s": -1.0, "v": 1.0},
    "VB-HC": {"name": "VB-HC (構想と設計/対人/貢献)",    "f": -1.0, "p": 1.0, "s": -1.0, "v": -1.0},
    "EP-SA": {"name": "EP-SA (現場と適応/システム/自律)", "f": 1.0, "p": -1.0, "s": 1.0, "v": 1.0},
    "EP-SC": {"name": "EP-SC (現場と適応/システム/貢献)", "f": 1.0, "p": -1.0, "s": 1.0, "v": -1.0},
    "EP-HA": {"name": "EP-HA (現場と適応/対人/自律)",    "f": -1.0, "p": -1.0, "s": 1.0, "v": 1.0},
    "EP-HC": {"name": "EP-HC (現場と適応/対人/貢献)",    "f": -1.0, "p": -1.0, "s": 1.0, "v": -1.0},
    "EB-SA": {"name": "EB-SA (秩序と安定/システム/自律)", "f": 1.0, "p": -1.0, "s": -1.0, "v": 1.0},
    "EB-SC": {"name": "EB-SC (秩序と安定/システム/貢献)", "f": 1.0, "p": -1.0, "s": -1.0, "v": -1.0},
    "EB-HA": {"name": "EB-HA (秩序と安定/対人/自律)",    "f": -1.0, "p": -1.0, "s": -1.0, "v": 1.0},
    "EB-HC": {"name": "EB-HC (秩序と安定/対人/貢献)",    "f": -1.0, "p": -1.0, "s": -1.0, "v": -1.0},
}

# ==========================================
# 2. 質問マスタデータ（全110問のマッピング定義）
# ==========================================
# axis: 'f'(Focus), 'p'(Perception), 's'(Strategy), 'v'(Value), 
#       'risk'(リスク許容度), 'resilience'(情動耐性), 'battery'(社会的バッテリー)
QUESTION_MASTER = {
    # --- 認識軸 (Perception) ---
    1:  {"axis": "p", "direction": 1, "weight": 1.5},
    2:  {"axis": "p", "direction": 1, "weight": 1.5},
    3:  {"axis": "p", "direction": 1, "weight": 1.5},
    4:  {"axis": "p", "direction": 1, "weight": 1.5},
    5:  {"axis": "p", "direction": 1, "weight": 1.5},
    6:  {"axis": "p", "direction": 1, "weight": 1.5},
    7:  {"axis": "p", "direction": 1, "weight": 1.5},
    8:  {"axis": "p", "direction": 1, "weight": 1.5},
    9:  {"axis": "p", "direction": 1, "weight": 1.5},
    10: {"axis": "p", "direction": 1, "weight": 1.5},
    11: {"axis": "p", "direction": 1, "weight": 1.0},
    12: {"axis": "p", "direction": 1, "weight": 1.0},
    13: {"axis": "p", "direction": 1, "weight": 1.0},
    14: {"axis": "p", "direction": 1, "weight": 1.0},
    15: {"axis": "p", "direction": 1, "weight": 1.0},
    16: {"axis": "p", "direction": 1, "weight": 1.0},
    17: {"axis": "p", "direction": 1, "weight": 1.0},
    18: {"axis": "p", "direction": 1, "weight": 1.0},
    19: {"axis": "p", "direction": 1, "weight": 1.0},
    20: {"axis": "p", "direction": 1, "weight": 1.0},
    # --- 戦略軸 (Strategy) ---
    21: {"axis": "s", "direction": 1, "weight": 1.5},
    22: {"axis": "s", "direction": 1, "weight": 1.5},
    23: {"axis": "s", "direction": 1, "weight": 1.5},
    24: {"axis": "s", "direction": 1, "weight": 1.5},
    25: {"axis": "s", "direction": 1, "weight": 1.5},
    26: {"axis": "s", "direction": 1, "weight": 1.5},
    27: {"axis": "s", "direction": 1, "weight": 1.5},
    28: {"axis": "s", "direction": 1, "weight": 1.5},
    29: {"axis": "s", "direction": 1, "weight": 1.5},
    30: {"axis": "s", "direction": 1, "weight": 1.5},
    31: {"axis": "s", "direction": 1, "weight": 1.0},
    32: {"axis": "s", "direction": 1, "weight": 1.0},
    33: {"axis": "s", "direction": 1, "weight": 1.0},
    34: {"axis": "s", "direction": 1, "weight": 1.0},
    35: {"axis": "s", "direction": 1, "weight": 1.0},
    36: {"axis": "s", "direction": 1, "weight": 1.0},
    37: {"axis": "s", "direction": 1, "weight": 1.0},
    38: {"axis": "s", "direction": 1, "weight": 1.0},
    39: {"axis": "s", "direction": 1, "weight": 1.0},
    40: {"axis": "s", "direction": 1, "weight": 1.0},
    # --- 価値軸 (Value) ---
    41: {"axis": "v", "direction": 1, "weight": 1.5},
    42: {"axis": "v", "direction": 1, "weight": 1.5},
    43: {"axis": "v", "direction": 1, "weight": 1.5},
    44: {"axis": "v", "direction": 1, "weight": 1.5},
    45: {"axis": "v", "direction": 1, "weight": 1.5},
    46: {"axis": "v", "direction": 1, "weight": 1.5},
    47: {"axis": "v", "direction": 1, "weight": 1.5},
    48: {"axis": "v", "direction": 1, "weight": 1.5},
    49: {"axis": "v", "direction": 1, "weight": 1.5},
    50: {"axis": "v", "direction": 1, "weight": 1.5},
    51: {"axis": "v", "direction": 1, "weight": 1.0},
    52: {"axis": "v", "direction": 1, "weight": 1.0},
    53: {"axis": "v", "direction": 1, "weight": 1.0},
    54: {"axis": "v", "direction": 1, "weight": 1.0},
    55: {"axis": "v", "direction": 1, "weight": 1.0},
    56: {"axis": "v", "direction": 1, "weight": 1.0},
    57: {"axis": "v", "direction": 1, "weight": 1.0},
    58: {"axis": "v", "direction": 1, "weight": 1.0},
    59: {"axis": "v", "direction": 1, "weight": 1.0},
    60: {"axis": "v", "direction": 1, "weight": 1.0},
    # --- 対象軸 (Focus) ---
    61: {"axis": "f", "direction": 1, "weight": 1.5},
    62: {"axis": "f", "direction": 1, "weight": 1.5},
    63: {"axis": "f", "direction": 1, "weight": 1.5},
    64: {"axis": "f", "direction": 1, "weight": 1.5},
    65: {"axis": "f", "direction": 1, "weight": 1.5},
    66: {"axis": "f", "direction": 1, "weight": 1.5},
    67: {"axis": "f", "direction": 1, "weight": 1.5},
    68: {"axis": "f", "direction": 1, "weight": 1.5},
    69: {"axis": "f", "direction": 1, "weight": 1.5},
    70: {"axis": "f", "direction": 1, "weight": 1.5},
    71: {"axis": "f", "direction": 1, "weight": 1.0},
    72: {"axis": "f", "direction": 1, "weight": 1.0},
    73: {"axis": "f", "direction": 1, "weight": 1.0},
    74: {"axis": "f", "direction": 1, "weight": 1.0},
    75: {"axis": "f", "direction": 1, "weight": 1.0},
    76: {"axis": "f", "direction": 1, "weight": 1.0},
    77: {"axis": "f", "direction": 1, "weight": 1.0},
    78: {"axis": "f", "direction": 1, "weight": 1.0},
    79: {"axis": "f", "direction": 1, "weight": 1.0},
    80: {"axis": "f", "direction": 1, "weight": 1.0},
    # --- モディファイア（隠し変数） ---
    81: {"axis": "risk", "direction": 1, "weight": 1.0},
    82: {"axis": "risk", "direction": 1, "weight": 1.0},
    83: {"axis": "risk", "direction": 1, "weight": 1.0},
    84: {"axis": "risk", "direction": 1, "weight": 1.0},
    85: {"axis": "risk", "direction": 1, "weight": 1.0},
    86: {"axis": "risk", "direction": 1, "weight": 1.0},
    87: {"axis": "risk", "direction": 1, "weight": 1.0},
    88: {"axis": "risk", "direction": 1, "weight": 1.0},
    89: {"axis": "risk", "direction": 1, "weight": 1.0},
    90: {"axis": "risk", "direction": 1, "weight": 1.0},
    91:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    92:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    93:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    94:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    95:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    96:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    97:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    98:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    99:  {"axis": "resilience", "direction": 1, "weight": 1.0},
    100: {"axis": "resilience", "direction": 1, "weight": 1.0},
    101: {"axis": "battery", "direction": -1, "weight": 1.0},
    102: {"axis": "battery", "direction": -1, "weight": 1.0},
    103: {"axis": "battery", "direction": -1, "weight": 1.0},
    104: {"axis": "battery", "direction": -1, "weight": 1.0},
    105: {"axis": "battery", "direction": -1, "weight": 1.0},
    106: {"axis": "battery", "direction": -1, "weight": 1.0},
    107: {"axis": "battery", "direction": -1, "weight": 1.0},
    108: {"axis": "battery", "direction": -1, "weight": 1.0},
    109: {"axis": "battery", "direction": -1, "weight": 1.0},
    110: {"axis": "battery", "direction": -1, "weight": 1.0},
    
    # ※ 実際にはここに1〜110問全ての定義を記述します
}

# ==========================================
# 3. 基礎計算ロジック
# ==========================================

def calculate_normalized_axis_score(answers):
    """回答リストから正規化スコア (-1.0 ~ 1.0) を算出"""
    if not answers:
        return 0.0
        
    weighted_sum = 0
    max_possible_sum = 0
    
    for item in answers:
        weighted_sum += item['answer'] * item['direction'] * item['weight']
        max_possible_sum += 3 * item['weight']
        
    return weighted_sum / max_possible_sum if max_possible_sum != 0 else 0.0

def calculate_modifier_score(answers):
    """モディファイアのスコアを 0 ~ 100% に変換"""
    normalized = calculate_normalized_axis_score(answers)
    return ((normalized + 1.0) / 2.0) * 100

def find_closest_type(user_vector):
    """ユークリッド距離による最適OSの判定"""
    min_distance = float('inf')
    closest_type_id = None
    
    for type_id, centroid in CENTROIDS.items():
        distance = math.sqrt(
            (user_vector["f"] - centroid["f"])**2 +
            (user_vector["p"] - centroid["p"])**2 +
            (user_vector["s"] - centroid["s"])**2 +
            (user_vector["v"] - centroid["v"])**2
        )
        if distance < min_distance:
            min_distance = distance
            closest_type_id = type_id
            
    return closest_type_id, min_distance

# ==========================================
# 4. API連携用 統合ラッパー関数
# ==========================================

def run_full_diagnosis(raw_answers):
    """
    フロントエンドからの生データを受け取り、全計算を一括で実行して結果辞書を返す。
    raw_answers 例: [{'q_id': 1, 'value': 3}, {'q_id': 2, 'value': -1}, ...]
    """
    
    # 軸ごとの回答を振り分けるバケツを用意
    categorized = {
        'f': [], 'p': [], 's': [], 'v': [],
        'risk': [], 'resilience': [], 'battery': []
    }
    
    # 1. ユーザーの回答をマスタデータと照合してバケツに仕分ける
    for ans in raw_answers:
        q_id = ans.get('q_id')
        if q_id in QUESTION_MASTER:
            master = QUESTION_MASTER[q_id]
            axis = master['axis']
            
            categorized[axis].append({
                'answer': ans['value'],
                'direction': master['direction'],
                'weight': master['weight']
            })

    # 2. 4つのOSコアベクトルの計算
    vectors = {
        "f": calculate_normalized_axis_score(categorized['f']),
        "p": calculate_normalized_axis_score(categorized['p']),
        "s": calculate_normalized_axis_score(categorized['s']),
        "v": calculate_normalized_axis_score(categorized['v'])
    }
    
    # 3. 最適タイプの判定
    result_type_id, distance = find_closest_type(vectors)
    
    # 4. モディファイア（隠し変数）の計算
    modifiers = {
        "risk": calculate_modifier_score(categorized['risk']),
        "resilience": calculate_modifier_score(categorized['resilience']),
        "battery": calculate_modifier_score(categorized['battery'])
    }
    
    # 5. routes.py で扱いやすい形式にパックして返す
    return {
        "type": result_type_id,
        "full_name": CENTROIDS[result_type_id]["name"],
        "distance": distance,
        "vectors": vectors,
        "modifiers": modifiers
    }