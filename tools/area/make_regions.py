"""인천 지역 페이지를 틀로 삼아 나머지 지역 페이지를 만든다.
사용: python3 tools/area/make_regions.py  (area/<slug>/index.html 생성)"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL = open(os.path.join(ROOT, 'area/incheon/index.html'), encoding='utf-8').read()
UPDATED = '2026-11-16'

def g(prefix, names):
    return [f'{prefix} {n}' if prefix else n for n in names]

REGIONS = [
 dict(slug='gangwon', short='강원', full='강원특별자치도', en='GANGWON', unit='시·군', hl='춘천·원주·강릉',
      hero='춘천 · 원주 · 강릉 · 속초를 비롯한 강원 18개 시·군의',
      ex='예: 원주시, 강릉, 속초',
      areas=['춘천시','원주시','강릉시','동해시','태백시','속초시','삼척시','홍천군','횡성군','영월군','평창군','정선군','철원군','화천군','양구군','인제군','고성군','양양군'],
      note=None, alias={}),
 dict(slug='chungcheong', short='대전·세종·충청', full='대전·세종·충북·충남', en='CHUNGCHEONG', unit='시·군·구', hl='대전·세종·천안·청주',
      hero='대전 · 세종 · 천안 · 청주를 비롯한 충청권 32개 시·군·구의',
      ex='예: 유성구, 천안, 청주',
      areas=g('대전',['동구','중구','서구','유성구','대덕구'])+['세종시']+g('충북',['청주시','충주시','제천시','보은군','옥천군','영동군','증평군','진천군','괴산군','음성군','단양군'])+g('충남',['천안시','공주시','보령시','아산시','서산시','논산시','계룡시','당진시','금산군','부여군','서천군','청양군','홍성군','예산군','태안군']),
      note=None, alias={'세종': ['세종시']}),
 dict(slug='jeolla', short='광주·전라', full='광주·전남·전북', en='JEOLLA', unit='시·군·구', hl='광주·전주·순천·여수',
      hero='광주 · 전주 · 순천 · 여수를 비롯한 광주·전남·전북 41개 시·군·구의',
      ex='예: 광산구, 전주, 여수',
      areas=g('광주',['동구','서구','남구','북구','광산구'])+g('전남',['목포시','여수시','순천시','나주시','광양시','담양군','곡성군','구례군','고흥군','보성군','화순군','장흥군','강진군','해남군','영암군','무안군','함평군','영광군','장성군','완도군','진도군','신안군'])+g('전북',['전주시','군산시','익산시','정읍시','남원시','김제시','완주군','진안군','무주군','장수군','임실군','순창군','고창군','부안군']),
      note=('2026년 7월부터 광주와 전남이 하나로 통합되었습니다',
            '2026년 7월 1일 광주광역시와 전라남도가 전남광주통합특별시로 출범했습니다. 광주 5개 구와 전남 22개 시·군 이름은 그대로 쓰이니, 아래 목록에서 평소 쓰던 지역 이름으로 찾으시면 됩니다. 전북은 전북특별자치도입니다.'),
      alias={}),
 dict(slug='gyeongbuk', short='대구·경북', full='대구·경북', en='GYEONGBUK', unit='시·군·구', hl='대구·포항·구미·경산',
      hero='대구 · 포항 · 구미 · 경산을 비롯한 대구·경북 31개 시·군·구의',
      ex='예: 수성구, 포항, 구미',
      areas=g('대구',['중구','동구','서구','남구','북구','수성구','달서구','달성군','군위군'])+g('경북',['포항시','경주시','김천시','안동시','구미시','영주시','영천시','상주시','문경시','경산시','의성군','청송군','영양군','영덕군','청도군','고령군','성주군','칠곡군','예천군','봉화군','울진군','울릉군']),
      note=('군위군은 대구광역시입니다',
            '군위군은 2023년 7월 1일부터 경북에서 대구광역시로 편입되었습니다. 대구·경북 어느 쪽으로 검색하셔도 상담할 수 있습니다.'),
      alias={'군위': ['대구 군위군']}),
 dict(slug='gyeongnam', short='부산·울산·경남', full='부산·울산·경남', en='GYEONGNAM', unit='시·군·구', hl='부산·울산·창원·김해',
      hero='부산 · 울산 · 창원 · 김해를 비롯한 부산·울산·경남 39개 시·군·구의',
      ex='예: 해운대구, 창원, 김해',
      areas=g('부산',['중구','서구','동구','영도구','부산진구','동래구','남구','북구','해운대구','사하구','금정구','강서구','연제구','수영구','사상구','기장군'])+g('울산',['중구','남구','동구','북구','울주군'])+g('경남',['창원시','진주시','통영시','사천시','김해시','밀양시','거제시','양산시','의령군','함안군','창녕군','고성군','남해군','하동군','산청군','함양군','거창군','합천군']),
      note=None, alias={'서면': ['부산 부산진구'], '센텀': ['부산 해운대구'], '마산': ['경남 창원시'], '진해': ['경남 창원시']}),
 dict(slug='jeju', short='제주', full='제주특별자치도', en='JEJU', unit='시', hl='제주시·서귀포시',
      hero='제주시와 서귀포시의',
      ex='예: 제주시, 서귀포',
      areas=['제주시','서귀포시'],
      note=None, alias={'애월': ['제주시'], '노형': ['제주시'], '연동': ['제주시'], '중문': ['서귀포시'], '성산': ['서귀포시']}),
]

def rep(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        sys.exit(f'틀 문자열 개수 다름({n}≠{count}): {old[:60]}')
    return s.replace(old, new)

def make(r):
    s, short, unit, n = TPL, r['short'], r['unit'], len(r['areas'])
    jong = unit.endswith('군')
    eul, euro = ('을', '으로') if jong else ('를', '로')
    url = f"https://onulcheolgeo.kr/area/{r['slug']}/"
    s = rep(s, '<title>인천 철거업체 | 송도·부평·구월 상가·사무실 철거, 원상복구 - 오늘의 철거</title>',
            f"<title>{short} 철거업체 | {r['hl']} 상가·사무실 철거, 원상복구 - 오늘의 철거</title>")
    s = rep(s, '인천 전 지역(11개 구·군)', f"{short} 전 지역({n}개 {unit})")
    s = s.replace('https://onulcheolgeo.kr/area/incheon/', url)
    s = rep(s, '"areaServed": {"@type": "City", "name": "인천광역시"}',
            '"areaServed": ' + json.dumps({"@type": "AdministrativeArea", "name": r['full']}, ensure_ascii=False))
    s = rep(s, '인천 11개 구·군 모두 상담합니다. 구·군 이름과', f"{short} {n}개 {unit} 모두 상담합니다. {unit} 이름과", 2)
    s = rep(s, 'INCHEON DEMOLITION', f"{r['en']} DEMOLITION")
    s = rep(s, '인천 원도심부터 송도 · 청라 · 검단 신도시까지 상가', f"{r['hero']} 상가")
    s = re.sub(r'최종 업데이트 \d{4}-\d{2}-\d{2}', f'최종 업데이트 {UPDATED}', s)
    s = rep(s, '업종, 구·군 이름, 평수', f'업종, {unit} 이름, 평수')
    # 후기: 수도권 현장 후기임을 그대로 밝힌다
    s = rep(s, '<h2 class="sec-title">인천 · 수도권 고객 후기</h2>\n        <p class="sec-sub">오늘의 철거와 함께한 고객님들이 남겨 주신 후기입니다.</p>',
            '<h2 class="sec-title">오늘의 철거 고객 후기</h2>\n        <p class="sec-sub">수도권 현장에서 오늘의 철거와 함께한 고객님들이 남겨 주신 후기입니다.</p>')
    rv = re.search(r'<div class="reviews">.*?</div>\n', s, re.S)
    reviews = rv.group(0)
    s = s.replace(reviews, '@@REVIEWS@@')
    # 지역 목록
    s = rep(s, 'INCHEON 11 AREAS', f"{r['en']} {n} AREAS")
    s = rep(s, '인천 11개 구·군 철거 상담', f'{short} <span style="white-space:nowrap">{n}개 {unit}</span> 철거 상담')
    s = rep(s, '찾으시는 구·군을 검색해 보세요. 인천 모든 구·군에서', f'찾으시는 {unit}{eul} 검색해 보세요. {short} 모든 {unit}에서')
    s = rep(s, 'placeholder="구·군 이름으로 찾기 (예: 연수구, 송도, 중구)"', f'placeholder="{unit} 이름으로 찾기 ({r["ex"]})"')
    note = re.search(r'\s*<div class="region-note">.*?</div>', s).group(0)
    s = s.replace(note, f'\n      <div class="region-note"><b>{r["note"][0]}</b>{r["note"][1]}</div>' if r['note'] else '')
    lis = ''.join(f'<li>{a}</li>' for a in r['areas'])
    s = re.sub(r'(<ul class="districts" id="gu-list">\s*).*?(\s*</ul>)', lambda m: m.group(1)+lis+m.group(2), s, flags=re.S)
    near = '\n'.join(f'        <a class="btn btn-outline" href="{h}">{t}</a>' for h, t in
                     [('/area/seoul/', '서울 철거 보기'), ('/area/', '전국 지역별 철거 보기')])
    s = re.sub(r'(<div class="near">\n).*?(\n      </div>)', lambda m: m.group(1)+near+m.group(2), s, flags=re.S)
    s = re.sub(r'var alias=\{.*?\};', 'var alias=' + json.dumps(r['alias'], ensure_ascii=False) + ';', s)
    s = rep(s, '해당 구·군으로 상담하시면', f'해당 {unit}{euro} 상담하시면')
    s = rep(s, '<p>구·군 이름 · 평수', f'<p>{unit} 이름 · 평수')
    # 나머지 '인천' → 지역명 (푸터 제외)
    head, foot = s.split('<footer class="site-footer">')
    head = head.replace('인천', short)
    s = head + '<footer class="site-footer">' + foot
    s = s.replace('@@REVIEWS@@', reviews)
    s = s.replace('<li aria-current="page">'+short+'</li>', '<li aria-current="page">'+short+'</li>')
    left = [m for m in re.findall(r'.{0,30}(?:인천|incheon|구·군).{0,30}', head)]
    if left:
        sys.exit(f"{r['slug']}: 남은 인천 표현 {left}")
    d = os.path.join(ROOT, 'area', r['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(s)
    print('생성', r['slug'], n, '곳')

for r in REGIONS:
    make(r)
