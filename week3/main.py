import flet as ft
import requests
import json
import sqlite3

# SQLiteデータベースに接続（なければ作成される）
conn = sqlite3.connect('weather_forecast.db')
cursor = conn.cursor()

# 予報データを格納するテーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_name TEXT,
    weather TEXT,
    wind TEXT,
    wave TEXT,
    pops TEXT,
    temperature TEXT,
    report_datetime TEXT,
    publishing_office TEXT
)
''')

conn.commit()

def save_forecast_to_db(forecast_data):
    # SQLiteデータベースに接続
    conn = sqlite3.connect('weather_forecast.db')
    cursor = conn.cursor()

    for entry in forecast_data:
        publishing_office = entry.get("publishingOffice", "不明")
        report_datetime = entry.get("reportDatetime", "不明")

        for time_series in entry.get("timeSeries", []):
            for area in time_series.get("areas", []):
                area_name = area.get("area", {}).get("name", "不明")
                weather = area.get("weathers", ["情報なし"])[0]
                wind = area.get("winds", ["情報なし"])[0]
                wave = area.get("waves", ["情報なし"])[0] if "waves" in area else "情報なし"
                pops = area.get("pops", ["情報なし"])[0] if "pops" in area else "情報なし"
                temps = area.get("temps", ["情報なし"])[0] if "temps" in area else "情報なし"

                # データベースに挿入
                cursor.execute('''
                INSERT INTO forecasts (area_name, weather, wind, wave, pops, temperature, report_datetime, publishing_office)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (area_name, weather, wind, wave, pops, temps, report_datetime, publishing_office))

    conn.commit()
    conn.close()


def main(page: ft.Page):
    # ページを更新するためのアクション
    page.scroll = ft.ScrollMode.AUTO

    def get_forecast(e):
        area_code = dropdown.value
        print(f"Selected area_code: {area_code}")  # デバッグ出力

        if area_code:
            response = requests.get(f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json')
            print(f"API response status: {response.status_code}")  # デバッグ出力

            if response.status_code == 200:
                forecast_data = response.json()
                print("Fetched Forecast Data:")  # デバッグ出力
                print(json.dumps(forecast_data, indent=2, ensure_ascii=False))  # デバッグ出力
                display_forecast(forecast_data)

            else:
                output.value = f"Error: {response.status_code}"
                page.update()

    def display_forecast(data):
        # ページをクリアして、予報データを表示
        page.controls.clear()
        
        # 戻るボタンをページに追加
        back_button = ft.ElevatedButton(text="戻る", on_click=show_area_selection)
        page.controls.append(back_button)

        for entry in data:
            publishing_office = entry.get("publishingOffice", "不明")
            report_datetime = entry.get("reportDatetime", "不明")
            title = ft.Text(f"{publishing_office} {report_datetime}", style=ft.TextStyle(size=24, weight="bold"))
            page.controls.append(title)

            for time_series in entry.get("timeSeries", []):
                time_defines = time_series.get("timeDefines", [])

                for area in time_series.get("areas", []):
                    area_name = area.get("area", {}).get("name", "不明")
                    weather = area.get("weathers", ["情報なし"])[0]
                    wind = area.get("winds", ["情報なし"])[0]
                    wave = area.get("waves", ["情報なし"])[0] if "waves" in area else "情報なし"
                    pops = area.get("pops", ["情報なし"])[0] if "pops" in area else "情報なし"
                    temps = area.get("temps", ["情報なし"])[0] if "temps" in area else "情報なし"
                    weather_text = ft.Text(f"地域: {area_name}", style=ft.TextStyle(size=20, weight="semi-bold"))
                    weather_detail_text = ft.Text(f"天気: {weather}, 風向: {wind}, 波: {wave}, 降水確率: {pops}, 気温: {temps}")
                    page.controls.append(weather_text)
                    page.controls.append(weather_detail_text)

        print("Forecast displayed on page.")  # デバッグ出力
        page.update()

    def show_area_selection(e=None):
        # 地域選択画面を表示
        page.controls.clear()
        page_controls = [
            ft.Text("地域を選択してください："),
            dropdown
        ]
        page.controls.extend(page_controls)
        print("Area selection displayed on page.")  # デバッグ出力
        page.update()

    # areas.jsonファイルを読み込む
    with open('/Users/university/DSprograming2/week2/area.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # デバッグ用にデータをログ出力
    print("Loaded JSON data:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # ドロップダウンオプションのためのリスト
    area_options = []

    # 各セクション("centers", "offices", "class10s", "class15s", "class20s")のデータを追加
    for section in ["offices", "class10s", "class15s", "class20s"]:
        if section in data:
            print(f"Processing section: {section}")  
            for key, value in data[section].items():
                print(f"Processing key: {key}")  
                # 各地域の辞書情報からnameを取得
                area_name = value.get("name", "")
                print(f"Found name: {area_name}")  
                if area_name:  # nameが存在する場合のみ追加
                    area_options.append(ft.dropdown.Option(text=area_name, key=key))

    print(f"Total options: {len(area_options)}")  

    dropdown = ft.Dropdown(
        options=area_options,
        width=300,
        on_change=get_forecast
    )

    output = ft.Text()
    
    # 地域選択画面を初期表示
    show_area_selection()

    def get_forecast(e):
        area_code = dropdown.value
        if area_code:
            response = requests.get(f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json')
            if response.status_code == 200:
                forecast_data = response.json()
                save_forecast_to_db(forecast_data)  # データベースに保存
            else:
                output.value = f"Error: {response.status_code}"
                page.update()

ft.app(target=main)