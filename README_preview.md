# Launchrail Preview Engine

**설계도 → 프리뷰 UI 자동 생성 엔진**

---

## 📌 이 엔진은 무엇인가?

설계도 JSON을 입력하면 Standard OS 5-Section 프리뷰 HTML을 자동 생성하는 엔진입니다.

### 역할

```
설계도 JSON → preview_engine.py → 인터랙티브 HTML 프리뷰
```

**이 엔진이 하는 일:**
- ✅ JSON 설계도를 파싱하여 5-Section UI로 렌더링
- ✅ JDE/JOE 분리 구조 유지
- ✅ Standard OS 레이아웃 고정 출력
- ✅ 업종 무관 범용 엔진

**이 엔진이 하지 않는 일:**
- ❌ 설계 생성
- ❌ 설계 검수/판정 (→ Operator Dashboard에서 수행)
- ❌ 실행/배포

---

## 📂 파일 구조

```
launchrail-preview-engine/
├── preview_engine.py              # 핵심 엔진 (Python)
├── preview_viewer.html            # 브라우저 프리뷰 뷰어 (JSON → UI 렌더링)
├── b2b_saas_os_design.json        # 설계도 예시 (B2B SaaS)
├── b2b_saas_os_preview.html       # 생성된 프리뷰 예시
├── launchrail_dashboard SaaS.html       # SaaS 대시보드 프리뷰
└── launchrail_dashboard 헬스회원관리.html  # 헬스장 대시보드 프리뷰
```

---

## 🚀 사용 방법

### 방법 1: Python 엔진 (CLI)

```bash
python preview_engine.py design.json
```

→ HTML 파일 자동 생성

### 방법 2: Preview Viewer (브라우저)

1. `preview_viewer.html` 더블클릭
2. JSON 붙여넣기
3. "렌더링 시작" 클릭
4. 5-Section UI 바로 확인

---

## 🖥️ Standard OS 5-Section 구조

| 섹션 | 내용 |
|------|------|
| **Global Status** | 전체 상태 (OK/Warning/Action) + 헤드라인 |
| **Today's One Thing** | 오늘 가장 중요한 액션 1개 |
| **Signal Cards** | 4열 그리드, 사실+상태 카드 |
| **Recent History** | 시간순 활동 기록 |
| **Reasoning** | 판단 근거 (coverage + notes) |

---

## 📋 JSON 입력 형식

```json
{
  "status": "OK",
  "headline": "시스템 설명 문구",
  "one_thing": "오늘 해야 할 가장 중요한 일",
  "signals": [
    { "title": "항목명", "value": 123, "state": "OK" },
    { "title": "항목명", "value": 7, "state": "Warning" }
  ],
  "history": [
    { "time": "14:30", "event": "이벤트 내용", "state": "OK" }
  ],
  "reasoning": {
    "coverage": "판단 범위 설명",
    "notes": "추가 참고 사항"
  }
}
```

### 상태코드
- `OK` — 정상
- `Warning` — 주의
- `Action` — 즉시 조치 필요

---

## 🔗 관련 저장소

| 저장소 | 역할 |
|--------|------|
| **launchrail-preview-engine** (여기) | 설계도 → 프리뷰 생성 |
| **launchrail-operator-dashboard** | STEP 3 검수 + 판정 기록 |

---

## 🏗️ 아키텍처

```
JJO 7-Layer 기반
├── JDE (Stage 1~7): 타임라인 렌더링
└── JOE (Stage 8~10): 숨김 패널 (개발자 모드)
    └── 활성화: ?dev=true 또는 Cmd+Shift+J
```

---

## 🎯 핵심 원칙

**1. 범용 엔진** — 업종 무관, JSON만 맞으면 작동

**2. 형식 고정** — Standard OS 5-Section 레이아웃 불변

**3. 엔진은 렌더만** — 판단/검수는 Operator Dashboard 영역

---

## 🔄 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-06 | 초기 버전. preview_engine.py 작성, GitHub 업로드 |
| 2026-02-13 | Standard OS 5-Section UI 전환. JJO 7-Layer 유지 |
| 2026-02-15 | Preview Viewer (preview_viewer.html) 추가. 브라우저에서 JSON → UI 렌더링 가능 |

---

**Made with JJO System™ — Launchrail 2026**
