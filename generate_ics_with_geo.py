#!/usr/bin/env python3
"""Generate ICS calendar with GEO (map location) support for Shanghai Port FC 2026 season."""

import json
from datetime import datetime, timedelta

# Chinese stadium coordinates (latitude, longitude)
STADIUM_COORDS = {
    # 上海海港主场
    "上海浦东足球场": {"geo": "31.1456,121.6008", "name": "上海浦东足球场"},
    "上海体育场": {"geo": "30.6778,121.4394", "name": "上海体育场（八万人体育场）"},
    # 各客队球场
    "郑州航海体育场": {"geo": "34.7447,113.7278", "name": "郑州航海体育场"},
    "成都凤凰山体育公园": {"geo": "30.8783,104.0947", "name": "成都凤凰山体育公园"},
    "杭州黄龙体育中心": {"geo": "30.2844,120.1367", "name": "杭州黄龙体育中心"},
    "北京国安（工人体育场）": {"geo": "39.9303,116.4380", "name": "北京工人体育场"},
    "武汉体育中心": {"geo": "30.5812,114.1312", "name": "武汉体育中心"},
    "深圳大运中心": {"geo": "22.7156,114.4114", "name": "深圳大运中心"},
    "重庆奥体中心": {"geo": "29.5286,106.4697", "name": "重庆奥体中心"},
    "青岛体育场": {"geo": "36.0671,120.3826", "name": "青岛新华锦体育场"},
    "青岛青春足球场": {"geo": "36.0850,120.3930", "name": "青岛青春足球场"},
    "厦门奥体中心": {"geo": "24.4570,118.0920", "name": "厦门奥体中心"},
    "天津泰达体育场": {"geo": "39.1469,117.2650", "name": "天津泰达体育场"},
    "大连梭鱼湾专业足球场": {"geo": "38.8630,121.5910", "name": "大连梭鱼湾专业足球场"},
    "济南奥体中心": {"geo": "36.8280,117.0930", "name": "济南奥体中心"},
    "辽宁铁人（沈阳浑南）": {"geo": "41.6230,123.5060", "name": "沈阳浑南足球训练基地"},
    "云南大学津桥学院": {"geo": "25.0420,102.7220", "name": "云南大学津桥学院"},
    "广州天河体育场": {"geo": "23.1300,113.3280", "name": "广州天河体育场"},
    "长沙贺龙体育场": {"geo": "28.2000,112.9380", "name": "长沙贺龙体育中心"},
}

def resolve_venue(venue_type, opponent_cn):
    """根据主客场和对阵球队解析场馆名。"""
    if venue_type == "Home":
        # 默认主场：上海浦东足球场
        return "上海浦东足球场", STADIUM_COORDS["上海浦东足球场"]["geo"]
    else:
        # 客场：根据对手确定球场
        away_map = {
            "河南队": ("郑州航海体育场", STADIUM_COORDS["郑州航海体育场"]["geo"]),
            "山东泰山": ("济南奥体中心", STADIUM_COORDS["济南奥体中心"]["geo"]),
            "北京国安": ("北京国安（工人体育场）", STADIUM_COORDS["北京国安（工人体育场）"]["geo"]),
            "浙江队": ("杭州黄龙体育中心", STADIUM_COORDS["杭州黄龙体育中心"]["geo"]),
            "成都蓉城": ("成都凤凰山体育公园", STADIUM_COORDS["成都凤凰山体育公园"]["geo"]),
            "武汉三镇": ("武汉体育中心", STADIUM_COORDS["武汉体育中心"]["geo"]),
            "深圳队": ("深圳大运中心", STADIUM_COORDS["深圳大运中心"]["geo"]),
            "上海申花": ("上海体育场", STADIUM_COORDS["上海体育场"]["geo"]),
            "重庆铜梁龙": ("重庆奥体中心", STADIUM_COORDS["重庆奥体中心"]["geo"]),
            "青岛西海岸": ("青岛青春足球场", STADIUM_COORDS["青岛青春足球场"]["geo"]),
            "青岛海牛": ("青岛新华锦体育场", STADIUM_COORDS["青岛体育场"]["geo"]),
            "天津津门虎": ("天津泰达体育场", STADIUM_COORDS["天津泰达体育场"]["geo"]),
            "大连英博": ("大连梭鱼湾专业足球场", STADIUM_COORDS["大连梭鱼湾专业足球场"]["geo"]),
            "辽宁铁人": ("辽宁铁人（沈阳浑南）", STADIUM_COORDS["辽宁铁人（沈阳浑南）"]["geo"]),
            "云南玉昆": ("云南大学津桥学院", STADIUM_COORDS["云南大学津桥学院"]["geo"]),
            "沈阳城市": ("辽宁铁人（沈阳浑南）", STADIUM_COORDS["辽宁铁人（沈阳浑南）"]["geo"]),
        }
        return away_map.get(opponent_cn, ("未知球场", "0.0,0.0"))


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
        "X-WR-CALDESC:上海海港足球俱乐部2026赛季中超联赛赛程（含地图定位）",
    ]

    for match in matches:
        dt_start = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
        dt_end = dt_start + timedelta(hours=2)
        dt_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        venue_name, geo = resolve_venue(match["venue"], match["opponent_cn"])

        home_away = "主" if match["venue"] == "Home" else "客"
        description = (
            f"中超联赛 2026赛季\n"
            f"上海海港 {'主场' if match['venue']=='Home' else '客场'} vs {match['opponent_cn']}\n"
            f"球场: {venue_name}"
        )

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Asia/Shanghai:{dt_start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID=Asia/Shanghai:{dt_end.strftime('%Y%m%dT%H%M%S')}",
            f"DTSTAMP:{dt_stamp}",
            f"UID:shanghai-port-2026-{match['date']}-{match['opponent_cn']}@shanghaiport.com",
            f"SUMMARY:上海海港 vs {match['opponent_cn']}",
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
    print(f"   每场比赛包含 GEO 坐标，可在日历中直接地图定位")


if __name__ == "__main__":
    with open("2026-schedule.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 生成带地图定位的ICS
    generate_ics(data["matches"], "shanghai_port_2026_with_geo.ics")

    # 同时生成原版（不覆盖）
    # generate_ics(data["matches"], "shanghai_port_2026.ics")
