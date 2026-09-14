#!/usr/bin/env python3
"""Build SwipeLibrary.html (the operator's visual browser) from CONCEPT_LIBRARY.md.
The HTML is DERIVED: never edit it by hand. Source of truth = CONCEPT_LIBRARY.md (the generator reads that).
Run: python3 tools/build_browser.py   (the repo's pre-commit hook runs it on every commit)
"""
import re, sys, os, json, html, datetime
REPO=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.expanduser('~/.claude/skills/static-remix/references/CONCEPT_LIBRARY.md')
OUT=os.path.join(REPO,'SwipeLibrary.html')
RAW='https://raw.githubusercontent.com/YassineCoyote/novexa-swipe-library/main/swipe_%02d.jpg'
t=open(SRC,encoding='utf-8').read()
m=re.search(r'\((\d+) direct statics\)',t); total=int(m.group(1)) if m else 0
tiers={}
for tier,rng in re.findall(r'\| \*\*(PROVEN|UNPROVEN|BANNED)\*\* \| ([^|]*?) \|',t): tiers[tier]=re.sub(r'\*|\(.*?\)','',rng).strip()
entries={}; fam=None
for line in t.splitlines():
    h=re.match(r'^## (.+?)\s+\(',line)
    if h: fam=h.group(1).strip(); continue
    e=re.match(r'^- \*\*#(\d+) \[([A-D])\] (.+?)\*\* — `swipe_(\d+)\.jpg`(?: \(([^)]*)\))?(?: — (.*))?$',line)
    if e and fam:
        n=int(e.group(1)); entries[n]=dict(n=n,score=e.group(2),title=e.group(3),family=fam,ref=e.group(5) or '',text=(e.group(6) or '').strip(),eye='',psych='')
        cur=n; continue
    s=re.match(r'^\s+- (EYE PATH|PSYCH ANGLE): (.*)$',line)
    if s and entries: entries[cur]['eye' if s.group(1)=='EYE PATH' else 'psych']=s.group(2).strip()
missing=[i for i in range(1,total+1) if i not in entries]
fams=[]; [fams.append(v['family']) for v in entries.values() if v['family'] not in fams]
col={'A':'#1a7f37','B':'#0969da','C':'#9a6700','D':'#cf222e'}
lab={'A':'A STEAL IT','B':'B SLOT IT, STRIPPED','C':'C RESERVE','D':'D NEVER'}
def tier_of(n):
    if n in (4,12,13,23,24,25,26,30): return 'BANNED'
    lo,hi=[int(x) for x in re.findall(r'\d+',tiers.get('PROVEN','31-0'))[:2]]
    return 'PROVEN' if lo<=n<=hi else 'UNPROVEN'
cards=[]
for n in sorted(entries):
    v=entries[n]; u=RAW%n
    md=lambda s: re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',html.escape(s)).replace('&lt;b&gt;','<b>').replace('&lt;/b&gt;','</b>')
    metas=[('FAMILY',v['family']),('TIER',tier_of(n))]
    if v['eye']: metas.append(('EYE PATH',v['eye']))
    if v['psych']: metas.append(('PSYCH ANGLE',v['psych']))
    if v['ref']: metas.append(('SOURCE',v['ref']))
    body=''.join(f'<p class="meta"><span class="lab">{k}</span> {md(x)}</p>' for k,x in metas)
    if v['text']: body+=f'<p class="tear">{md(v["text"])}</p>'
    cards.append(f'''<article class="swipe" data-n="{n}" data-fam="{html.escape(v['family'])}" data-score="{v['score']}" data-tier="{tier_of(n)}" data-txt="{html.escape((v['title']+' '+v['text']+' '+v['psych']).lower())}">
<div class="thumb"><img loading="lazy" src="{u}" alt="Swipe {n} {html.escape(v['title'])}"></div>
<div class="body"><div class="top"><span class="num">#{n}</span><span class="score" style="background:{col[v['score']]}">{lab[v['score']]}</span></div>
<h2>{html.escape(v['title'])}</h2>{body}<div class="urlrow"><input class="url" readonly value="{u}" onclick="this.select()"></div></div></article>''')
opts=''.join(f'<option>{html.escape(f)}</option>' for f in fams)
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>novexa-swipe-library — {total} direct statics</title>
<style>
body{{margin:0;font:14px/1.45 -apple-system,Helvetica,Arial,sans-serif;background:#f6f8fa;color:#1f2328}}
header{{background:#fff;border-bottom:1px solid #d0d7de;padding:16px 24px;position:sticky;top:0;z-index:2}}
h1{{margin:0 0 6px;font-size:20px}} .note{{color:#57606a;margin:0 0 10px;font-size:13px}}
.controls{{display:flex;gap:8px;flex-wrap:wrap}} .controls input,.controls select{{padding:6px 8px;border:1px solid #d0d7de;border-radius:6px;font-size:13px}}
#count{{align-self:center;color:#57606a}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:16px 24px}}
.swipe{{background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden;display:flex;flex-direction:column}}
.thumb{{background:#eaeef2;display:flex;justify-content:center;align-items:center;min-height:240px}} .thumb img{{max-width:100%;max-height:420px;display:block}}
.body{{padding:10px 12px 12px}} .top{{display:flex;justify-content:space-between;align-items:center}} .num{{font-weight:700;font-size:16px}}
.score{{color:#fff;font-size:11px;font-weight:700;padding:2px 7px;border-radius:10px}} h2{{font-size:14px;margin:6px 0 8px;letter-spacing:.02em}}
.meta{{margin:2px 0;font-size:12px}} .lab{{display:inline-block;min-width:82px;color:#57606a;font-weight:700;font-size:10px;letter-spacing:.05em}}
.tear{{font-size:12px;color:#424a53;margin:6px 0 0;border-top:1px solid #eaeef2;padding-top:6px}}
.url{{width:100%;box-sizing:border-box;font-size:10px;color:#57606a;border:1px solid #eaeef2;border-radius:4px;padding:3px 5px;margin-top:8px}}
.hidden{{display:none}}
</style></head><body>
<header><h1>novexa-swipe-library — {total} direct statics</h1>
<p class="note">GENERATED FILE — built from <code>static-remix/references/CONCEPT_LIBRARY.md</code> by <code>tools/build_browser.py</code> on {datetime.date.today()}. Do not edit by hand; the generator reads CONCEPT_LIBRARY.md, this page is for the operator's eyes only. Tiers: PROVEN {tiers.get('PROVEN','?')} · UNPROVEN {tiers.get('UNPROVEN','?')} · BANNED {tiers.get('BANNED','?')}. Direct statics only — natives live in native-image-ads.</p>
<div class="controls"><input id="q" placeholder="filter (number, title, teardown, angle)…" oninput="filt()">
<select id="sc" onchange="filt()"><option value="">all scores</option><option>A</option><option>B</option><option>C</option><option>D</option></select>
<select id="fw" onchange="filt()"><option value="">all families</option>{opts}</select>
<select id="ti" onchange="filt()"><option value="">all tiers</option><option>PROVEN</option><option>UNPROVEN</option><option>BANNED</option></select>
<span id="count"></span></div></header>
<main class="grid" id="grid">{''.join(cards)}</main>
<script>
function filt(){{const q=document.getElementById('q').value.toLowerCase(),sc=document.getElementById('sc').value,fw=document.getElementById('fw').value,ti=document.getElementById('ti').value;let k=0;
document.querySelectorAll('.swipe').forEach(c=>{{const ok=(!q||c.dataset.n===q.replace('#','')||c.dataset.txt.includes(q))&&(!sc||c.dataset.score===sc)&&(!fw||c.dataset.fam===fw)&&(!ti||c.dataset.tier===ti);c.classList.toggle('hidden',!ok);if(ok)k++;}});
document.getElementById('count').textContent=k+' / {total}';}}filt();
</script></body></html>'''
open(OUT,'w',encoding='utf-8').write(page)
print(f'SwipeLibrary.html: {len(entries)} entries of {total} declared; families {len(fams)}; missing numbers: {missing or "none"}')
if missing: sys.exit(1)
# Install the hook on a fresh clone:  cp tools/pre-commit.hook .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
