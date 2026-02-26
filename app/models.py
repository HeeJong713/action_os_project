from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# SQLAlchemyのインスタンスを作成
db = SQLAlchemy()

# ==========================================
# 1. 診断結果テーブル (assessments)
# ==========================================
class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(64), nullable=False, index=True) # 検索を高速化するためにindexを付与
    
    # OS判定結果
    result_type = db.Column(db.String(10), nullable=False) # 例: "VB-SC"
    distance = db.Column(db.Float, nullable=False)         # ユークリッド距離
    
    # 4次元ベクトル（正規化スコア -1.0 ~ 1.0）
    vector_f = db.Column(db.Float, nullable=False)
    vector_p = db.Column(db.Float, nullable=False)
    vector_s = db.Column(db.Float, nullable=False)
    vector_v = db.Column(db.Float, nullable=False)
    
    # モディファイア（隠し変数 0.0 ~ 100.0）
    mod_risk = db.Column(db.Float, nullable=False)
    mod_resilience = db.Column(db.Float, nullable=False)
    mod_battery = db.Column(db.Float, nullable=False)
    
    # タイムスタンプ
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーションシップ（1対多の関係を定義）
    # Assessmentオブジェクトから紐づくResponsesを簡単に取得できるようにする
    responses = db.relationship('Response', backref='assessment', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment {self.id} - Type: {self.result_type}>"


# ==========================================
# 2. 回答詳細テーブル (responses)
# ==========================================
class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外部キー（どの診断結果に紐づくか）
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False, index=True)
    
    # 質問番号と回答
    question_id = db.Column(db.Integer, nullable=False)
    answer_value = db.Column(db.Integer, nullable=False) # -3 から +3

    def __repr__(self):
        return f"<Response Q{self.question_id}: {self.answer_value}>"