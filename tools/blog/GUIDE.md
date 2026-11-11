# 철거정보 글 작성 지침 (자동 발행용)

오늘의 철거(https://onulcheolgeo.kr) 사이트의 **철거정보** 게시판(/info/)에 올리는 정보글 작성 규칙이다.
예약 작업은 이 문서를 처음부터 끝까지 읽고 그대로 따른다. 사이트 공통 규칙은 저장소 루트의 `CLAUDE.md` 에 있다.

## 1. 목적과 말투
- 목적: 철거·원상복구·폐업을 앞둔 사장님이 검색으로 들어와 **바로 답을 얻고**, 필요하면 상담으로 이어지게 하는 것.
- 정보성 글. 광고·홍보 말투 금지. 존댓말, 쉬운 말, 한 문단 3~4문장 이내.
- 금지 표현(빌드 검사에서 막힘): 최고, 최저가, 업계 1위, 1위, 100%, 보장합니다, 엄선, 맞춤형, 체계적, 완벽, 무조건, 최상, 그리고 사람 이름 '박시연'.
- 본문에 **전화번호 숫자를 쓰지 않는다.** 상담 안내는 글 아래 상담 상자(자동으로 붙음)가 한다.
- 지어낸 후기·사례·금액·실적·통계 금지. "평당 얼마" 같은 가격은 쓰지 않는다(현장마다 다름).

## 2. 사실 확인 규칙
- 법령·제도·기한·지원금·서류 같은 사실은 **공식 출처**(국가법령정보센터, 국세청, 소상공인시장진흥공단·소상공인24, 정부24, 환경부, 고용노동부, 지자체·교육청 등)를 WebSearch/WebFetch로 확인한 것만 쓴다.
- 공식 기관 자료를 그대로 옮긴 2차 자료(기관 PDF를 올린 상공회의소 등)는 발행 기관이 확인되면 쓸 수 있다. 일반 블로그 정보만으로는 쓰지 않는다.
- 확인 못 한 내용은 빼거나 "신청 시점의 공식 공고 확인", "관할 구청(세무서·보건소 등) 확인"으로만 안내한다.
- 확인한 출처는 `refs` 에 제목과 주소로 적는다(1개 이상).
- roadmap.json 의 `verify` 항목은 반드시 확인을 시도한다. 확인이 꼭 필요한 핵심 사실을 끝내 확인하지 못하면 그 글은 쓰지 말고(=push 하지 않고) 사장님께 무엇을 확인해 달라는지 보고한다.

### 오늘의 철거에 대해 쓸 수 있는 사실(사장님 확인)
- 무료 방문견적, 현장 확인 후 작업 범위 기준 견적
- 철거, 폐기물 처리, 원상복구, 마무리 확인까지 진행 / 시공 후 1년 무상 A/S
- 점포철거비(폐업) 지원금 신청을 도와드림, 전자세금계산서 발행, 정산용 견적서(공사 내역서) 제공
- 서울·경기·인천 수도권 중심, 전국 상담 / 철거 후 인테리어 연계 상담
- 이 밖의 업체 사실(연락 시간, 시공 기간, 집기 매입, 추가금 정책 등)은 **쓰지 않는다**(아직 확인 안 됨).

## 3. 글 구조 (SEO + AEO + GEO)
- 제목(title): 12~45자, **핵심 키워드(keyword)를 앞쪽에** 그대로 넣는다. 질문형이나 "~할 것", "~순서" 형태.
- description: 60~150자, 첫 문장에 핵심 키워드. 검색 결과에 보일 요약.
- lead(첫 문단): 2~3문장으로 **질문에 대한 답을 먼저** 쓴다.
- summary: 핵심 요약 정확히 3줄.
- sections: 소제목 4~8개. **질문형 소제목(?로 끝남) 2개 이상**. 각 소제목 바로 아래 첫 1~2문장은 그 질문의 결론만 읽어도 이해되게.
  - 표 1개 이상(비교표·단계표), 체크리스트 1개 이상을 넣는다.
  - "이런 경우엔 다른 방법이 나을 수 있습니다" 같은 균형 잡힌 내용 1곳.
  - 마지막 소제목 근처에 "상담 전에 준비하면 좋은 것" 목록.
  - 본문(sections) 글자 수 1,500자 이상.
- faq: 3~5개. 본문과 겹쳐도 되지만 문장은 짧고 직접 답한다.
- refs: 확인한 공식 출처.
- related_posts: 이미 있는 다른 글 slug 0~2개(없으면 빈 목록). related_pages: 사이트 페이지 1~3개.

### sections 의 html 에 쓸 수 있는 태그
`<p> <ul> <ol> <li> <strong> <h3> <a href="/..."> <div class="table-wrap"><table><thead><tr><th>…</th></tr></thead><tbody><tr><td>…</td></tr></tbody></table></div> <div class="tip">…</div>`
- 내부 링크는 실제 있는 주소만: `/`, `/support/`, `/demolition/`, `/cases/`, `/interior/`, `/about/`, `/area/`, `/area/seoul/`, `/area/gyeonggi/`, `/area/incheon/`, `/info/<있는 slug>/`
- script·style·iframe·외부 이미지 금지.

## 4. 글 파일 형식 — tools/blog/posts/<slug>.json
```json
{
  "slug": "영문-소문자-하이픈",
  "date": "YYYY-MM-DD (오늘 한국 날짜)",
  "category": "폐업 · 지원금 | 원상복구 | 비용 · 견적 | 업종별 철거 | 사무실 철거 | 주거 철거 | 철거 상식",
  "keyword": "핵심 키워드",
  "title": "제목",
  "description": "요약 설명",
  "cover": "images/ 폴더 안 파일 이름 (아래 목록에서)",
  "cover_alt": "이미지 설명(무엇이 보이는지)",
  "lead": "첫 문단",
  "summary": ["요약1", "요약2", "요약3"],
  "sections": [{"h2": "소제목?", "html": "<p>…</p>"}],
  "faq": [{"q": "질문?", "a": "답"}],
  "refs": [{"title": "자료 이름 (기관)", "url": "https://…"}],
  "related_posts": [],
  "related_pages": [{"href": "/support/", "label": "폐업지원금 안내"}]
}
```

### 대표 이미지(cover)로 쓸 수 있는 사진 — images/
| 파일 | 내용 |
|---|---|
| service_closing_demolition.jpg | 폐업 매장 천장·내부 자재 철거, 폐기물 정리 (예시 이미지) |
| service_store_demolition.jpg | 상가 매장 카운터·진열장 해체 (예시 이미지) |
| service_restoration.jpg | 원상복구를 마친 빈 상가 (예시 이미지) |
| service_office_demolition.jpg | 사무실 유리 파티션 해체 (예시 이미지) |
| img_02_6c6933847304.jpg | 작업자가 내부를 철거하는 현장 |
| img_25_d53feb2a7a7d.jpg | 천장과 내부 설비 철거 진행 현장 |
| img_26_29adb6df02e7.jpg | 원상복구 완료 현장 |
| img_04_83d6e5d49e6f.jpg | 철거 견적 상담 장면 |
| img_24_375eced0b585.jpg | 철거 상담 전 확인사항 안내 이미지 |
| about_inner_new.jpg | 도면·체크리스트·안전모가 놓인 현장 점검 테이블 |
| img_05_63ae4c007a36.jpg / img_06_69e11a3e72fb.jpg | 프랜차이즈 매장 철거 전 / 후 외관 |
| img_07_ec62178d914e.jpg / img_08_07103554deac.jpg | 카페 철거 전 / 원상복구 후 |
| img_09_e7734376c82b.jpg / img_10_ab277e150c9d.jpg | 사무공간 철거 전 / 후 |
| img_15_ebb16d43da74.jpg / img_16_a0921bddb546.jpg | 식당 홀 / 식당 주방 설비 |
| img_17_e31e33e87381.jpg / img_18_4b024390f95c.jpg | 의류매장 / 세탁소 철거 전후 |
| img_20_912e568bdbd9.jpg | 철거 후 인테리어로 새로 꾸민 공간 |
- roadmap 에 정해진 cover 를 우선 쓰고, 바로 앞 글과 같은 사진이면 다른 어울리는 사진으로 바꾼다.

## 5. 발행 절차
1. `TZ=Asia/Seoul date +%F` 로 오늘 날짜 확인.
2. `tools/blog/roadmap.json` 에서 status가 todo이고 시기(season_from ~ season_until)에 맞는 글 중 no가 가장 작은 1편을 고른다. 시기가 지난 글(season_until < 오늘)은 status를 "skipped"로 바꾼다.
3. 기존 글(tools/blog/posts/*.json) 제목과 겹치지 않는지 확인한다. 기존 글 1~2개를 읽어 형식과 말투를 맞춘다.
4. 고객이 물을 하위 질문 8~10개를 먼저 정리하고(roadmap 의 questions 참고), 그것으로 소제목과 FAQ를 만든다.
5. verify 사실을 공식 출처로 확인한다(2절).
6. `tools/blog/posts/<slug>.json` 작성 → `python3 tools/blog/build.py tools/blog/posts/<slug>.json` 이 "완료"를 출력할 때까지 고친다.
7. Playwright(Chromium: /opt/pw-browsers/chromium 또는 설치된 것)로 `python3 -m http.server` 를 띄워 `/info/<slug>/` 를 휴대폰 폭(390px)과 PC 폭에서 열어 본다: 가로 넘침 없음, 이미지 표시, 스크립트 오류 없음.
8. roadmap.json 의 해당 글 status를 "done", `"published": "YYYY-MM-DD"` 추가. 대기열 todo가 3개 이하로 남으면 겹치지 않는 새 주제 5개를 같은 형식으로 추가한다.
9. 변경 파일만 커밋해 main 에 push 한다(이 저장소는 main = 실제 사이트, GitHub Pages).
10. 1~3분 뒤 GitHub Actions(pages build) 성공을 확인한다.

## 6. 보고 (한국어, 짧게)
- 글 제목, 주소(https://onulcheolgeo.kr/info/<slug>/), 이 글이 답하는 대표 질문 3개
- 확인한 출처, 확인 못 해 뺀 내용
- 마지막 줄: "네이버 서치어드바이저 '웹 페이지 수집'과 구글 서치콘솔 'URL 검사 → 색인 생성 요청'에 이 주소를 넣어 주세요."
- 실패하면 어느 단계에서 왜 멈췄는지, push 했는지 여부.
