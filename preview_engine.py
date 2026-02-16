#!/usr/bin/env python3
"""
JJO System Preview Engine
=========================
AI OS 설계도(JSON)를 입력받아 운영자가 실제로 경험할 하루를
인터랙티브 HTML 프리뷰로 생성하는 범용 엔진

Architecture:
- JDE (1-7): Reasoning, Constraint, Safety, Memory, Audit, Routing, Evolution
- JOE (8-10): 비가시 기록/관찰/평가 구조
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class PreviewEngine:
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.design_data = self._load_json()
        self.timeline_log = []

    def _load_json(self) -> Dict:
        """JSON 설계도 파일 로드"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: File not found: {self.json_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format: {e}")
            sys.exit(1)

    def _get_events(self) -> tuple:
        """preview_directive.events 배열 추출 및 JDE/JOE 분리"""
        try:
            events = self.design_data.get('preview_directive', {}).get('events', [])
        except (KeyError, AttributeError):
            print("⚠️  Warning: No preview_directive.events found")
            return [], {"observation": [], "evaluation": [], "evolution": []}

        # JDE(1~7)와 JOE(8~10) 분리
        jde_events = []
        joe_data = {
            "observation": [],
            "evaluation": [],
            "evolution": []
        }

        for e in events:
            stage = e.get("stage", 0)
            if stage <= 7:
                jde_events.append(e)
            elif stage == 8:
                joe_data["observation"].append(e)
            elif stage == 9:
                joe_data["evaluation"].append(e)
            elif stage == 10:
                joe_data["evolution"].append(e)

        return jde_events, joe_data

    def _render_event_card(self, event: Dict, index: int) -> str:
        """이벤트를 HTML 카드로 렌더링"""
        event_type = event.get('type', 'normal')
        title = event.get('title', 'Untitled Event')
        description = event.get('description', '')
        stage = event.get('stage', 'N/A')
        human_gate = event.get('human_gate', False)
        safety_trigger = event.get('safety_trigger', False)

        # 카드 스타일 결정
        card_class = 'event-card'
        badge = ''

        if safety_trigger:
            card_class += ' safety-event'
            badge = '<span class="badge badge-danger">🛑 SAFETY</span>'
        elif human_gate:
            card_class += ' human-gate'
            badge = '<span class="badge badge-warning">👤 Human Gate</span>'

        # Stage 배지
        stage_badge = f'<span class="badge badge-stage">Stage {stage}</span>'

        return f'''
        <div class="{card_class}" data-index="{index}" data-type="{event_type}">
            <div class="card-header">
                <h3>
                    <span class="event-number">#{index + 1}</span>
                    {title}
                </h3>
                <div class="badges">
                    {stage_badge}
                    {badge}
                </div>
            </div>
            <div class="card-body">
                <p class="description">{description}</p>
                <div class="event-meta">
                    <span class="meta-item"><strong>Type:</strong> {event_type}</span>
                    {self._render_event_details(event)}
                </div>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary" onclick="processEvent({index})">
                    {'⚠️ Proceed with Caution' if safety_trigger else '▶️ Execute Event'}
                </button>
            </div>
        </div>
        '''

    def _render_event_details(self, event: Dict) -> str:
        """이벤트 세부 정보 렌더링"""
        details = []

        if 'input' in event:
            details.append(f'<span class="meta-item"><strong>Input:</strong> {event["input"]}</span>')

        if 'output' in event:
            details.append(f'<span class="meta-item"><strong>Output:</strong> {event["output"]}</span>')

        if 'reasoning' in event:
            details.append(f'<span class="meta-item"><strong>Reasoning:</strong> {event["reasoning"]}</span>')

        if 'constraint' in event:
            details.append(f'<span class="meta-item"><strong>Constraint:</strong> {event["constraint"]}</span>')

        return '\n'.join(details)

    def _render_joe_panel(self, joe_data: Dict) -> str:
        """JOE 데이터 패널 렌더링 (숨김 패널)"""
        def render_joe_section(title: str, events: List[Dict], stage: int) -> str:
            if not events:
                return f'<div class="joe-section"><h4>{title}</h4><p class="joe-empty">No data recorded</p></div>'

            items = []
            for e in events:
                items.append(f'''
                <div class="joe-item">
                    <div class="joe-item-header">
                        <strong>{e.get("title", "Untitled")}</strong>
                        <span class="joe-stage-badge">Stage {stage}</span>
                    </div>
                    <p class="joe-description">{e.get("description", "")}</p>
                    <div class="joe-meta">
                        {f'<div><strong>Input:</strong> {e["input"]}</div>' if "input" in e else ''}
                        {f'<div><strong>Output:</strong> {e["output"]}</div>' if "output" in e else ''}
                        {f'<div><strong>Reasoning:</strong> {e["reasoning"]}</div>' if "reasoning" in e else ''}
                    </div>
                </div>
                ''')

            return f'''
            <div class="joe-section">
                <h4>{title}</h4>
                {''.join(items)}
            </div>
            '''

        observation_html = render_joe_section("📊 Observation (Stage 8)", joe_data["observation"], 8)
        evaluation_html = render_joe_section("📈 Evaluation (Stage 9)", joe_data["evaluation"], 9)
        evolution_html = render_joe_section("🔄 Evolution (Stage 10)", joe_data["evolution"], 10)

        return f'''
        <div class="joe-panel" id="joePanel">
            <div class="joe-header">
                <h3>🧠 JOE Layer (Developer / Auditor Mode)</h3>
                <p class="joe-disclaimer">
                    This panel shows system-level observation and evaluation.
                    It does not affect operator decisions.
                </p>
            </div>
            <div class="joe-body">
                {observation_html}
                {evaluation_html}
                {evolution_html}
            </div>
        </div>
        '''

    def _generate_html(self) -> str:
        """완성된 HTML 프리뷰 생성 - 5섹션 구조"""
        jde_events, joe_data = self._get_events()
        system_name = self.design_data.get('system_name', 'JJO System')
        version = self.design_data.get('version', '1.0')

        # 용어 매핑
        stage_mapping = {
            1: "왜 이렇게 판단했나요?",
            2: "반드시 지킨 기준",
            3: "위험 감지 및 보호",
            4: "과거 기록",
            5: "판단 근거 로그",
            6: "운영 효율 상태",
            7: "앞으로 바뀔 수 있는 영역"
        }

        # ① Global Status 추출
        global_status = "OK"
        global_message = "오늘 전체 운영 상태는 정상입니다"
        warning_count = sum(1 for e in jde_events if e.get('safety_trigger') or e.get('human_gate'))

        if warning_count > 0:
            global_status = "Warning"
            global_message = f"주의가 필요한 항목이 {warning_count}개 있습니다"

        # ② Today's One Thing 추출 (첫 번째 action 타입)
        one_thing = next((e for e in jde_events if e.get('type') == 'action'), None)
        one_thing_html = ""
        if one_thing:
            one_thing_html = f'''
            <div class="one-thing-card">
                <h2>오늘 할 일</h2>
                <div class="one-thing-content">
                    <h3>{one_thing.get('title', '')}</h3>
                    <p>{one_thing.get('description', '')}</p>
                </div>
                <button class="btn-action">{one_thing.get('action_label', '실행하기')}</button>
            </div>
            '''

        # ③ Signal Cards (처음 4개 이벤트)
        signal_cards_html = []
        for i, event in enumerate(jde_events[:4]):
            status = "normal"
            if event.get('safety_trigger'):
                status = "danger"
            elif event.get('human_gate'):
                status = "warning"

            signal_cards_html.append(f'''
            <div class="signal-card signal-{status}">
                <div class="signal-icon">{event.get('icon', '📊')}</div>
                <div class="signal-headline">{event.get('title', '')}</div>
                <div class="signal-value">{event.get('value', '')}</div>
                <div class="signal-progress">
                    <div class="progress-bar-inner" style="width: {event.get('progress', 0)}%"></div>
                </div>
            </div>
            ''')

        # ④ Recent History
        history_html = []
        for i, event in enumerate(jde_events[-5:]):
            history_html.append(f'''
            <tr>
                <td class="history-time">{event.get('time', '00:00')}</td>
                <td class="history-activity">{event.get('title', '')}</td>
                <td class="history-status">
                    <span class="status-badge status-{event.get('status', 'normal')}">{event.get('status', 'OK')}</span>
                </td>
            </tr>
            ''')

        # ⑤ Reason/Coverage
        reason_sections_html = []
        for stage in range(1, 8):
            stage_events = [e for e in jde_events if e.get('stage') == stage]
            if stage_events:
                section_title = stage_mapping.get(stage, f"Stage {stage}")
                items = []
                for e in stage_events:
                    items.append(f'<li>{e.get("reasoning", e.get("description", ""))}</li>')

                reason_sections_html.append(f'''
                <div class="reason-section">
                    <h4>{section_title}</h4>
                    <ul>{''.join(items)}</ul>
                </div>
                ''')

        joe_panel = self._render_joe_panel(joe_data)

        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{system_name} - Launchrail Standard OS</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex;
        }}

        /* 좌측 사이드바 */
        .sidebar {{
            width: 220px;
            background: #2c3e50;
            color: white;
            padding: 30px 20px;
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            z-index: 100;
        }}

        .sidebar h1 {{
            font-size: 1.3em;
            margin-bottom: 10px;
        }}

        .sidebar .version {{
            font-size: 0.85em;
            color: #95a5a6;
            margin-bottom: 30px;
        }}

        .sidebar nav {{
            margin-top: 30px;
        }}

        .sidebar nav a {{
            display: block;
            color: #ecf0f1;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 5px;
            transition: background 0.2s;
        }}

        .sidebar nav a:hover {{
            background: rgba(255,255,255,0.1);
        }}

        /* 메인 영역 */
        .main-container {{
            margin-left: 220px;
            width: calc(100% - 220px);
            display: flex;
            flex-direction: column;
        }}

        /* 상단 헤더 */
        .top-header {{
            background: white;
            padding: 20px 40px;
            border-bottom: 1px solid #e1e8ed;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 90;
        }}

        .search-box {{
            flex: 1;
            max-width: 500px;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 0.95em;
        }}

        .header-status {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .status-indicator {{
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}

        .status-ok {{
            background: #d4edda;
            color: #155724;
        }}

        .status-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .status-danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        /* 메인 콘텐츠 */
        .main-content {{
            padding: 30px 40px;
            flex: 1;
        }}

        /* ① Global Status Bar */
        .global-status {{
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #28a745;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .global-status.warning {{
            border-left-color: #ffc107;
        }}

        .global-status.danger {{
            border-left-color: #dc3545;
        }}

        .global-status h2 {{
            font-size: 1.1em;
            color: #333;
            margin-bottom: 8px;
        }}

        .global-status .message {{
            color: #666;
            font-size: 0.95em;
        }}

        /* ② Today's One Thing */
        .one-thing-card {{
            background: #FFF9E5;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 2px solid #f5e6a8;
        }}

        .one-thing-card h2 {{
            font-size: 0.9em;
            color: #856404;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }}

        .one-thing-content h3 {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 10px;
        }}

        .one-thing-content p {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }}

        .btn-action {{
            background: #ffc107;
            color: #333;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-action:hover {{
            background: #e0a800;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        /* ③ Signal Cards - 4열 그리드 */
        .signal-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}

        .signal-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #28a745;
        }}

        .signal-card.signal-warning {{
            border-left-color: #ffc107;
        }}

        .signal-card.signal-danger {{
            border-left-color: #dc3545;
        }}

        .signal-icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}

        .signal-headline {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }}

        .signal-value {{
            font-size: 1.8em;
            font-weight: 700;
            color: #333;
            margin-bottom: 10px;
        }}

        .signal-progress {{
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
        }}

        .progress-bar-inner {{
            height: 100%;
            background: #28a745;
            transition: width 0.3s;
        }}

        /* ④⑤ History + Reason 2:1 레이아웃 */
        .bottom-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 60px;
        }}

        /* ④ Recent History */
        .history-panel {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .history-panel h3 {{
            font-size: 1.1em;
            margin-bottom: 20px;
            color: #333;
        }}

        .history-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .history-table th {{
            text-align: left;
            padding: 12px;
            background: #f8f9fa;
            color: #666;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .history-table td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }}

        .history-time {{
            color: #999;
            width: 80px;
        }}

        .history-activity {{
            color: #333;
        }}

        .history-status {{
            width: 100px;
            text-align: right;
        }}

        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }}

        .status-badge.status-normal {{
            background: #d4edda;
            color: #155724;
        }}

        .status-badge.status-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .status-badge.status-danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        /* ⑤ Reason/Coverage */
        .reason-panel {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            max-height: 600px;
            overflow-y: auto;
        }}

        .reason-panel h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #333;
        }}

        .reason-disclaimer {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            font-size: 0.85em;
            color: #666;
            line-height: 1.5;
            margin-bottom: 20px;
            border-left: 3px solid #6c757d;
        }}

        .reason-section {{
            margin-bottom: 20px;
        }}

        .reason-section h4 {{
            font-size: 0.95em;
            color: #495057;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .reason-section ul {{
            list-style: none;
            padding-left: 0;
        }}

        .reason-section li {{
            padding: 8px 0;
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
            border-bottom: 1px solid #f1f3f5;
        }}

        .reason-section li:last-child {{
            border-bottom: none;
        }}

        /* 봉인 문구 */
        .seal-notice {{
            position: fixed;
            bottom: 0;
            left: 220px;
            right: 0;
            background: #2c3e50;
            color: white;
            padding: 15px 40px;
            text-align: center;
            font-size: 0.85em;
            z-index: 80;
            border-top: 3px solid #ffc107;
        }}

        /* JOE 패널 (기존 유지) */
        .joe-toggle-btn {{
            position: fixed;
            bottom: 70px;
            right: 20px;
            background: #333;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1002;
            transition: all 0.3s ease;
        }}

        .joe-toggle-btn:hover {{
            background: #555;
            transform: translateY(-2px);
        }}

        .joe-panel {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 400px;
            max-height: 500px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
            z-index: 999;
            display: none;
        }}

        .joe-panel.visible {{
            display: block;
        }}

        .joe-header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
        }}

        .joe-header h3 {{
            margin-bottom: 10px;
            font-size: 1.2em;
        }}

        .joe-disclaimer {{
            font-size: 0.85em;
            color: #ecf0f1;
            font-style: italic;
            line-height: 1.4;
        }}

        .joe-body {{
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
        }}

        .joe-section {{
            margin-bottom: 20px;
        }}

        .joe-section h4 {{
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #ecf0f1;
        }}

        .joe-empty {{
            color: #999;
            font-style: italic;
            font-size: 0.9em;
        }}

        .joe-item {{
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 3px solid #95a5a6;
        }}

        .joe-item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .joe-stage-badge {{
            background: #95a5a6;
            color: white;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.8em;
        }}

        .joe-description {{
            color: #555;
            font-size: 0.9em;
            line-height: 1.5;
            margin-bottom: 8px;
        }}

        .joe-meta {{
            font-size: 0.85em;
            color: #666;
        }}

        .joe-meta div {{
            margin-bottom: 4px;
        }}

        @media (max-width: 1200px) {{
            .signal-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .bottom-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <!-- 좌측 사이드바 -->
    <div class="sidebar">
        <h1>{system_name}</h1>
        <div class="version">v{version}</div>
        <nav>
            <a href="#dashboard">📊 Dashboard</a>
            <a href="#signals">📡 Signals</a>
            <a href="#history">🕐 History</a>
            <a href="#settings">⚙️ Settings</a>
        </nav>
    </div>

    <!-- 메인 컨테이너 -->
    <div class="main-container">
        <!-- 상단 헤더 -->
        <div class="top-header">
            <div class="search-box">
                <input type="text" placeholder="검색...">
            </div>
            <div class="header-status">
                <span class="status-indicator status-{global_status.lower()}">{global_status}</span>
            </div>
        </div>

        <!-- 메인 콘텐츠 -->
        <div class="main-content">
            <!-- ① Global Status Bar -->
            <div class="global-status {global_status.lower()}">
                <h2>전체 운영 상태</h2>
                <div class="message">{global_message}</div>
            </div>

            <!-- ② Today's One Thing -->
            {one_thing_html}

            <!-- ③ Signal Cards -->
            <div class="signal-grid">
                {''.join(signal_cards_html)}
            </div>

            <!-- ④⑤ History + Reason -->
            <div class="bottom-grid">
                <!-- ④ Recent History -->
                <div class="history-panel">
                    <h3>최근 활동</h3>
                    <table class="history-table">
                        <thead>
                            <tr>
                                <th>시간</th>
                                <th>활동</th>
                                <th>상태</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(history_html)}
                        </tbody>
                    </table>
                </div>

                <!-- ⑤ Reason/Coverage -->
                <div class="reason-panel">
                    <h3>판단 근거</h3>
                    <div class="reason-disclaimer">
                        이 영역은 참고용 설명이며, 운영에 필요한 모든 판단은 상단 상태와 오늘 할 일에 이미 반영되어 있습니다.
                    </div>
                    {''.join(reason_sections_html)}
                </div>
            </div>
        </div>

        <!-- 봉인 문구 -->
        <div class="seal-notice">
            본 프리뷰 UI는 Launchrail Standard OS의 확정된 화면 사양이며, 시공 및 가격 산정의 기준으로 사용됩니다.
        </div>
    </div>

    <!-- JOE 패널 (Developer Mode) -->
    <button class="joe-toggle-btn" id="joeToggleBtn" onclick="toggleJoePanel()">
        🧠 Developer / Auditor Mode
    </button>

    {joe_panel}

    <script>
        function toggleJoePanel() {{
            const panel = document.getElementById('joePanel');
            panel.classList.toggle('visible');
        }}

        // ?dev=true 또는 Cmd+Shift+J로 JOE 패널 토글
        if (window.location.search.includes('dev=true')) {{
            document.getElementById('joePanel').classList.add('visible');
        }}

        document.addEventListener('keydown', (e) => {{
            if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'J') {{
                toggleJoePanel();
                e.preventDefault();
            }}
        }});
    </script>
</body>
</html>
'''

    def generate_preview(self, output_path: str = None) -> str:
        """프리뷰 HTML 생성 및 저장"""
        if output_path is None:
            output_path = self.json_path.stem + '_preview.html'

        html_content = self._generate_html()
        output_file = Path(output_path)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Preview generated: {output_file.absolute()}")
        return str(output_file.absolute())


def main():
    """CLI 진입점"""
    if len(sys.argv) < 2:
        print("Usage: python preview_engine.py <design.json> [output.html]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    engine = PreviewEngine(json_path)
    preview_path = engine.generate_preview(output_path)

    print(f"\n🎬 Open the preview in your browser:")
    print(f"   file:///{preview_path}")


if __name__ == '__main__':
    main()
