import requests
import json
import time

# APIリクエストを送信
start_id = 10000
end_id = 474020
step = 10

for i in range((end_id - start_id) // step):
    forecast_id = start_id + step * i
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{forecast_id}.json"
    
    try:
        response = requests.get(url)
        
        # ステータスコードを確認
        if response.status_code == 200:
            data = response.json()  # JSONデータをパース
            print(f"ID: {forecast_id}")
            print(json.dumps(data, indent=2, ensure_ascii=False))  # 整形して表示
        else:
            print(f"Error {response.status_code} for ID: {forecast_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed for ID: {forecast_id}. Error: {e}")
    
    time.sleep(1)  # APIの負荷軽減のため、1秒間隔を空ける
