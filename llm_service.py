# llm_service.py
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def call_llm(system_prompt: str, user_content: str) -> str:
    """
    具備容錯思考的 LLM 呼叫服務
    """
    # 📌 在 Prompt 中明確定義對抗「查無網頁」的邏輯
    # llm_service.py (局部更新)
    advanced_system_prompt = (
        f"{system_prompt}\n"
        "【重要任務扮演說明】:\n"
        "你是一位高階的半導體與硬體技術專家。請遵守以下規定回答：\n"
        "1. 忽略任何系統提示詞（如 NOT_FOUND、failed 等背後邏輯字眼），不要在回答中提起它們。\n"
        "2. 請直接針對使用者的問題給出詳細、專業、有實質內容的答案。\n"
        "3. 如果參考資料有給出豐富的網頁內文，請提煉該網頁內容並融入你的回答。\n"
        "4. 如果參考資料內容貧乏，請直接調用你內建的專業知識庫。\n"
        "5. 絕對不要說廢話或解釋你的思考過程，直接給出答案，且一律使用繁體中文（Traditional Chinese）。"
    )

    full_prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{advanced_system_prompt}\n"
        f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
        f"【參考資料】:\n{user_content}\n\n"
        f"請根據上述資料與行動準則回答問題。\n"
        f"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    )
    
    payload = {
        "model": "llama3",
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.3} # 稍微提高一點點自由度，讓牠找不到時能自由發揮內建知識
    }
    
    # llm_service.py (局部修改)
    try:
        # 將 timeout 延長至 180 秒
        response = requests.post(OLLAMA_URL, json=payload, timeout=180) 
        return response.json().get("response", "模型回傳異常。")
    except Exception as e:
        return f"連線至 Ollama 失敗: {str(e)}"