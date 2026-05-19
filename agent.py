# agent.py
import requests
import urllib.parse

def browser_agent_search(query: str) -> dict:
    """
    自主 AI Agent：透過 Wikipedia 官方 API 進行結構化全文檢索，100% 免疫防爬蟲
    """
    print(f"🕵️ 知識庫未命中！AI Agent 啟動維基百科 API 檢索: {query}")
    
    # 對中文或帶空格的關鍵字進行網址編碼（URL Encoding）
    encoded_query = urllib.parse.quote(query)
    
    # 📌 使用維基百科官方的 opensearch API，這能根據關鍵字模糊搜尋最相關的條目
    api_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded_query}&limit=3&namespace=0&format=json"
    
    try:
        # 發送請求，並加上標準的 User-Agent 宣告我們是學術研發測試
        headers = {"User-Agent": "RAG-Agent-Demo/1.0 (contact: your-email@example.com)"}
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Wikipedia OpenSearch 回傳格式為: [原查詢詞, [標題列表], [摘要列表], [連結列表]]
            titles = data[1]
            descriptions = data[2]
            links = data[3]
            
            if titles and descriptions:
                # 📌 整合前 2 個最相關條目的摘要當作上下文
                context_list = []
                for i in range(min(2, len(titles))):
                    context_list.append(f"【條目：{titles[i]}】\n摘要：{descriptions[i]}")
                
                scraped_text = "\n\n".join(context_list)
                source_url = links[0] if links else f"https://en.wikipedia.org/wiki/{encoded_query}"
                status = "success"
            else:
                scraped_text = "NOT_FOUND"
                source_url = f"https://en.wikipedia.org/wiki/{encoded_query}"
                status = "failed"
        else:
            scraped_text = "NOT_FOUND"
            source_url = f"https://en.wikipedia.org/wiki/{encoded_query}"
            status = "failed"
            
    except Exception as e:
        scraped_text = f"Agent API 檢索出錯: {str(e)}"
        source_url = "內網錯誤"
        status = "error"
        
    return {
        "agent_status": status,
        "target_query": query,
        "extracted_text": scraped_text,
        "source_url": source_url
    }