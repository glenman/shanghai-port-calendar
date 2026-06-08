#!/usr/bin/env python3
import json

with open('2026-schedule.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
for match in data['matches']:
    if match['match_number'] == 15:
        print(f"第15轮: {match['opponent_cn']} - 辽宁铁人 ✓")
    elif match['match_number'] == 30:
        print(f"第30轮: {match['opponent_cn']} - 辽宁铁人 ✓")
