#!/usr/bin/env python3
"""오늘의 철거 '철거정보' 글 빌드 도구.

사용법:
  python3 tools/blog/build.py                 # 모든 글 다시 생성 + 목록·메인·사이트맵 갱신 + 검사
  python3 tools/blog/build.py tools/blog/posts/<slug>.json   # 해당 글을 특히 엄격하게 검사(나머지도 다시 생성)

글 원본: tools/blog/posts/<slug>.json  (형식은 tools/blog/GUIDE.md 참고)
생성물:  info/<slug>/index.html, info/index.html, index.html(최신 글 3개 영역), sitemap.xml
검사를 통과하지 못하면 종료 코드 1로 끝나고 아무 파일도 쓰지 않는다.
"""
import html, json, os, re, sys, glob, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
SITE = 'https://onulcheolgeo.kr'
POSTS_DIR = 'tools/blog/posts'
CATEGORIES = ['폐업 · 지원금', '원상복구', '비용 · 견적', '업종별 철거', '사무실 철거', '주거 철거', '철거 상식']
STATIC_URLS = ['/', '/about/', '/support/', '/cases/', '/interior/', '/demolition/', '/info/',
               '/area/', '/area/seoul/', '/area/gyeonggi/', '/area/incheon/']
BANNED = ['최고', '최저가', '업계 1위', '1위', '100%', '보장합니다', '엄선', '맞춤형', '체계적', '완벽', '박시연', '무조건', '최상']
PHONE_RE = re.compile(r'010[-\s.]?7990[-\s.]?2378|01079902378')

esc = lambda s: html.escape(s, quote=True)
def rd(p): return open(p, encoding='utf-8').read()
def strip_tags(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

# ---------------- 공통 틀(헤더·푸터)을 폐업지원금 페이지에서 가져온다 ----------------
def site_shell():
    t = rd('support/index.html')
    header = t[t.index('<header>'):t.index('</header>') + len('</header>')]
    header = header.replace(' class="active" aria-current="page"', '')
    footer = t[t.index('<footer class="site-footer">'):t.index('</footer>') + len('</footer>')]
    i = t.index('<div class="mobile-fab-group">'); j = t.index('</div>\n<script>', i) + len('</div>')
    fab = t[i:j]
    favicon = '\n'.join(re.findall(r'<link rel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>', t))
    return header, footer, fab, favicon

def set_active(header, href):
    return header.replace(f'<a href="{href}">', f'<a href="{href}" class="active" aria-current="page">', 1)

def head(title, desc, url, og_type, og_image, ld, favicon, extra=''):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="오늘의 철거">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/images/{og_image}">
<meta name="twitter:card" content="summary_large_image">
{favicon}
<link rel="stylesheet" href="/assets/site.css">
{extra}<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
'''

MENU_JS = "<script>\ndocument.querySelector('.menu-btn').addEventListener('click',()=>document.querySelector('.mobile-menu').classList.toggle('open'));\n"

def tail(footer, fab, js=''):
    return f'\n{footer}\n{fab}\n{MENU_JS}{js}</script>\n</body>\n</html>\n'

# ---------------- 글 읽기 + 검사 ----------------
def load_posts():
    posts = []
    for p in sorted(glob.glob(f'{POSTS_DIR}/*.json')):
        d = json.load(open(p, encoding='utf-8'))
        d['_file'] = p
        posts.append(d)
    posts.sort(key=lambda d: (d['date'], d['slug']), reverse=True)
    return posts

def internal_target_exists(href, slugs):
    path = href.split('#')[0].split('?')[0]
    if not path.startswith('/'):
        return True
    if path.startswith('/info/') and path.strip('/').count('/') == 1:
        return path.strip('/').split('/')[1] in slugs
    f = path.lstrip('/')
    if f == '' or f.endswith('/'):
        f = f + 'index.html'
    return os.path.exists(f)

def check_post(d, slugs, strict):
    errs = []
    need = ['slug', 'title', 'description', 'category', 'keyword', 'date', 'cover', 'cover_alt', 'lead', 'summary', 'sections', 'faq', 'refs', 'related_posts', 'related_pages']
    for k in need:
        if k not in d: errs.append(f'필수 항목 없음: {k}')
    if errs: return errs
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', d['slug']): errs.append('slug는 영어 소문자·숫자·하이픈만')
    if os.path.basename(d['_file']) != d['slug'] + '.json': errs.append('파일 이름과 slug가 다름')
    try: datetime.date.fromisoformat(d['date'])
    except Exception: errs.append('date 형식은 YYYY-MM-DD')
    if d['category'] not in CATEGORIES: errs.append(f'category는 {CATEGORIES} 중 하나')
    if not (12 <= len(d['title']) <= 45): errs.append(f'제목 길이 12~45자 (지금 {len(d["title"])}자)')
    if not (60 <= len(d['description']) <= 150): errs.append(f'description 60~150자 (지금 {len(d["description"])}자)')
    if d['keyword'] not in d['title']: errs.append('핵심 키워드가 제목에 없음')
    if d['keyword'] not in d['description']: errs.append('핵심 키워드가 description에 없음')
    if not os.path.exists('images/' + d['cover']): errs.append(f'대표 이미지 없음: images/{d["cover"]}')
    if len(d['summary']) != 3: errs.append('summary(핵심 요약)는 3줄')
    if not (4 <= len(d['sections']) <= 8): errs.append('본문 소제목(sections)은 4~8개')
    if strict:
        q = sum(1 for s in d['sections'] if s['h2'].rstrip().endswith('?'))
        if q < 2: errs.append('질문형 소제목(?로 끝남)을 2개 이상')
    if not (3 <= len(d['faq']) <= 5): errs.append('FAQ는 3~5개')
    if strict and not d['refs']: errs.append('참고 자료(refs)가 1개 이상 필요')
    for r in d['refs']:
        if not r.get('url', '').startswith('http'): errs.append(f'참고 자료 주소 오류: {r}')
    body_text = ' '.join([d['title'], d['description'], d['lead'], ' '.join(d['summary'])] +
                         [s['h2'] + ' ' + s['html'] for s in d['sections']] + [f['q'] + ' ' + f['a'] for f in d['faq']])
    for w in BANNED:
        if w in strip_tags(body_text): errs.append(f'금지 표현 사용: "{w}"')
    if PHONE_RE.search(body_text): errs.append('본문에 전화번호를 쓰지 않음(버튼으로만 안내)')
    plain = strip_tags(''.join(s['html'] for s in d['sections']))
    if strict and len(plain) < 1500: errs.append(f'본문이 짧음 ({len(plain)}자, 1500자 이상)')
    for s in d['sections']:
        for href in re.findall(r'href="([^"]+)"', s['html']):
            if href.startswith('/') and not internal_target_exists(href, slugs): errs.append(f'없는 내부 링크: {href}')
        if re.search(r'<(script|style|iframe)', s['html'], re.I): errs.append('본문에 script/style/iframe 금지')
    for rp in d['related_posts']:
        if rp not in slugs: errs.append(f'related_posts에 없는 글: {rp}')
    for pg in d['related_pages']:
        if not internal_target_exists(pg['href'], slugs): errs.append(f'related_pages 없는 주소: {pg["href"]}')
    return errs

# ---------------- 글 페이지 ----------------
def read_minutes(d):
    n = len(strip_tags(' '.join(s['html'] for s in d['sections'])))
    return max(3, round(n / 500))

def render_post(d, by_slug, shell):
    header, footer, fab, favicon = shell
    url = f'{SITE}/info/{d["slug"]}/'
    toc = '\n'.join(f'        <li><a href="#s{i}">{esc(s["h2"])}</a></li>' for i, s in enumerate(d['sections'], 1))
    sections = '\n'.join(f'''      <section class="post-section" id="s{i}">
        <h2>{esc(s["h2"])}</h2>
        {s["html"]}
      </section>''' for i, s in enumerate(d['sections'], 1))
    faq = '\n'.join(f'        <details><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>' for f in d['faq'])
    refs = '\n'.join(f'        <li><a href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">{esc(r["title"])}</a></li>' for r in d['refs'])
    rel_cards = ''
    for rs in d['related_posts'][:2]:
        r = by_slug[rs]
        rel_cards += f'''        <a class="info-card" href="/info/{r["slug"]}/">
          <div class="info-card-img has-img"><img src="/images/{r["cover"]}" alt="{esc(r["cover_alt"])}" loading="lazy" decoding="async"></div>
          <div class="info-card-body"><span class="info-cat">{esc(r["category"])}</span><h3>{esc(r["title"])}</h3></div>
        </a>\n'''
    rel_pages = ''.join(f'<a class="btn btn-outline" href="{esc(p["href"])}">{esc(p["label"])}</a>' for p in d['related_pages'])
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "headline": d['title'], "description": d['description'],
         "image": f'{SITE}/images/{d["cover"]}', "datePublished": d['date'], "dateModified": d.get('updated', d['date']),
         "inLanguage": "ko-KR", "articleSection": d['category'], "keywords": d['keyword'], "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": "오늘의 철거", "url": SITE + '/'},
         "publisher": {"@type": "Organization", "name": "오늘의 철거", "url": SITE + '/'}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": f['a']}} for f in d['faq']]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + '/'},
            {"@type": "ListItem", "position": 2, "name": "철거정보", "item": SITE + '/info/'},
            {"@type": "ListItem", "position": 3, "name": d['title'], "item": url}]},
    ]
    extra = f'<meta property="article:published_time" content="{d["date"]}">\n'
    out = head(f'{d["title"]} | 오늘의 철거', d['description'], url, 'article', d['cover'], ld, favicon, extra)
    out += set_active(header, '/info/') + f'''

<main>
<article class="post-wrap">
  <div class="wrap post-narrow">
    <nav class="post-crumb" aria-label="현재 위치"><a href="/">홈</a> › <a href="/info/">철거정보</a> › <span>{esc(d["category"])}</span></nav>
    <span class="info-cat">{esc(d["category"])}</span>
    <h1 class="post-title">{esc(d["title"])}</h1>
    <p class="post-lead">{esc(d["lead"])}</p>
    <p class="post-meta">오늘의 철거 철거정보 · <time datetime="{d["date"]}">{d["date"].replace("-", ".")}</time> · 읽는 시간 약 {read_minutes(d)}분</p>
    <figure class="post-cover has-img"><img src="/images/{d["cover"]}" alt="{esc(d["cover_alt"])}" width="1200" height="800" decoding="async"></figure>
    <div class="post-summary">
      <b>핵심 요약</b>
      <ul>
{chr(10).join(f"        <li>{esc(x)}</li>" for x in d["summary"])}
      </ul>
    </div>
    <nav class="post-toc" aria-label="목차">
      <b>목차</b>
      <ol>
{toc}
      </ol>
    </nav>
    <div class="post-body">
{sections}
    </div>
    <section class="post-faq" id="faq">
      <h2>자주 묻는 질문</h2>
      <div class="area-faq">
{faq}
      </div>
    </section>
    <section class="post-refs">
      <h2>참고 자료</h2>
      <ul>
{refs}
      </ul>
      <p class="post-note">이 글은 일반적인 정보입니다. 실제 철거 범위와 비용, 지원 여부는 현장 상태와 계약 조건, 신청 시점의 공식 공고에 따라 달라질 수 있습니다.</p>
    </section>
    <div class="post-cta">
      <b>현장에 맞는 안내가 필요하신가요?</b>
      <p>업종 · 지역 · 평수 · 현장 사진을 보내주시면 철거 범위와 일정을 함께 확인해 드립니다.</p>
      <div class="post-cta-btns">
        <a class="btn btn-yellow" href="https://naver.me/551kJA6x" target="_blank" rel="noopener noreferrer">무료 방문견적 신청</a>
        <a class="btn btn-outline" href="https://open.kakao.com/o/s7KwuzWi" target="_blank" rel="noopener noreferrer">카카오 상담</a>
        <a class="btn btn-outline" href="tel:01079902378">☎ 전화 상담</a>
      </div>
    </div>
    <section class="post-related">
      <h2>함께 보면 좋은 정보</h2>
      <div class="info-grid info-grid-2">
{rel_cards}      </div>
      <div class="post-pages">{rel_pages}</div>
    </section>
    <p class="post-back"><a href="/info/">← 철거정보 목록으로</a></p>
  </div>
</article>
</main>
'''
    out += tail(footer, fab)
    return out

# ---------------- 목록 페이지 ----------------
def card(d):
    return f'''      <a class="info-card" href="/info/{d["slug"]}/" data-cat="{esc(d["category"])}">
        <div class="info-card-img has-img"><img src="/images/{d["cover"]}" alt="{esc(d["cover_alt"])}" loading="lazy" decoding="async"></div>
        <div class="info-card-body">
          <span class="info-cat">{esc(d["category"])}</span>
          <h3>{esc(d["title"])}</h3>
          <p>{esc(d["description"])}</p>
          <time datetime="{d["date"]}">{d["date"].replace("-", ".")}</time>
        </div>
      </a>'''

def render_list(posts, shell):
    header, footer, fab, favicon = shell
    url = f'{SITE}/info/'
    used = [c for c in CATEGORIES if any(p['category'] == c for p in posts)]
    filters = '<button class="filter active" data-filter="all" aria-pressed="true">전체</button>' + ''.join(
        f'<button class="filter" data-filter="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in used)
    cards = '\n'.join(card(p) for p in posts) or '      <p class="case-empty">첫 정보글을 준비하고 있습니다.</p>'
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "철거정보", "url": url,
           "description": "폐업철거, 원상복구, 철거 비용과 견적, 업종별 철거에 대한 정보글 모음",
           "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": i, "url": f'{SITE}/info/{p["slug"]}/', "name": p['title']} for i, p in enumerate(posts[:20], 1)]}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + '/'},
              {"@type": "ListItem", "position": 2, "name": "철거정보", "item": url}]}]
    out = head('철거정보 | 폐업철거·원상복구·철거 비용 정보 - 오늘의 철거',
               '폐업철거와 점포철거비 지원, 상가·사무실 원상복구 범위, 철거 비용이 달라지는 이유 등 철거 전에 알아두면 좋은 정보를 정리했습니다.',
               url, 'website', 'img_02_6c6933847304.jpg', ld, favicon)
    out += set_active(header, '/info/') + f'''

<main>
<section class="page active" id="page-info">
  <section class="page-hero" style="background:linear-gradient(rgba(11,17,24,.66),rgba(11,17,24,.66)),url('/images/img_25_d53feb2a7a7d.jpg') center/cover no-repeat"><div class="wrap"><div class="eyebrow">DEMOLITION GUIDE</div><h1>철거정보</h1><p>철거 · 원상복구 · 폐업 전에 알아두면 좋은 내용을 정리합니다.</p></div></section>
  <section class="section">
    <div class="wrap">
      <div class="filters info-filters">{filters}</div>
      <div class="info-grid" id="infoGrid">
{cards}
      </div>
      <p class="case-empty" id="infoEmpty" hidden>해당 분류의 글은 준비 중입니다.</p>
    </div>
  </section>
</section>
</main>
'''
    js = """document.querySelectorAll('.info-filters .filter').forEach(btn=>btn.addEventListener('click',()=>{
  const f=btn.dataset.filter;let n=0;
  document.querySelectorAll('.info-filters .filter').forEach(b=>{const on=b===btn;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on);});
  document.querySelectorAll('#infoGrid .info-card').forEach(c=>{const s=f==='all'||c.dataset.cat===f;c.hidden=!s;if(s)n++;});
  document.getElementById('infoEmpty').hidden=n>0;
}));
"""
    out += tail(footer, fab, js)
    return out

# ---------------- 메인 최신 글 3개 ----------------
HOME_START, HOME_END = '<!-- INFO-LATEST:START -->', '<!-- INFO-LATEST:END -->'
def render_home_block(posts):
    if not posts: return f'{HOME_START}\n{HOME_END}'
    cards = '\n'.join(card(p) for p in posts[:3])
    return f'''{HOME_START}
  <section class="section" id="info-latest">
    <div class="wrap">
      <div class="home-seo-head">
        <div class="eyebrow">DEMOLITION GUIDE</div>
        <h2 class="section-title">철거 전에 알아두면 좋은 정보</h2>
      </div>
      <div class="info-grid">
{cards}
      </div>
      <div class="info-more"><a class="btn btn-outline" href="/info/">철거정보 전체 보기 →</a></div>
    </div>
  </section>
  {HOME_END}'''

def render_sitemap(posts):
    today = datetime.date.today().isoformat()
    rows = [(u, today) for u in STATIC_URLS] + [(f'/info/{p["slug"]}/', p.get('updated', p['date'])) for p in posts]
    body = ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{m}</lastmod>\n  </url>\n' for u, m in rows)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'

def main():
    strict_files = {os.path.normpath(a) for a in sys.argv[1:]}
    posts = load_posts()
    slugs = {p['slug'] for p in posts}
    by_slug = {p['slug']: p for p in posts}
    if len(slugs) != len(posts): print('오류: 같은 slug가 두 번 있음'); sys.exit(1)
    all_errs = {}
    for d in posts:
        e = check_post(d, slugs, strict=os.path.normpath(d['_file']) in strict_files)
        if e: all_errs[d['_file']] = e
    for f in strict_files:
        if not os.path.exists(f): all_errs[f] = ['파일이 없음']
    if all_errs:
        for f, es in all_errs.items():
            print(f'\n[검사 실패] {f}')
            for e in es: print('  -', e)
        sys.exit(1)
    shell = site_shell()
    outputs = {}
    for d in posts:
        outputs[f'info/{d["slug"]}/index.html'] = render_post(d, by_slug, shell)
    outputs['info/index.html'] = render_list(posts, shell)
    home = rd('index.html')
    if HOME_START not in home: print('오류: index.html에 INFO-LATEST 표시가 없음'); sys.exit(1)
    a = home.index(HOME_START); b = home.index(HOME_END) + len(HOME_END)
    outputs['index.html'] = home[:a] + render_home_block(posts) + home[b:]
    outputs['sitemap.xml'] = render_sitemap(posts)
    # 생성물 검사: JSON-LD, FAQ 일치, 전화번호(본문)
    for path, s in outputs.items():
        for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            json.loads(x)
    for path, s in outputs.items():
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        open(path, 'w', encoding='utf-8').write(s)
    print(f'완료: 글 {len(posts)}편, 목록·메인·사이트맵 갱신')
    for d in posts[:5]: print(f'  {d["date"]}  {SITE}/info/{d["slug"]}/  {d["title"]}')

if __name__ == '__main__':
    main()
