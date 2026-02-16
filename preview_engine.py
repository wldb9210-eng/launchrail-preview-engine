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

        # Stage별 Tailwind 색상 매핑
        stage_colors = {
            1: "blue", 2: "blue", 3: "amber",
            4: "emerald", 5: "gray", 6: "purple", 7: "indigo"
        }

        # ① Global Status 추출
        global_status = "OK"
        global_message = "오늘 전체 운영 상태는 정상입니다"
        warning_count = sum(1 for e in jde_events if e.get('safety_trigger') or e.get('human_gate'))

        if warning_count > 0:
            global_status = "Warning"
            global_message = f"주의가 필요한 항목이 {warning_count}개 있습니다"

        status_dot = "green" if global_status == "OK" else "amber"
        status_label = f"{system_name} 운영 정상" if global_status == "OK" else f"운영 주의 · {warning_count}건"

        # ② Today's One Thing 추출 (첫 번째 action 타입)
        one_thing = next((e for e in jde_events if e.get('type') == 'action'), None)
        one_thing_html = ""
        if one_thing:
            one_thing_html = f'''
            <div class="card p-5 mb-5" style="background: #FFF9E5;">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-amber-200 rounded-xl flex items-center justify-center text-2xl">{one_thing.get('icon', '📌')}</div>
                        <div>
                            <p class="text-amber-700 text-[10px] font-semibold uppercase tracking-wider mb-0.5">오늘 꼭 해야 할 일</p>
                            <h3 class="text-gray-900 text-lg font-bold">{one_thing.get('title', '')}</h3>
                        </div>
                    </div>
                    <button class="bg-amber-400 hover:bg-amber-500 text-gray-900 px-5 py-2 rounded-full font-semibold text-xs transition">
                        {one_thing.get('action_label', '지금 확인')} →
                    </button>
                </div>
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

            color_map = {"normal": "emerald", "warning": "amber", "danger": "red"}
            label_map = {"normal": "정상", "warning": "주의", "danger": "위험"}
            color = color_map[status]
            label = label_map[status]

            signal_cards_html.append(f'''
                <div class="card p-4">
                    <div class="flex items-center justify-between mb-2">
                        <div class="w-10 h-10 bg-{color}-100 rounded-lg flex items-center justify-center text-lg">
                            {event.get('icon', '📊')}
                        </div>
                        <span class="text-[10px] font-semibold text-gray-500 uppercase">{label}</span>
                    </div>
                    <h4 class="text-gray-900 font-bold text-sm mb-1">{event.get('title', '')}</h4>
                    <div class="flex items-end gap-1 mb-2">
                        <span class="text-3xl font-bold text-gray-900">{event.get('value', '')}</span>
                    </div>
                    <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
                        <div class="h-full bg-{color}-500" style="width: {event.get('progress', 0)}%"></div>
                    </div>
                    <p class="text-[10px] text-gray-600">{event.get('description', '')}</p>
                </div>
            ''')

        # ④ Recent History
        last_events = jde_events[-5:]
        history_html = []
        for i, event in enumerate(last_events):
            status = event.get('status', 'normal')
            color_map = {"normal": "emerald", "warning": "amber", "danger": "red"}
            label_map = {"normal": "완료", "warning": "주의", "danger": "위험"}
            color = color_map.get(status, "emerald")
            label = label_map.get(status, status)
            border = "border-b border-gray-50" if i < len(last_events) - 1 else ""

            history_html.append(f'''
                        <div class="flex items-center justify-between py-2 {border}">
                            <div class="flex items-center gap-3">
                                <span class="text-[10px] text-gray-500 font-mono w-12">{event.get('time', '00:00')}</span>
                                <span class="text-xs font-medium text-gray-900">{event.get('title', '')}</span>
                            </div>
                            <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-{color}-100 text-{color}-700 rounded-full text-[10px] font-semibold">
                                <span class="w-1 h-1 bg-{color}-500 rounded-full"></span>
                                {label}
                            </span>
                        </div>
            ''')

        # ⑤ Reason/Coverage
        reason_sections_html = []
        for stage in range(1, 8):
            stage_events = [e for e in jde_events if e.get('stage') == stage]
            if stage_events:
                section_title = stage_mapping.get(stage, f"Stage {stage}")
                color = stage_colors.get(stage, "gray")
                items = []
                for e in stage_events:
                    items.append(f'<li>• {e.get("reasoning", e.get("description", ""))}</li>')

                reason_sections_html.append(f'''
                        <div>
                            <div class="flex items-center gap-1.5 mb-1">
                                <div class="w-1.5 h-1.5 bg-{color}-500 rounded-full"></div>
                                <h4 class="font-semibold text-[11px] text-gray-900">{section_title}</h4>
                            </div>
                            <ul class="text-[10px] text-gray-600 space-y-0.5 ml-3">
                                {''.join(items)}
                            </ul>
                        </div>
                ''')

        joe_panel = self._render_joe_panel(joe_data)

        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{system_name} - Launchrail Standard OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body {{
            background: #F5F7FA;
            overflow: hidden;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        .sidebar {{
            width: 220px;
            background: white;
            border-right: 1px solid #E5E7EB;
        }}
        .main-content {{
            height: 100vh;
            overflow-y: auto;
        }}

        /* JOE 패널 */
        .joe-toggle-btn {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1f2937;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 25px;
            font-size: 0.8em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1002;
            transition: all 0.2s;
        }}
        .joe-toggle-btn:hover {{
            background: #374151;
            transform: translateY(-2px);
        }}
        .joe-panel {{
            position: fixed;
            bottom: 60px;
            right: 20px;
            width: 380px;
            max-height: 480px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
            z-index: 999;
            display: none;
        }}
        .joe-panel.visible {{
            display: block;
        }}
        .joe-header {{
            background: #1f2937;
            color: white;
            padding: 16px 20px;
        }}
        .joe-header h3 {{
            margin-bottom: 8px;
            font-size: 1em;
            font-weight: 700;
        }}
        .joe-disclaimer {{
            font-size: 0.75em;
            color: #d1d5db;
            line-height: 1.4;
        }}
        .joe-body {{
            padding: 16px;
            max-height: 360px;
            overflow-y: auto;
        }}
        .joe-section {{
            margin-bottom: 16px;
        }}
        .joe-section h4 {{
            color: #1f2937;
            font-size: 0.9em;
            font-weight: 700;
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .joe-empty {{
            color: #9ca3af;
            font-style: italic;
            font-size: 0.8em;
        }}
        .joe-item {{
            background: #f9fafb;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 8px;
            border-left: 3px solid #9ca3af;
        }}
        .joe-item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .joe-stage-badge {{
            background: #6b7280;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7em;
            font-weight: 600;
        }}
        .joe-description {{
            color: #6b7280;
            font-size: 0.8em;
            line-height: 1.5;
            margin-bottom: 6px;
        }}
        .joe-meta {{
            font-size: 0.75em;
            color: #6b7280;
        }}
        .joe-meta div {{
            margin-bottom: 3px;
        }}
    </style>
</head>
<body class="flex">

    <!-- 좌측 사이드바 -->
    <div class="sidebar h-screen p-5">
        <div class="mb-6">
            <h1 class="text-xl font-bold text-gray-900">{system_name}</h1>
            <p class="text-[10px] text-gray-500 mt-0.5">v{version}</p>
        </div>
        <nav class="space-y-1">
            <a href="#" class="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 text-gray-900 font-medium text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                </svg>
                Dashboard
            </a>
        </nav>
    </div>

    <!-- 메인 컨텐츠 -->
    <div class="flex-1 main-content">

        <!-- 상단 헤더 -->
        <div class="bg-white border-b border-gray-200 px-6 py-3 sticky top-0 z-10">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <h2 class="text-xl font-bold text-gray-900">Dashboard</h2>
                    <div class="flex items-center gap-1.5">
                        <div class="w-2 h-2 bg-{status_dot}-500 rounded-full"></div>
                        <span class="text-xs text-gray-600">{status_label}</span>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <input type="text" placeholder="Search..." class="px-3 py-1.5 bg-gray-50 rounded-lg text-xs border-0 w-48">
                    <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                </div>
            </div>
        </div>

        <div class="p-6">

            <!-- ② Today's One Thing -->
            {one_thing_html}

            <!-- ③ Signal Cards -->
            <div class="grid grid-cols-4 gap-4 mb-5">
                {''.join(signal_cards_html)}
            </div>

            <!-- ④⑤ History + Reason -->
            <div class="grid grid-cols-3 gap-4">

                <!-- ④ Recent History -->
                <div class="col-span-2 card p-4">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
                            <span>📜</span> 최근 활동 기록
                        </h3>
                    </div>
                    <div class="space-y-0">
                        {''.join(history_html)}
                    </div>
                </div>

                <!-- ⑤ Reason/Coverage -->
                <div class="card p-4">
                    <h3 class="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <span>💡</span> 판단 근거
                    </h3>
                    <div class="bg-blue-50 rounded-lg p-3 mb-3">
                        <p class="text-[10px] text-blue-900 leading-relaxed">
                            운영에 필요한 모든 판단은 <strong>상단</strong>에 반영되어 있습니다.
                        </p>
                    </div>
                    <div class="space-y-3">
                        {''.join(reason_sections_html)}
                    </div>
                </div>

            </div>

        </div>

        <!-- 봉인 문구 -->
        <div class="bg-white border-t border-gray-200 py-4 mt-6">
            <div class="text-center">
                <p class="text-[10px] text-gray-600">
                    본 프리뷰 UI는 <strong class="text-gray-900">Launchrail Standard OS</strong>의 확정된 화면 사양이며, 시공 및 가격 산정의 기준으로 사용됩니다.
                </p>
            </div>
        </div>

    </div>

    <!-- JOE 패널 (Developer Mode) -->
    <button class="joe-toggle-btn" id="joeToggleBtn" onclick="toggleJoePanel()">
        🧠 Developer Mode
    </button>

    {joe_panel}

    <script>
        function toggleJoePanel() {{
            const panel = document.getElementById('joePanel');
            panel.classList.toggle('visible');
        }}

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
