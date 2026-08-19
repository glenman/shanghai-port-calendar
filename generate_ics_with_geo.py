#!/usr/bin/env python3
"""Generate ICS calendar with GEO (map location) support for Shanghai Port FC 2026 season.

数据源: schedule.json (含超级杯/中超/足协杯/亚冠全部赛事)
输出: shanghai_port_2026_with_geo.ics (含地图定位)
"""

import json
from datetime import datetime, timedelta

# 球场坐标 (纬度,经度) - 含中超/足协杯/亚冠全部球场
STADIUM_COORDS = {
    # 上海主场
    "上海体育场": {"geo": "31.1447,121.4394", "name": "上海体育场（八万人体育场）"},
    "上汽浦东足球场": {"geo": "31.2050,121.6290", "name": "上汽浦东足球场"},
    "浦东足球场": {"geo": "31.2050,121.6290", "name": "浦东足球场"},
    # 中超客场
    "大连梭鱼湾足球场": {"geo": "38.8630,121.5910", "name": "大连梭鱼湾足球场"},
    "济南奥体中心": {"geo": "36.8280,117.0930", "name": "济南奥体中心"},
    "青岛国信体育场": {"geo": "36.0671,120.3826", "name": "青岛国信体育场"},
    "青岛西海岸体育场": {"geo": "36.0850,120.3930", "name": "青岛西海岸体育场"},
    "北京工人体育场": {"geo": "39.9303,116.4380", "name": "北京工人体育场"},
    "成都凤凰山体育场": {"geo": "30.8783,104.0947", "name": "成都凤凰山体育场"},
    "郑州航海体育场": {"geo": "34.7447,113.7278", "name": "郑州航海体育场"},
    "沈阳奥体中心": {"geo": "41.6230,123.5060", "name": "沈阳奥体中心"},
    "武汉体育中心": {"geo": "30.5812,114.1312", "name": "武汉体育中心"},
    "深圳大运中心": {"geo": "22.7156,114.4114", "name": "深圳大运中心"},
    "重庆龙兴体育场": {"geo": "29.5286,106.4697", "name": "重庆龙兴体育场"},
    "玉溪高原体育场": {"geo": "24.3510,102.5460", "name": "玉溪高原体育场"},
    "杭州黄龙体育中心": {"geo": "30.2844,120.1367", "name": "杭州黄龙体育中心"},
    "天津奥体中心": {"geo": "39.1469,117.2650", "name": "天津奥体中心"},
    # 超级杯
    "南京奥体中心": {"geo": "32.0030,118.7240", "name": "南京奥体中心"},
    # 亚冠客场 (海外)
    "叻丕体育场": {"geo": "13.5280,99.8130", "name": "叻丕体育场 (Ratchaburi Stadium)"},
    "纽卡斯尔体育场": {"geo": "-32.9280,151.7760", "name": "纽卡斯尔体育场 (Newcastle Stadium)"},
    "浦项钢园球场": {"geo": "36.0130,129.3650", "name": "浦项钢园球场 (Pohang Steel Yard)"},
    "全州世界杯竞技场": {"geo": "35.8380,127.1460", "name": "全州世界杯竞技场 (Jeonju World Cup Stadium)"},
}

# 赛事类型 → 日历分组描述
COMPETITION_DESC = {
    "超级杯": "超级杯",
    "中超": "中超联赛",
    "足协杯": "足协杯",
    "亚冠": "亚冠精英联赛",
}


def resolve_venue(venue_name):
    """根据球场名查找坐标，找不到则返回默认值。"""
    entry = STADIUM_COORDS.get(venue_name)
    if entry:
        return venue_name, entry["geo"]
    return venue_name, "0.0,0.0"


def build_description(match):
    """构建 ICS DESCRIPTION 字段。"""
    comp = COMPETITION_DESC.get(match.get("type", ""), match.get("type", ""))
    is_home = match["homeTeam"] == "上海海港"
    home_away = "主场" if is_home else "客场"
    opponent = match["awayTeam"] if is_home else match["homeTeam"]

    lines = [
        f"{comp} 2026赛季 {match.get('round', '')}",
        f"上海海港 {home_away} vs {opponent}",
        f"球场: {match.get('venue', '未知')}",
    ]

    if match.get("status") == "已结束" and match.get("result", "-") != "-":
        lines.append(f"比分: {match['result']}")
        scorers = match.get("scorers")
        if scorers:
            home_scorers = scorers.get("home", [])
            away_scorers = scorers.get("away", [])
            if home_scorers:
                lines.append(f"{match['homeTeam']}进球: {', '.join(home_scorers)}")
            if away_scorers:
                lines.append(f"{match['awayTeam']}进球: {', '.join(away_scorers)}")

    if match.get("referee") and match["referee"] != "未知":
        lines.append(f"裁判: {match['referee']}")

    return "\n".join(lines)


def generate_ics(matches, output_file):
    """生成带GEO属性的ICS文件。"""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shanghai Port FC Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:上海海港2026赛季赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-WR-CALDESC:上海海港足球俱乐部2026赛季赛程（超级杯/中超/足协杯/亚冠，含地图定位）",
    ]

    for match in matches:
        dt_start = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
        dt_end = dt_start + timedelta(hours=2)
        dt_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        venue_name, geo = resolve_venue(match.get("venue", ""))
        is_home = match["homeTeam"] == "上海海港"
        opponent = match["awayTeam"] if is_home else match["homeTeam"]
        comp = COMPETITION_DESC.get(match.get("type", ""), match.get("type", ""))
        home_away = "主" if is_home else "客"

        description = build_description(match)
        summary = f"上海海港 {home_away}场 vs {opponent} ({comp})"

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Asia/Shanghai:{dt_start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID=Asia/Shanghai:{dt_end.strftime('%Y%m%dT%H%M%S')}",
            f"DTSTAMP:{dt_stamp}",
            f"UID:shanghai-port-2026-{match['id']}-{match['date']}@shanghaiport.com",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description.replace(chr(10), chr(13) + chr(10))}",
            f"LOCATION:{venue_name}",
            f"GEO:{geo}",
            f"STATUS:CONFIRMED",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print(f"✅ ICS文件已生成: {output_file}")
    print(f"   共 {len(matches)} 场比赛")


if __name__ == "__main__":
    with open("schedule.json", "r", encoding="utf-8") as f:
        matches = json.load(f)

    # 按日期排序
    matches.sort(key=lambda m: m["date"])

    # 生成带地图定位的ICS
    generate_ics(matches, "shanghai_port_2026_with_geo.ics")
