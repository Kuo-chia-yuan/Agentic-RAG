# main.py
import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any

# 匯入我們前面寫好的模組
from agent import browser_agent_search
from llm_service import call_llm

app = FastAPI(
    title="Dynamic Agent RAG API",
    description="本地端 RAG 知識庫檢索與 AI Agent 雙核心動態調度系統",
    version="2.0.0"
)

# 讀取地端切塊數據
def load_rag_database():
    try:
        with open("data/processed/knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 定義 API 輸出契約
class AskResponse(BaseModel):
    mode: str          # "RAG_LOCAL" 或 "AGENT_WEB_BROWSER"
    answer: str        # LLM 整合後的最終回答
    references: Any    # 參考的本地 Chunks 或是 Agent 抓到的網頁 JSON

@app.get("/ask", response_model=AskResponse, summary="動態智能問答接口")
def ask_question(q: str = Query(..., description="請輸入你想查詢的技術問題或關鍵字")):
    """
    執行雙核心動態調度邏輯：
    1. 檢索本地端 RAG 知識庫
    2. 若命中 -> 直接調用 LLM 生成回答
    3. 若未命中 -> 觸發 Playwright 瀏覽器 Agent 上網，將結果轉為 JSON 後再交給 LLM 整合回答
    """
    rag_data = load_rag_database()
    
    # 執行本地關鍵字比對
    matched_chunks = [item for item in rag_data if q.lower() in item["content"].lower()]
    
    # ---- 分流邏輯 1：本地 RAG 命中 ----
    if matched_chunks:
        mode = "RAG_LOCAL"
        # 提取 Chunks 內容當作上下文
        context = "\n".join([f"來源[{c['source']}]: {c['content']}" for c in matched_chunks])
        system_prompt = "你是一個地端技術文件專家，請嚴謹地根據提供的文件內容回答問題。"
        
        # 呼叫 LLM
        answer = call_llm(system_prompt, context)
        return AskResponse(mode=mode, answer=answer, references=matched_chunks)
        
    # ---- 分流邏輯 2：本地 RAG 未命中，啟動瀏覽器 AI Agent ----
    else:
        mode = "AGENT_WEB_BROWSER"
        # 啟動 Playwright 執行網頁任務自動化並回傳結構化 JSON
        agent_json = browser_agent_search(q)
        
        system_prompt = "你是一個配備了網路瀏覽器的 AI 代理人。請將隨附的網頁監測 JSON 數據進行語意提煉，給予使用者最即時、精準的整合報告。"
        context_str = f"Agent 狀態: {agent_json['agent_status']}\n網頁文字抓取結果: {agent_json['extracted_text']}"
        
        # 呼叫 LLM 整合回答
        answer = call_llm(system_prompt, context_str)
        return AskResponse(mode=mode, answer=answer, references=agent_json)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py:app", host="127.0.0.1", port=8000, reload=True)