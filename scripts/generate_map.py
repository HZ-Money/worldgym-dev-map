import os
import folium
import gpxpy

# 設定中心點為「新北市新莊區民安路188巷5號」
DEFAULT_CENTER = [25.0366, 121.4391]
DEFAULT_ZOOM = 17

def generate_map_for_folder(folder_name):
    if not os.path.isdir(folder_name):
        print(f"❌ 資料夾不存在：{folder_name}")
        return

    m = folium.Map(location=DEFAULT_CENTER, zoom_start=DEFAULT_ZOOM)

    for filename in os.listdir(folder_name):
        if filename.endswith('.gpx'):
            gpx_path = os.path.join(folder_name, filename)
            with open(gpx_path, 'r', encoding='utf-8') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [(point.latitude, point.longitude) for point in segment.points]
                        folium.PolyLine(points, color="blue", weight=5).add_to(m)

    output_path = os.path.join(folder_name, 'index.html')
    m.save(output_path)
    print(f"✅ 地圖已產出：{output_path}")

def main():
    for folder in os.listdir('.'):
        if folder.startswith('2025-') and os.path.isdir(folder):
            generate_map_for_folder(folder)

if __name__ == '__main__':
    main()
