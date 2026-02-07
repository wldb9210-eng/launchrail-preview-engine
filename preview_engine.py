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
        """완성된 HTML 프리뷰 생성"""
        jde_events, joe_data = self._get_events()
        system_name = self.design_data.get('system_name', 'JJO System')
        version = self.design_data.get('version', '1.0')

        event_cards = '\n'.join([
            self._render_event_card(event, i)
            for i, event in enumerate(jde_events)
        ])

        joe_panel = self._render_joe_panel(joe_data)

        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{system_name} - Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .version {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }}

        .timeline {{
            position: relative;
            padding-left: 40px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: rgba(255,255,255,0.3);
        }}

        .event-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            position: relative;
            transition: all 0.3s ease;
            opacity: 0.6;
        }}

        .event-card.active {{
            opacity: 1;
            transform: translateX(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .event-card.completed {{
            opacity: 0.5;
            background: #f0f0f0;
        }}

        .event-card::before {{
            content: '';
            position: absolute;
            left: -28px;
            top: 30px;
            width: 16px;
            height: 16px;
            background: white;
            border: 3px solid #667eea;
            border-radius: 50%;
        }}

        .event-card.active::before {{
            background: #667eea;
            box-shadow: 0 0 0 6px rgba(102, 126, 234, 0.3);
        }}

        .event-card.completed::before {{
            background: #4CAF50;
            border-color: #4CAF50;
        }}

        .human-gate {{
            border-left: 5px solid #ff9800;
        }}

        .safety-event {{
            border-left: 5px solid #f44336;
            background: #fff3f3;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .card-header h3 {{
            color: #333;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .event-number {{
            display: inline-block;
            background: #667eea;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            text-align: center;
            line-height: 35px;
            font-size: 0.8em;
        }}

        .badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .badge-stage {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        .card-body {{
            margin-bottom: 15px;
        }}

        .description {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .event-meta {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}

        .meta-item {{
            color: #555;
            font-size: 0.95em;
        }}

        .card-footer {{
            display: flex;
            justify-content: flex-end;
        }}

        .btn {{
            padding: 10px 25px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .btn-primary {{
            background: #667eea;
            color: white;
        }}

        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}

        .log-panel {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            max-height: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
            z-index: 1000;
        }}

        .log-header {{
            background: #333;
            color: white;
            padding: 15px;
            font-weight: bold;
        }}

        .log-body {{
            padding: 15px;
            max-height: 320px;
            overflow-y: auto;
        }}

        .log-entry {{
            padding: 8px;
            margin-bottom: 8px;
            border-left: 3px solid #667eea;
            background: #f8f9fa;
            font-size: 0.9em;
        }}

        .log-entry.success {{
            border-left-color: #4CAF50;
        }}

        .log-entry.warning {{
            border-left-color: #ff9800;
        }}

        .log-entry.error {{
            border-left-color: #f44336;
        }}

        .log-timestamp {{
            color: #999;
            font-size: 0.85em;
        }}

        .progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: rgba(0,0,0,0.1);
            z-index: 1001;
        }}

        .progress-fill {{
            height: 100%;
            background: #4CAF50;
            transition: width 0.3s ease;
            width: 0%;
        }}

        .joe-toggle-btn {{
            position: fixed;
            bottom: 440px;
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
            right: 390px;
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

        @media (max-width: 768px) {{
            .log-panel {{
                width: calc(100% - 40px);
                bottom: 10px;
                right: 20px;
                left: 20px;
            }}

            .joe-panel {{
                width: calc(100% - 40px);
                right: 20px;
                left: 20px;
                bottom: 430px;
            }}

            .joe-toggle-btn {{
                bottom: auto;
                top: 80px;
                right: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="progress-bar">
        <div class="progress-fill" id="progressFill"></div>
    </div>

    <div class="container">
        <header>
            <h1>
                {system_name}
                <span class="version">v{version}</span>
            </h1>
            <p class="subtitle">🎬 Interactive Preview - 운영자가 경험할 하루</p>
        </header>

        <div class="timeline" id="timeline">
            {event_cards}
        </div>
    </div>

    <button class="joe-toggle-btn" id="joeToggleBtn" onclick="toggleJoePanel()">
        🧠 Developer / Auditor Mode
    </button>

    {joe_panel}

    <div class="log-panel">
        <div class="log-header">📋 Timeline Log</div>
        <div class="log-body" id="logBody"></div>
    </div>

    <script>
        let currentEventIndex = -1;
        const totalEvents = {len(jde_events)};

        function toggleJoePanel() {{
            const panel = document.getElementById('joePanel');
            panel.classList.toggle('visible');
        }}

        function addLog(message, type = 'info') {{
            const logBody = document.getElementById('logBody');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = `log-entry ${{type}}`;
            entry.innerHTML = `
                <div class="log-timestamp">${{timestamp}}</div>
                <div>${{message}}</div>
            `;
            logBody.insertBefore(entry, logBody.firstChild);
        }}

        function updateProgress() {{
            const progress = ((currentEventIndex + 1) / totalEvents) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }}

        function processEvent(index) {{
            const cards = document.querySelectorAll('.event-card');
            const card = cards[index];
            const eventType = card.dataset.type;
            const title = card.querySelector('h3').textContent.trim();

            // 이전 카드 완료 표시
            if (currentEventIndex >= 0) {{
                cards[currentEventIndex].classList.remove('active');
                cards[currentEventIndex].classList.add('completed');
            }}

            // 현재 카드 활성화
            currentEventIndex = index;
            card.classList.add('active');
            card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

            // 버튼 비활성화
            const button = card.querySelector('.btn');
            button.disabled = true;
            button.textContent = '✓ Completed';

            // 로그 추가
            if (card.classList.contains('safety-event')) {{
                addLog(`🛑 Safety Event Triggered: ${{title}}`, 'error');
            }} else if (card.classList.contains('human-gate')) {{
                addLog(`👤 Human Gate: ${{title}}`, 'warning');
            }} else {{
                addLog(`✓ Event Executed: ${{title}}`, 'success');
            }}

            // 진행률 업데이트
            updateProgress();

            // 다음 이벤트 활성화
            if (index + 1 < totalEvents) {{
                setTimeout(() => {{
                    cards[index + 1].style.opacity = '1';
                }}, 300);
            }} else {{
                addLog('🎉 All events completed!', 'success');
            }}
        }}

        // 초기화: 첫 번째 이벤트만 활성화
        document.addEventListener('DOMContentLoaded', () => {{
            const cards = document.querySelectorAll('.event-card');
            if (cards.length > 0) {{
                cards[0].style.opacity = '1';
                addLog('Preview session started', 'info');
            }}
        }});

        // 키보드 단축키
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') {{
                const cards = document.querySelectorAll('.event-card');
                if (currentEventIndex + 1 < totalEvents) {{
                    processEvent(currentEventIndex + 1);
                }}
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
