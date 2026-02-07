# LaunchRail Preview Engine

AI OS 설계도(JSON)를 입력받아 운영자가 실제로 경험할 하루를 인터랙티브 HTML 프리뷰로 생성하는 범용 엔진

## 🏗️ Architecture

**JJO System** - AI OS 설계의 10단계 표준 아키텍처

- **JDE (1-7)**: 가시적 운영 구조
  - Reasoning, Constraint, Safety, Memory, Audit, Routing, Evolution

- **JOE (8-10)**: 비가시 기록/관찰/평가 구조
  - Stage 8: Observation (관찰)
  - Stage 9: Evaluation (평가)
  - Stage 10: Evolution (진화)

## 🚀 Features

### 1. JSON → HTML 변환
- 설계도 JSON 파일을 읽어 인터랙티브 HTML 생성
- 업종 무관 범용 엔진

### 2. JDE/JOE 구조 분리
- **JDE Layer**: 운영자가 보는 메인 타임라인
- **JOE Layer**: 개발자/감사자 전용 숨김 패널

### 3. 특수 이벤트 처리
- **Human Gate** (`human_gate: true`): 인간 판단 필요
  - 주황색 테두리 + 👤 배지
- **Safety Trigger** (`safety_trigger: true`): 시스템 중단
  - 빨간색 테두리 + 🛑 배지

### 4. 인터랙티브 기능
- 버튼 클릭으로 단계별 진행
- 키보드 단축키 (스페이스, →)
- 자동 스크롤 및 진행률 표시
- 실시간 타임라인 로그

### 5. JOE 철학
- ❌ 추천 문구 금지
- ❌ "다음엔 이렇게 하세요" 금지
- ❌ 경향성 강조 금지
- ✅ 오직 기록/분류/보관만

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/wldb9210-eng/launchrail-preview-engine.git
cd launchrail-preview-engine

# Python 3.7+ required
python --version
```

## 🎯 Usage

### Basic Usage

```bash
python preview_engine.py <design.json>
```

### With Custom Output Path

```bash
python preview_engine.py design.json output.html
```

### Example

```bash
python preview_engine.py test_design.json
# Output: test_design_preview.html
```

## 📋 JSON Format

```json
{
  "system_name": "병원 AI 접수 시스템",
  "version": "1.0.0",
  "preview_directive": {
    "scenario": "일반 외래 환자 접수 시나리오",
    "events": [
      {
        "title": "환자 내원 및 초기 접수",
        "description": "환자가 병원에 도착하여 AI 키오스크에서 접수를 시작합니다.",
        "stage": 1,
        "type": "greeting",
        "input": "안녕하세요, 진료 받으러 왔습니다",
        "output": "환영합니다. 진료 접수를 도와드리겠습니다.",
        "reasoning": "친절한 첫인상 제공, 환자 불안감 해소",
        "constraint": "개인정보 보호법 준수",
        "human_gate": false,
        "safety_trigger": false
      }
    ]
  }
}
```

### Event Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | 이벤트 제목 |
| `description` | string | Yes | 이벤트 설명 |
| `stage` | number | Yes | 단계 (1-10) |
| `type` | string | Yes | 이벤트 타입 |
| `input` | string | No | 입력 데이터 |
| `output` | string | No | 출력 데이터 |
| `reasoning` | string | No | 추론 근거 |
| `constraint` | string | No | 제약사항 |
| `human_gate` | boolean | No | 인간 판단 필요 여부 |
| `safety_trigger` | boolean | No | Safety 트리거 여부 |

## 📂 Project Structure

```
launchrail-preview-engine/
├── preview_engine.py              # 메인 엔진
├── test_design.json               # 테스트 시나리오 (병원 접수)
├── test_design_preview.html       # v1 출력 샘플
├── test_design_preview_v2.html    # v2 출력 샘플 (JDE/JOE 분리)
└── README.md
```

## 🎬 Demo

### JDE Timeline (메인)
![JDE Timeline](https://via.placeholder.com/800x400?text=JDE+Timeline+Preview)

운영자가 경험하는 실제 이벤트 플로우 (Stage 1-7)

### JOE Panel (숨김)
![JOE Panel](https://via.placeholder.com/400x400?text=JOE+Panel+Preview)

개발자/감사자 전용 관찰/평가/진화 데이터 (Stage 8-10)

## 🧠 JOE Layer Philosophy

JOE 패널은 **"추천하지 않는다"**는 철학을 따릅니다:

- 시스템이 무엇을 관찰했는지 **기록**
- 어떤 패턴이 있는지 **분류**
- 데이터를 **보관**

하지만 절대:
- "이렇게 하세요" 제안 ❌
- "다음엔 이렇게" 권장 ❌
- 경향성 강조 ❌

> "This panel shows system-level observation and evaluation.
> It does not affect operator decisions."

## 🔧 Advanced Features

### Custom Styling

HTML 출력 파일의 CSS를 수정하여 커스터마이징 가능:

```css
.event-card {
    background: white;
    border-radius: 10px;
    /* 원하는 스타일 추가 */
}
```

### Keyboard Shortcuts

- `Space` or `→`: 다음 이벤트 실행
- 버튼 클릭: 개별 이벤트 실행

### Developer Mode Toggle

"🧠 Developer / Auditor Mode" 버튼 클릭으로 JOE 패널 토글

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**wldb9210-eng**

- GitHub: [@wldb9210-eng](https://github.com/wldb9210-eng)

## 🙏 Acknowledgments

- JJO System Architecture
- AI OS Design Principles
- LaunchRail Framework

---

**Made with ❤️ for AI System Designers**
