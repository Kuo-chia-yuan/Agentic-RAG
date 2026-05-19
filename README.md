# Agentic RAG System with Local LLM

基於 **FastAPI** 構建動態調度 RAG 系統。本專案具備動態 Routing 機制，能自動評估本地知識庫的命中率，並在未命中時自主喚醒網絡 API Agent 進行瀏覽器 Real-Time 檢索，最後交由本地端大語言模型（Ollama Llama3）進行推論，達成 100% 資料去識別化與隱私閉環。

---

## 🚀 核心技術亮點 (Key Features)

* **動態智能 Routing：** 系統會自動對輸入的 Query 進行本地知識庫檢索，若關鍵字命中率達標則啟用 `RAG_LOCAL` 模式；若查無資料則自動路由至 `AGENT_WEB_BROWSER` 模式。
* **Robust API Agent：** 整合維基百科官方結構化 OpenSearch API 作為網絡檢索層，100% 免疫公網搜尋引擎（如 DuckDuckGo/Google）對無頭瀏覽器（Headless）的動態防爬蟲與驗證碼（Cloudflare 牆）限制。
* **本地端隱私 Inference：** 後端對接 **Ollama** 引擎（支援 Llama3 / Gemma），所有生成式回答皆在本地端硬體完成推論，防止敏感技術文件（如晶片規格書）外洩。
* **高 Scannability 後端設計：** 採用 FastAPI 異步管線，內建 Swagger UI，方便進行即時接口測試。

---

## 🛠️ 架構與檔案結構 (Project Structure)

```text
DYNAMIC-AGENT-RAG/
├── data/               # 本地知識庫原始文件與切塊數據
├── .venv/              # Python 獨立虛擬環境 (Git 已忽略)
├── agent.py            # 自主網絡 Agent (封裝 Wikipedia 結構化檢索)
├── ingest.py           # 知識庫管道 (Data Ingestion Pipeline)
├── llm_service.py      # 本地大模型推論服務 (Ollama API 對接)
├── main.py             # FastAPI 主程式、路由入口與邏輯分流
├── make_data.py        # 模擬技術規格書 PDF 生成腳本
└── .gitignore          # Git 忽略配置
```

## 📦 快速開始 (Quick Start)

### 1. 環境初始化與套件安裝
請確保使用 Python 3.10+ 環境，並在專案根目錄執行：

```bash
# 建立並啟動虛擬環境
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 安裝核心依賴套件
pip install fastapi uvicorn pydantic fpdf2 python-pptx pypdf aiofiles requests
```
### 2. 啟動本地端大語言模型引擎
本專案依賴 Ollama 運行本地模型，請確保已下載安裝 Ollama 客戶端並於後台運行：

```bash
# 拉取並啟動 Llama3 8B 模型 (亦可選擇輕量化的 gemma:2b)
ollama run llama3
```

### 3. 生成模擬數據與知識庫優化

```bash
python make_data.py  # 建立模擬晶片技術規格書 specs.pdf
python ingest.py     # 進行滑動視窗切塊處理並載入 RAG 緩存
```

### 4. 運行 FastAPI 後端服務
```bash
python -m uvicorn main:app --reload
```
服務啟動後，請於瀏覽器打開 http://127.0.0.1:8000/docs 進入 Swagger UI 進行接口測試。

## 🔍 API 測試情境範例 (Verification)

### 情境 A：本地知識庫命中 (`RAG_LOCAL`)
* **測試輸入 (Query):** `RD-AI-2026`
* **系統行為：** 系統檢測到本地 PDF 存在該晶片型號，精確抓取 `specs.pdf_chunk_0`，LLM 根據規格書內容（如工作電壓 0.8V - 1.2V）輸出繁體中文技術摘要。
* **預期模式：** `mode` 欄位回傳 `"RAG_LOCAL"`。
* <img width="2484" height="440" alt="image" src="https://github.com/user-attachments/assets/97a68324-1959-407d-a558-0052c7503b23" />

### 情境 B：全網即時知識調度 (`AGENT_WEB_BROWSER`)
* **測試輸入 (Query):** `Andy`
* **系統行為：** 本地知識庫未命中，觸發智能分流，Agent 調用 Wikipedia API 撈取網絡即時結構化上下文，LLM 自動過濾垃圾提示並轉化為專業報告。
* **預期模式：** `mode` 欄位回傳 `"AGENT_WEB_BROWSER"`。
* <img width="2482" height="384" alt="image" src="https://github.com/user-attachments/assets/183cfc01-534e-4c54-b932-074029c3f411" />
