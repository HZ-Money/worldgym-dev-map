import os
import re
import folium
import gpxpy
import json

DEFAULT_CENTER = [25.0366, 121.4391]  # 民安路188巷5號
DEFAULT_ZOOM = 16
FIXED_MARKER = {
    "name": "民安門市",
    "address": "新北市新莊區民安路188巷5號",
    "lat": 25.0366,
    "lng": 121.4391,
    "emoji": "📍"
}

folders = sorted([f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")])

def extract_name(filename):
    name_part = re.sub(r'^[\d_]*', '', filename)
    return name_part.replace('.gpx', '')

def generate_map_for_folder(gpx_folder):
    print(f"📍 正在處理：{gpx_folder}")
    m = folium.Map(location=DEFAULT_CENTER, zoom_start=DEFAULT_ZOOM, control_scale=True)

    # ⬅️ 返回首頁按鈕 + 標題（固定左上角）
    header_html = f'''
    <div style="position: fixed; top: 10px; left: 10px; z-index: 9999;
                background-color: white; padding: 10px 14px; border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3); line-height: 1.6;">
        <div><a href="../index.html" style="text-decoration:none;font-weight:bold;color:#d43f3a;">🔙 返回首頁</a></div>
        <div style="font-size:16px; font-weight:bold;">🦍🌍 WorldGym HZ 每日開發地圖</div>
        <div style="font-size:14px;">📅 月份：<b>{gpx_folder} 💰</b></div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(header_html))

    # 🏪 商家圖層
    merchant_layer = folium.FeatureGroup(name='🏪 特約商家')
    m.add_child(merchant_layer)

    shops_file = os.path.join(gpx_folder, 'shops.json')
    if os.path.exists(shops_file):
        try:
            with open(shops_file, 'r', encoding='utf-8') as f:
                shops_json = json.load(f)
                shops_data = shops_json.get("features", [])
                for shop in shops_data:
                    geometry = shop.get("geometry", {})
                    properties = shop.get("properties", {})
                    coords = geometry.get("coordinates", [])
                    if len(coords) == 2:
                        lon, lat = coords
                        name = properties.get("name", "商家")
                        note = properties.get("note", "")
                        emoji = properties.get("emoji", "")
                        popup_html = f"<b>{emoji} {name}</b><br>{note}"
                        folium.Marker(
                            location=[lat, lon],
                            popup=popup_html,
                            icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
                        ).add_to(merchant_layer)
        except Exception as e:
            print(f"❌ 商家載入失敗: {e}")

    # 🏠 固定地點標記：民安門市
    folium.Marker(
        location=[FIXED_MARKER["lat"], FIXED_MARKER["lng"]],
        popup=f"{FIXED_MARKER['emoji']} {FIXED_MARKER['name']}<br>{FIXED_MARKER['address']}",
        icon=folium.Icon(color="green", icon="home", prefix="fa")
    ).add_to(m)

    # 🚴 GPX 軌跡分層顯示
    gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]
    agent_layers = {}

    for gpx_file in sorted(gpx_files):
        name = extract_name(gpx_file)
        if name not in agent_layers:
            agent_layers[name] = folium.FeatureGroup(name=f'🚴 {name}')
            m.add_child(agent_layers[name])
        try:
            with open(os.path.join(gpx_folder, gpx_file), 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)
                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [(p.latitude, p.longitude) for p in segment.points]
                        if points:
                            folium.PolyLine(
                                points,
                                color="blue",
                                weight=4,
                                opacity=0.8,
                                tooltip=folium.Tooltip(f"📄 {gpx_file}", sticky=True)
                            ).add_to(agent_layers[name])
        except Exception as e:
            print(f"❌ GPX 錯誤 {gpx_file}: {e}")

    folium.LayerControl(collapsed=False).add_to(m)

    output_file = os.path.join(gpx_folder, "index.html")
    m.save(output_file)
    print(f"✅ 已產生地圖：{output_file}")

for folder in folders:
    generate_map_for_folder(folder)
