# Telos-Scale: 詳細技術ドキュメント

## 1. プロジェクト概要

**Telos-Scale** は、シンプルな自律AIエージェントが大量の試行を実行し、結果を共有することで集合知を進化させるOSSプラットフォームです。

### 核心哲学

- **シンプルさ**: 300行以下のコア実装
- **スケール**: 並列実行と分散共有による指数関数的成長
- **オープン性**: 誰でも貢献できるコミュニティ駆動モデル

### 従来版Telosとの違い

|特徴|Telos (従来)|Telos-Scale|
|---|---|---|
|アーキテクチャ|複数コンポーネント (Orchestrator, GoalGenerator, InstinctEngine等)|単一クラス `TelosScale`|
|評価メカニズム|InstinctEngine (4本能シグナル)|LLMによる直接評価 + 共有知識|
|設定|階層化 (config.yaml, telos.yaml, 環境変数)|環境変数のみ|
|共有機能|なし|オプションの共有レイヤー|
|デプロイ|Docker + Qdrant + SQLite|Dockerのみ (オプションで共有サーバー)|

## 2. アーキテクチャ

### システム全体図

```
[User]
  │
  ├─ telos-scale run --loops 100 --workers 5
  │     │
  │     ▼
  │   TelosScaleクラス (core.py)
  │     ├─ 1. コンテキスト取得 (ローカル + 共有メモリ)
  │     ├─ 2. 目標生成 (LLM)
  │     ├─ 3. サンドボックス実行
  │     ├─ 4. 結果記録
  │     └─ 5. 共有アップロード (オプション)
  │
  └─ telos-scale share --enable
        │
        ▼
    共有サーバー (オプション)
        ├─ POST /api/upload
        └─ GET /api/search?q=...
```

### コンポーネント詳細

#### 2.1 TelosScaleクラス (core.py)

```python
class TelosScale:
    """メインオーケストレーター - 300行以下を目標"""
    
    def __init__(self, 
                 shared_url: Optional[str] = None,
                 model: str = "gemini/gemini-flash-latest"):
        self.memory = LocalMemory()          # 過去試行のローカル記録
        self.shared = SharedClient(shared_url) if shared_url else None
        self.sandbox = DockerSandbox()       # Dockerサンドボックス
        self.llm = LLMClient(model)          # litellm経由のLLM
        
    def run_loop(self) -> Dict[str, Any]:
        """単一ループ実行"""
        # 1. コンテキスト取得
        context = self._get_context(num_examples=3)
        
        # 2. 目標生成
        goal = self._generate_goal(context)
        
        # 3. サンドボックス実行
        result = self._execute_goal(goal)
        
        # 4. 記録
        self._record(goal, result)
        
        # 5. 共有 (オプション)
        if self.shared:
            self.shared.upload(goal, result)
            
        return {"goal": goal, "result": result}
    
    def _get_context(self, num_examples: int) -> List[Dict]:
        """過去試行からコンテキストを構築"""
        local = self.memory.get_recent(num_examples)
        if self.shared:
            shared = self.shared.search(query="", limit=num_examples)
            return local + shared
        return local
```

#### 2.2 DockerSandboxクラス

```python
class DockerSandbox:
    """安全なコード実行環境"""
    
    def __init__(self, 
                 image: str = "python:3.11-slim",
                 memory_limit: str = "512m"):
        self.image = image
        self.memory_limit = memory_limit
        self.container = None
        
    def start(self):
        """コンテナ起動"""
        # Docker SDKでコンテナ作成
        # ワークスペースボリュームをマウント
        
    def execute_command(self, cmd: str) -> Tuple[int, str]:
        """コマンド実行と結果取得"""
        
    def read_file(self, path: str) -> str:
        """コンテナ内ファイル読み取り"""
        
    def write_file(self, path: str, content: str):
        """コンテナ内ファイル書き込み"""
        
    def stop(self, cleanup: bool = False):
        """コンテナ停止"""
```

#### 2.3 SharedClientクラス

```python
class SharedClient:
    """共有サーバーとの通信クライアント"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        
    def upload(self, goal: str, result: str, metadata: Dict = None):
        """試行結果を共有サーバーにアップロード"""
        payload = {
            "goal": goal,
            "result": result,
            "embedding": self._generate_embedding(result),
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        requests.post(f"{self.base_url}/api/upload", json=payload)
        
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """類似試行を検索"""
        response = requests.get(
            f"{self.base_url}/api/search",
            params={"q": query, "limit": limit}
        )
        return response.json()
```

#### 2.4 LocalMemoryクラス

```python
class LocalMemory:
    """シンプルなローカル記憶"""
    
    def __init__(self, max_size: int = 1000):
        self.memory = []  # (goal, result, timestamp) のリスト
        self.max_size = max_size
        
    def add(self, goal: str, result: str):
        self.memory.append({
            "goal": goal,
            "result": result,
            "timestamp": time.time()
        })
        if len(self.memory) > self.max_size:
            self.memory.pop(0)  # FIFO
            
    def get_recent(self, n: int) -> List[Dict]:
        return self.memory[-n:] if self.memory else []
```

## 3. インストールとセットアップ

### 3.1 必要条件

- **Docker** 20.10以上
- **Python** 3.11以上
- **OpenRouter APIキー** (または他のLLMプロバイダーキー)

### 3.2 クイックインストール

```bash
# 1. リポジトリクローン
git clone https://github.com/telos-scale/telos-scale.git
cd telos-scale

# 2. 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 依存関係インストール
pip install -r requirements.txt
# requirements.txt:
# litellm==1.0.0
# requests==2.31.0
# docker==6.1.0

# 4. 環境変数設定
echo "OPENROUTER_API_KEY=sk-or-..." > .env
# または
export OPENROUTER_API_KEY="sk-or-..."

# 5. Dockerの起動 (バックグラウンドで実行中であることを確認)
docker --version
```

### 3.3 ワンライナーインストール (デモ用)

```bash
curl -s https://telos.scale/install.sh | bash
# スクリプト内容:
# 1. DockerとPythonの存在確認
# 2. リポジトリクローン
# 3. 仮想環境設定
# 4. サンプルAPIキーでのテスト実行 (10ループ)
```

## 4. 使用方法

### 4.1 基本的な実行

```bash
# 10ループを逐次実行
telos-scale run --loops 10

# 5ワーカーで並列実行 (合計100ループ)
telos-scale run --loops 100 --workers 5

# 共有モードで実行 (結果を自動アップロード)
telos-scale run --loops 50 --share --shared-url https://api.telos.scale

# 特定のモデルを使用
telos-scale run --loops 20 --model "openrouter/deepseek/deepseek-chat-v3-0324"
```

### 4.2 コマンドリファレンス

```bash
# メインコマンド
telos-scale run [OPTIONS]

# オプション
--loops INTEGER          実行するループ数 (デフォルト: 10)
--workers INTEGER        並列ワーカー数 (デフォルト: 1)
--model TEXT             LLMモデル (デフォルト: "gemini/gemini-flash-latest")
--share                  共有モードを有効化
--shared-url TEXT        共有サーバーURL (デフォルト: https://api.telos.scale)
--output-dir TEXT        結果出力ディレクトリ (デフォルト: ./results)
--cost-limit FLOAT       最大コスト制限 (USD) (デフォルト: 10.0)
--verbose                詳細ログ出力

# ユーティリティコマンド
telos-scale status        現在の実行状況を表示
telos-scale list          過去の試行を一覧表示
telos-scale export        JSON形式で結果をエクスポート
telos-scale dashboard     ウェブダッシュボードを起動
```

### 4.3 プログラムによる使用

```python
from telos_scale import TelosScale

# 基本設定
agent = TelosScale()

# 単一ループ実行
result = agent.run_loop()
print(f"Goal: {result['goal']}")
print(f"Result: {result['result']}")

# バッチ実行
for i in range(100):
    print(f"Loop {i+1}/100")
    agent.run_loop()
    
# 共有モードで実行
shared_agent = TelosScale(
    shared_url="https://api.telos.scale",
    model="gemini/gemini-flash-latest"
)
```

## 5. 設定システム

### 5.1 環境変数

すべての設定は環境変数で制御されます：

```bash
# LLM設定
export OPENROUTER_API_KEY="sk-or-..."          # OpenRouterキー
export TELOS_MODEL="gemini/gemini-flash-latest" # デフォルトモデル
export TELOS_MAX_TOKENS="8000"                 # ループあたり最大トークン数

# サンドボックス設定
export TELOS_DOCKER_IMAGE="python:3.11-slim"   # サンドボックスイメージ
export TELOS_MEMORY_LIMIT="512m"               # コンテナメモリ制限
export TELOS_TIMEOUT="300"                     # コマンドタイムアウト(秒)

# 共有設定
export TELOS_SHARED_URL="https://api.telos.scale" # 共有サーバーURL
export TELOS_SHARED_API_KEY="..."               # 共有サーバーAPIキー(オプション)
export TELOS_SHARE_ENABLED="true"               # 共有を有効化

# 実行制限
export TELOS_COST_LIMIT="10.0"                  # 最大コスト(USD)
export TELOS_DAILY_LOOPS="1000"                 # 1日あたり最大ループ数
```

### 5.2 設定の優先順位

1. コマンドライン引数 (最高優先度)
2. 環境変数
3. デフォルト値

## 6. 共有プロトコル仕様

### 6.1 データ形式

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "goal": "Create a Python script that scrapes Hacker News",
  "result": "成功: scraped 100 posts. Code: ...",
  "embedding": [0.12, -0.45, 0.78, ...],  // 384次元ベクトル
  "metadata": {
    "model": "gemini/gemini-flash-latest",
    "tokens_used": 2200,
    "execution_time_ms": 4500,
    "user_hash": "a1b2c3d4",  // 匿名化ユーザーID
    "cost_usd": 0.001175,
    "tags": ["web-scraping", "python", "success"]
  },
  "timestamp": "2026-03-27T15:30:00Z"
}
```

### 6.2 APIエンドポイント

#### POST /api/upload

試行結果をアップロード

**リクエスト**:

```json
{
  "goal": "目標テキスト",
  "result": "結果テキスト",
  "embedding": [数値配列],  // オプション
  "metadata": {}  // オプション
}
```

**レスポンス**:

```json
{
  "success": true,
  "id": "アップロードID",
  "message": "Upload successful"
}
```

#### GET /api/search

類似試行を検索

**クエリパラメータ**:

- `q`: 検索クエリ (テキスト)
- `limit`: 返却数 (デフォルト: 5)
- `threshold`: 類似度閾値 (0.0-1.0, デフォルト: 0.7)

**レスポンス**:

```json
{
  "results": [
    {
      "id": "結果ID",
      "goal": "目標",
      "result": "結果",
      "similarity": 0.85,
      "metadata": {}
    }
  ]
}
```

### 6.3 セキュリティとプライバシー

- **匿名化**: ユーザーは自動生成ハッシュIDで識別
- **オプトイン**: 共有は明示的に有効化する必要あり
- **データ最小化**: APIキー、個人情報は一切収集しない
- **GDPR対応**: データ削除リクエストをサポート

## 7. 並列実行アーキテクチャ

### 7.1 ワーカーモデル

```
メインプロセス (Coordinator)
  ├─ ワーカー1 (子プロセス) → TelosScaleインスタンス1
  ├─ ワーカー2 (子プロセス) → TelosScaleインスタンス2
  ├─ ワーカー3 (子プロセス) → TelosScaleインスタンス3
  └─ 共有メモリキュー (Redis/メモリ内)
```

### 7.2 実装例

```python
from multiprocessing import Pool

def run_worker(worker_id: int, loops: int):
    """個別ワーカーの実行関数"""
    agent = TelosScale()
    for i in range(loops):
        result = agent.run_loop()
        print(f"Worker {worker_id}: Loop {i} completed")
    return worker_id

# 5ワーカーで100ループを実行 (各20ループ)
with Pool(processes=5) as pool:
    results = pool.starmap(run_worker, [(i, 20) for i in range(5)])
```

### 7.3 リソース管理

- **Dockerコンテナの分離**: 各ワーカーが独立したコンテナを使用
- **APIレート制限**: プロバイダーごとに適切なスロットリング
- **コスト追跡**: リアルタイムでコストを監視、制限を超えたら停止

## 8. デモと可視化

### 8.1 リアルタイムダッシュボード

```bash
# ダッシュボード起動
telos-scale dashboard

# ブラウザで http://localhost:8050 を開く
```

**ダッシュボード機能**:

- 現在実行中のループのリアルタイム表示
- 累積コストと試行回数のグラフ
- 生成されたコードのプレビュー
- 共有知識ベースの可視化

### 8.2 デモスクリプト

```bash
# デモモードで実行 (自動で可視化を開始)
telos-scale demo --duration 3600  # 1時間実行

# デモ結果をHTMLレポートとして出力
telos-scale demo --output report.html
```

## 9. 開発者ガイド

### 9.1 プロジェクト構造

```
telos-scale/
├── core.py              # メインクラス (300行以下を目標)
├── cli.py               # コマンドラインインターフェース
├── sandbox.py           # Dockerサンドボックス実装
├── shared.py            # 共有クライアント実装
├── memory.py            # ローカルメモリ実装
├── llm.py               # LLMクライアントラッパー
├── utils.py             # ユーティリティ関数
├── requirements.txt     # 依存関係
├── Dockerfile.sandbox   # サンドボックス用Dockerfile
├── docker-compose.yml   # 開発環境用
├── tests/               # テストスイート
├── docs/                # ドキュメント
└── examples/            # 使用例
```

### 9.2 拡張ポイント

1. **新しいツールの追加**: `sandbox.py` にメソッドを追加
2. **カスタムメモリバックエンド**: `memory.py` のインターフェースを実装
3. **代替LLMプロバイダー**: `llm.py` で対応
4. **カスタム可視化**: ダッシュボードテンプレートを拡張

### 9.3 テスト

```bash
# ユニットテスト
pytest tests/ -v

# 統合テスト (Dockerが必要)
pytest tests/integration/ -v

# コストテスト (実際のAPIを呼び出す)
pytest tests/cost_test.py --run-costly
```

## 10. 貢献ガイド

### 10.1 開発フロー

1. **Issue作成**: バグ報告や機能提案
2. **ブランチ作成**: `feature/新しい機能` または `fix/バグ修正`
3. **プルリクエスト**: テストを含む変更を提出
4. **コードレビュー**: メンテナーによるレビュー
5. **マージ**: マージ後、自動デプロイ

### 10.2 コーディング規約

- **シンプルさ**: 複雑さを避け、直感的な実装を
- **型ヒント**: Python 3.11+ の型ヒントを使用
- **テストカバレッジ**: 80%以上のカバレッジを目標
- **ドキュメント**: 公開APIにはdocstringを記載

## 11. ロードマップ

### フェーズ1: コア実装 (v0.1)

- [ ] 300行以下の `TelosScale` クラス実装
- [ ] 基本的なCLIインターフェース
- [ ] 単一ループ実行のテスト
- [ ] シンプルなデモスクリプト

### フェーズ2: スケーリング (v0.2)

- [ ] 並列実行サポート
- [ ] 共有プロトコルの実装
- [ ] コスト追跡と制限
- [ ] 基本的なダッシュボード

### フェーズ3: コミュニティ (v0.3)

- [ ] 公開共有サーバーの立ち上げ
- [ ] 貢献者インセンティブプログラム
- [ ] プラグインシステム
- [ ] 詳細な可視化ツール

### フェーズ4: プラットフォーム (v1.0)

- [ ] 分散実行ネットワーク
- [ ] クロスインスタンス知識交換
- [ ] 企業向け機能
- [ ] 研究機関向け連携機能

## 12. ライセンスとクレジット

**ライセンス**: MIT License

**クレジット**:

- 元々のTelosプロジェクトの貢献者
- OpenRouterなどのLLMプロバイダー
- Dockerコンテナ技術
- 貢献者コミュニティ

---

**Telos-Scale** は、シンプルさを維持しながらスケールすることで、人類全体のAI進化を加速することを目指しています。このドキュメントはプロジェクトの方向性と実装の詳細を示すものです。実際の実装では、シンプルさを最優先し、必要最小限の機能から始めることを推奨します。




---