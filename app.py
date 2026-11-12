"""
🎂 Sunita Didi's Birthday Website — Streamlit
Run:  pip install -r requirements.txt  &&  streamlit run app.py

A personal birthday page for Sunita Didi (born 13 Nov 1988), from Piyush.

Optional extras placed next to app.py:
    photos/   -> any .jpg/.png/.webp files are auto-added to the memory wall
    song.mp3  -> auto-loaded as the party song
"""

import base64
import datetime as dt
import html
import io
import json
import math
import random
import re
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# --------------------------------------------------------------------------- #
# Page config
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Happy Birthday, Sunita Didi! 🎂",
    page_icon="🎂",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "photos"
SONG_FILE = BASE_DIR / "song.mp3"

THEME = dict(
    bg1="#ff9a9e", bg2="#fad0c4", bg3="#a18cd1",
    accent="#ff4f81", accent2="#7b2ff7", text="#2d1b3d",
    card="rgba(255,255,255,.72)",
    confetti=["#ff4f81", "#7b2ff7", "#ffd166", "#06d6a0", "#118ab2", "#ff9f1c"],
)

# --------------------------------------------------------------------------- #
# Sunita Didi's details
# --------------------------------------------------------------------------- #
NAME = "Sunita Diiiduuuuuu"
DOB = dt.date(1988, 11, 13)
FROM_NAME = "Jintu (your KUTTA)"

MESSAGE = """Happiest Birthday to myyyy Diduuuuuu! ❤️🫂🧿

I honestly don't know where to begin because no words could ever truly express how grateful I am to have you in my life. Some people come into our lives and make them a little better, but you came into mine and made it a whole lot more beautiful. ❤️

I hope you always remember how special you are, how much you mean to me and how deeply you are loved. You deserve all the happiness, love, peace, success and magic that this world has to offer. May every little wish of yours come true, and may life always give you a thousand reasons to smile.

And Diduuu, one thing I want you to promise me is that you'll **always be YOU.** Just be the way you are, with all your little quirks, your madness, your craziness, your warmth and everything that makes you who you are. Never ever feel the need to change yourself. I love you exactly the way you are and I wouldn't want it any other way. ❤️

Alsooooo, pleaseeeee, never ever get bored of me! No matter how annoying I get, how many times I trouble you or how many silly things I do, I hope you always keep your KUTTA around. Because you genuinely mean the world to me. **YOU ARE MY EVERYTHING, DIDUUU!** 🫀

I want you to know that no matter what life brings, you will always have your KUTTA by your side. In your happiest moments, in your difficult days, through every misunderstanding, every silly fight and every little celebration, I'll always be there. It's never you versus me; it's always us against whatever comes our way.

Thank you for being YOU, Diduuu. Thank you for your love, your care, your warmth and for making a place in your life and heart for me. I pray that God protects your smile, blesses you with endless happiness and gives you everything your heart has ever wished for.

And pleaseeeee, never forget that you have a KUTTTA who loves you more than words could ever express. No matter where life takes us, one thing will never change: you'll always have me, cheering for you, praying for you, annoying you and loving you endlessly.

**Happy Birthday once again, my Badbudaaarr Suuuaaaaar!**

I love youuuuu endlessly, my Diduuu! ❤️🫀🧿"""

GIFT_SURPRISE = "🧴 Your gift: Baju mein dekho Baju mein ✨"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def next_birthday(dob: dt.date, today: dt.date) -> dt.date:
    def safe(year):
        try:
            return dt.date(year, dob.month, dob.day)
        except ValueError:  # 29 Feb in a non-leap year
            return dt.date(year, 3, 1)

    nb = safe(today.year)
    if nb < today:
        nb = safe(today.year + 1)
    return nb


def js_str(s: str) -> str:
    """Safe JS string literal for embedding inside <script>."""
    return json.dumps(s).replace("</", "<\\/")


def md_bold_segments(text: str):
    """Split on **bold** markers into [text, is_bold] pairs for the typewriter."""
    segments = []
    for part in re.split(r"(\*\*.*?\*\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            segments.append([part[2:-2], True])
        else:
            segments.append([part, False])
    return segments


@st.cache_data(show_spinner=False)
def to_data_uri(raw: bytes):
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail((700, 700))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def nice_caption(filename: str, i: int) -> str:
    stem = Path(filename).stem
    if re.match(r"(?i)^(img|dsc|pxl|whatsapp|screenshot|photo|image)[\W_]?", stem) or stem.isdigit():
        return f"Memory #{i}"
    return stem.replace("_", " ").replace("-", " ")[:22]


def load_wishes():
    try:
        return json.loads(WISHES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_wishes(wishes):
    WISHES_FILE.write_text(json.dumps(wishes, ensure_ascii=False, indent=2), encoding="utf-8")


def fill(template: str, **tokens) -> str:
    for k, v in tokens.items():
        template = template.replace(f"__{k}__", str(v))
    return template


# --------------------------------------------------------------------------- #
# Derived values
# --------------------------------------------------------------------------- #
# Pinned to IST (not the server's local timezone) so the countdown->"it's
# today" switch happens at midnight for Sunita Didi, regardless of where
# this app ends up hosted.
today = dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
T = THEME
THEME_TOKENS = dict(ACCENT=T["accent"], ACCENT2=T["accent2"], TEXT=T["text"], CARD=T["card"])

nb = next_birthday(DOB, today)
is_today = nb == today
turning = nb.year - DOB.year
days_alive = max(0, (today - DOB).days)
safe_name = html.escape(NAME)
safe_from = html.escape(FROM_NAME)
final_message = MESSAGE

# --------------------------------------------------------------------------- #
# Global page styling
# --------------------------------------------------------------------------- #
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Poppins:wght@400;600;800&family=Caveat:wght@600&display=swap');
.stApp{
  background:linear-gradient(-45deg,__BG1__,__BG2__,__BG3__,__BG1__);
  background-size:400% 400%;
  animation:bgmove 18s ease infinite;
}
@keyframes bgmove{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
header[data-testid="stHeader"]{background:transparent}
footer{visibility:hidden}
.block-container{padding-top:1rem;max-width:1200px;padding-bottom:90px}
.st-key-party_left,.st-key-party_right{
  position:fixed;bottom:18px;z-index:999;
  background:rgba(255,255,255,.6);backdrop-filter:blur(10px);
  padding:10px 14px;border-radius:999px;box-shadow:0 10px 30px rgba(0,0,0,.25);
  width:max-content;max-width:46vw;
}
.st-key-party_left{left:18px}
.st-key-party_right{right:18px}
.st-key-party_left .stButton button,.st-key-party_right .stButton button{white-space:nowrap}
[data-testid="stMain"], [data-testid="stMain"] p, [data-testid="stMain"] label p{color:__TEXT__ !important;font-family:'Poppins',sans-serif}
iframe{border:none}
.section-title{
  font-family:'Pacifico',cursive;text-align:center;font-size:clamp(28px,4vw,46px);
  color:__TEXT__;margin:2.4rem 0 .1rem;text-shadow:0 4px 18px rgba(0,0,0,.18);
  animation:fadeUp 1s both;
}
.section-sub{text-align:center;color:__TEXT__;opacity:.8;font-family:'Poppins',sans-serif;margin-bottom:.4rem}
@keyframes fadeUp{from{opacity:0;transform:translateY(30px)}}
.stButton button, [data-testid="stFormSubmitButton"] button{
  background:linear-gradient(90deg,__ACCENT__,__ACCENT2__) !important;color:#fff !important;
  border:none !important;border-radius:999px !important;font-weight:600 !important;
  padding:.55rem 1.4rem !important;transition:transform .2s, box-shadow .2s !important;
  box-shadow:0 6px 18px rgba(0,0,0,.18);
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover{transform:translateY(-3px) scale(1.04)}
.stButton button p, [data-testid="stFormSubmitButton"] button p{color:#fff !important}
.wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:26px;padding:18px 6px}
.note{
  position:relative;padding:22px 18px 14px;min-height:130px;color:#333;
  font-family:'Caveat',cursive;font-size:23px;line-height:1.2;
  box-shadow:0 10px 22px rgba(0,0,0,.2);transform:rotate(var(--r));
  transition:transform .3s;animation:fadeUp .7s backwards;animation-delay:var(--d);
  word-wrap:break-word;
}
.note:hover{transform:rotate(0) scale(1.06);z-index:2}
.note::before{content:'📌';position:absolute;top:-14px;left:50%;transform:translateX(-50%);font-size:22px}
.note .who{font-family:'Poppins',sans-serif;font-size:13px;font-weight:600;margin-top:10px;opacity:.7;text-align:right}
.empty-wall{text-align:center;opacity:.8;padding:20px;font-family:'Poppins',sans-serif;color:__TEXT__}
.party-footer{text-align:center;opacity:.85;padding:40px 0 20px;font-family:'Poppins',sans-serif;color:__TEXT__}
</style>
"""
st.markdown(
    fill(GLOBAL_CSS, BG1=T["bg1"], BG2=T["bg2"], BG3=T["bg3"], **THEME_TOKENS),
    unsafe_allow_html=True,
)


def section(title, sub=""):
    sub_html = f'<div class="section-sub">{sub}</div>' if sub else ""
    st.markdown(f'<div class="section-title">{title}</div>{sub_html}', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Component scaffold (each animated block runs in its own iframe)
# --------------------------------------------------------------------------- #
CONFETTI_JS = r"""
function makeConfetti(canvas){
  const ctx=canvas.getContext('2d'); let W=0,H=0,P=[];
  const fit=()=>{W=canvas.width=innerWidth;H=canvas.height=innerHeight;}; fit(); addEventListener('resize',fit);
  const pick=()=>COLORS[Math.floor(Math.random()*COLORS.length)];
  function add(x,y,vx,vy,g){P.push({x,y,vx,vy,g,r:Math.random()*7+4,c:pick(),a:Math.random()*6.28,va:Math.random()*.3-.15,round:Math.random()<.35,t:0});}
  function burst(x,y,n=120){for(let i=0;i<n;i++){const ang=Math.random()*Math.PI*2,sp=Math.random()*10+3;add(x,y,Math.cos(ang)*sp,Math.sin(ang)*sp-5,.22);}}
  function rain(n=3){for(let i=0;i<n;i++)add(Math.random()*W,-12,Math.random()*2-1,Math.random()*2+1.5,.03);}
  (function loop(){
    ctx.clearRect(0,0,W,H);
    for(const p of P){
      p.vy+=p.g; p.vx*=.985; p.vy*=.985; p.x+=p.vx+Math.sin(p.t/12)*.6; p.y+=p.vy; p.a+=p.va; p.t++;
      ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.a); ctx.fillStyle=p.c;
      if(p.round){ctx.beginPath();ctx.arc(0,0,p.r/2.4,0,6.28);ctx.fill();}
      else{ctx.scale(1,Math.cos(p.t/8));ctx.fillRect(-p.r/2,-p.r/4,p.r,p.r/2);}
      ctx.restore();
    }
    P=P.filter(p=>p.y<H+30&&p.t<900);
    requestAnimationFrame(loop);
  })();
  return {burst,rain};
}
"""

BASE_HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Poppins:wght@400;600;800&family=Caveat:wght@600&display=swap" rel="stylesheet">
<style>
:root{--accent:__ACCENT__;--accent2:__ACCENT2__;--text:__TEXT__;--card:__CARD__}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:transparent;font-family:'Poppins',sans-serif;color:var(--text);overflow:hidden}
#fx{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:50}
@keyframes blink{50%{opacity:0}}
__CSS__
</style></head><body>
__BODY__
<canvas id="fx"></canvas>
<script>
const COLORS=__COLORS__;
__CONFETTI__
const FX=makeConfetti(document.getElementById('fx'));
__JS__
</script></body></html>"""


def page(body, css="", js="", height=400, scrolling=False, **tokens):
    doc = (
        BASE_HTML.replace("__CSS__", css)
        .replace("__BODY__", body)
        .replace("__JS__", js)
        .replace("__CONFETTI__", CONFETTI_JS)
        .replace("__COLORS__", json.dumps(T["confetti"]))
    )
    doc = fill(doc, **THEME_TOKENS, **tokens)
    if hasattr(st, "iframe"):  # Streamlit 1.5x+ (components.html is deprecated there)
        st.iframe(doc, height=height)  # scrolling pages set overflow:auto in their own CSS
    else:
        components.html(doc, height=height, scrolling=scrolling)


# --------------------------------------------------------------------------- #
# GATE — full-screen countdown shown until the big day arrives; nothing else
# on the page renders until this is done.
# --------------------------------------------------------------------------- #
if not is_today and not st.session_state.get("entered_early"):
    GATE_BODY = """
<div class="gate">
  <div class="gate-top">⏳</div>
  <div class="gate-title">Something special is coming for</div>
  <div class="gate-name">__NAME__</div>
  <div class="cd">
    <div class="box"><div class="num" id="d">00</div><div class="lbl">Days</div></div>
    <div class="box"><div class="num" id="h">00</div><div class="lbl">Hours</div></div>
    <div class="box"><div class="num" id="m">00</div><div class="lbl">Minutes</div></div>
    <div class="box"><div class="num" id="s">00</div><div class="lbl">Seconds</div></div>
  </div>
  <div class="gate-sub">until __UNTIL__</div>
  <div class="enter" id="enter">🎉 It's here — tap to enter ✨</div>
</div>
"""
    GATE_CSS = """
.gate{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px}
.gate-top{font-size:56px;animation:sway 3s ease-in-out infinite}
@keyframes sway{50%{transform:rotate(8deg)}}
.gate-title{font-family:'Poppins',sans-serif;font-weight:600;font-size:clamp(15px,2.2vw,20px);opacity:.85;margin-top:6px}
.gate-name{font-family:'Pacifico',cursive;font-size:clamp(34px,6vw,64px);margin:4px 0 22px;
  background:linear-gradient(90deg,var(--accent),var(--accent2),var(--accent));background-size:200% auto;
  -webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 3s linear infinite}
@keyframes shine{to{background-position:200% center}}
.cd{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.box{background:var(--card);backdrop-filter:blur(8px);border-radius:20px;padding:20px 14px;width:124px;text-align:center;
     box-shadow:0 10px 30px rgba(0,0,0,.15);border:1px solid rgba(255,255,255,.35)}
.num{font-size:48px;font-weight:800;color:var(--accent);line-height:1.1}
.lbl{font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.8}
.bump{animation:bump .35s}
@keyframes bump{50%{transform:scale(1.25)}}
.gate-sub{margin-top:18px;font-weight:600;opacity:.8}
.enter{margin-top:26px;opacity:0;transform:translateY(16px) scale(.9);transition:all .6s cubic-bezier(.2,1.5,.4,1);
       background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;font-weight:700;padding:12px 26px;border-radius:999px;
       cursor:pointer;box-shadow:0 10px 24px rgba(0,0,0,.25)}
.enter.show{opacity:1;transform:none}
"""
    GATE_JS = r"""
const target=new Date(__TARGET__); const last={}; let fired=false;
function enterSite(){ try{ window.top.location.reload(); }catch(e){} }
function tick(){
  const diff=Math.max(0,target-new Date());
  const v={d:Math.floor(diff/864e5),h:Math.floor(diff/36e5)%24,m:Math.floor(diff/6e4)%60,s:Math.floor(diff/1e3)%60};
  for(const k in v){const el=document.getElementById(k);const val=String(v[k]).padStart(2,'0');
    if(last[k]!==val){el.textContent=val;el.classList.remove('bump');void el.offsetWidth;el.classList.add('bump');last[k]=val;}}
  if(diff===0 && !fired){
    fired=true; clearInterval(timer);
    FX.burst(innerWidth/2,innerHeight/2,260);
    document.getElementById('enter').classList.add('show');
    setTimeout(enterSite,1400);
  }
}
document.getElementById('enter').onclick=enterSite;
const timer=setInterval(tick,1000); tick();
"""
    page(
        GATE_BODY, GATE_CSS, GATE_JS, height=480,
        NAME=safe_name, TARGET=js_str(nb.isoformat() + "T00:00:00"),
        UNTIL=nb.strftime("%A, %d %B %Y"),
    )
    st.markdown(
        '<p style="text-align:center;opacity:.75;margin:-8px 0 10px">'
        "Can't wait that long? You don't have to \U0001F440</p>",
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        if st.button("Peek inside early", use_container_width=True):
            st.session_state.entered_early = True
            st.balloons()
            time.sleep(1.5)
            st.rerun()
    st.stop()

# --------------------------------------------------------------------------- #
# 1. HERO — waving title, balloons you can pop, confetti rain, age counter
# --------------------------------------------------------------------------- #
HERO_BODY = """
<div class="hero">
  <div id="balloons"></div>
  <h1 class="title" id="title"></h1>
  <h2 class="name">__NAME__</h2>
  <p class="turning">__TURN_LABEL__ <span id="age">0</span> 🎉</p>
</div>
"""
HERO_CSS = """
.hero{position:relative;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow:hidden;padding:0 12px}
.title{font-family:'Pacifico',cursive;font-size:clamp(40px,8vw,96px);font-weight:400;z-index:2;text-shadow:0 6px 24px rgba(0,0,0,.2);line-height:1.3}
.word{display:inline-block;white-space:nowrap;margin:0 .15em}
.title span span{display:inline-block;animation:wave 2.2s ease-in-out infinite}
@keyframes wave{0%,100%{transform:translateY(0) rotate(0)}25%{transform:translateY(-18px) rotate(-5deg)}50%{transform:translateY(0)}}
.name{font-size:clamp(32px,6vw,72px);font-weight:800;z-index:2;
  background:linear-gradient(90deg,var(--accent),var(--accent2),var(--accent));background-size:200% auto;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  animation:shine 3s linear infinite,pop 1s cubic-bezier(.2,1.6,.4,1) both}
@keyframes shine{to{background-position:200% center}}
@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
.turning{font-size:clamp(18px,3vw,28px);margin-top:6px;z-index:2;font-weight:600}
#age{display:inline-block;min-width:1.4em;font-weight:800;color:var(--accent)}
.balloon{position:absolute;bottom:-160px;width:64px;height:80px;
  border-radius:50% 50% 47% 47% / 55% 55% 45% 45%;
  background:radial-gradient(circle at 32% 28%,rgba(255,255,255,.75) 0 8%,var(--c) 30%);
  box-shadow:inset -8px -10px 0 rgba(0,0,0,.12);cursor:pointer;animation:rise linear forwards;z-index:3}
.balloon::before{content:'';position:absolute;bottom:-7px;left:50%;transform:translateX(-50%);
  border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:9px solid var(--c)}
.balloon::after{content:'';position:absolute;top:100%;left:50%;width:1.5px;height:80px;background:rgba(255,255,255,.7);margin-top:2px}
@keyframes rise{
  0%{transform:translate(0,0) rotate(-4deg) scale(var(--s))}
  25%{transform:translate(18px,-200px) rotate(4deg) scale(var(--s))}
  50%{transform:translate(-12px,-400px) rotate(-3deg) scale(var(--s))}
  75%{transform:translate(14px,-600px) rotate(3deg) scale(var(--s))}
  100%{transform:translate(0,-860px) rotate(0) scale(var(--s))}}
"""
HERO_JS = r"""
const t=document.getElementById('title'); let k=0;
"Happy Birthday".split(' ').forEach(w=>{
  const word=document.createElement('span'); word.className='word';
  [...w].forEach(ch=>{const s=document.createElement('span');s.textContent=ch;
    s.style.animationDelay=(k*0.08)+'s'; s.style.color=k%2?'var(--accent2)':'var(--accent)'; k++; word.appendChild(s);});
  t.appendChild(word);
});
const AGE=__AGE__; let n=0; const el=document.getElementById('age');
const step=()=>{n++; el.textContent=n; if(n<AGE) setTimeout(step, Math.max(25,1500/AGE));};
if(AGE>0) setTimeout(step,700);
const bw=document.getElementById('balloons');
function spawn(){
  const b=document.createElement('div'); b.className='balloon';
  b.style.setProperty('--c',COLORS[Math.floor(Math.random()*COLORS.length)]);
  b.style.setProperty('--s',(0.7+Math.random()*0.6).toFixed(2));
  b.style.left=(Math.random()*92)+'%';
  const d=7+Math.random()*6; b.style.animationDuration=d+'s';
  b.onclick=e=>{FX.burst(e.clientX,e.clientY,60); b.remove();};
  bw.appendChild(b); setTimeout(()=>b.remove(),d*1000);
}
for(let i=0;i<8;i++) setTimeout(spawn,i*350);
setInterval(spawn,900);
setTimeout(()=>{FX.burst(innerWidth*.2,innerHeight*.6,130);FX.burst(innerWidth*.8,innerHeight*.6,130);},400);
let rt=0; const r=setInterval(()=>{FX.rain(3); if(++rt>90) clearInterval(r);},60);
"""
page(
    HERO_BODY, HERO_CSS, HERO_JS, height=560,
    NAME=safe_name, AGE=turning, TURN_LABEL="Officially",
)

# --------------------------------------------------------------------------- #
# 3. CAKE — click candles to blow them out
# --------------------------------------------------------------------------- #
section("🎂 Make a Wish", "Click each candle to blow it out or hit “Blow!”")
CAKE_BODY = """
<div class="wrap">
  <div class="cake">
    <div class="candles" id="candles"></div>
    <div class="tier t1"></div><div class="tier t2"></div><div class="tier t3"></div>
    <div class="plate"></div>
  </div>
  <div class="btns"><button id="blow">🌬️ Blow!</button><button id="relight">🔥 Relight</button></div>
  <div class="wish" id="wish">✨ Wish made! May it come true, Diiiduuuuuu ✨</div>
</div>
"""
CAKE_CSS = """
.wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:18px}
.cake{position:relative;display:flex;flex-direction:column;align-items:center;margin-top:40px;animation:bob 3s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-6px)}}
.candles{display:flex;gap:8px;align-items:flex-end;height:50px;margin-bottom:-2px;z-index:3}
.candle{width:11px;height:46px;border-radius:3px;position:relative;cursor:pointer;
  background:repeating-linear-gradient(-45deg,#fff 0 5px,var(--accent) 5px 10px);box-shadow:inset -2px 0 0 rgba(0,0,0,.1)}
.candle::before{content:'';position:absolute;top:-6px;left:50%;width:2px;height:7px;background:#333;transform:translateX(-50%)}
.flame{position:absolute;left:50%;bottom:calc(100% + 3px);width:14px;height:26px;margin-left:-7px;
  border-radius:50% 50% 50% 50% / 60% 60% 40% 40%;
  background:radial-gradient(ellipse at 50% 75%,#fff 0 18%,#ffe066 32%,#ff9f1c 60%,rgba(255,80,0,0) 72%);
  transform-origin:50% 100%;animation:flick .12s ease-in-out infinite alternate;
  filter:drop-shadow(0 0 10px #ffb703) drop-shadow(0 0 22px #ff7b00);transition:opacity .3s,transform .3s}
@keyframes flick{from{transform:scale(1,1) rotate(-2deg)}to{transform:scale(.92,1.08) rotate(2deg)}}
.candle.out .flame{opacity:0;transform:scale(.1);animation:none}
.smoke{position:absolute;left:50%;bottom:100%;width:8px;height:8px;margin-left:-4px;border-radius:50%;
  background:rgba(210,210,210,.75);animation:smoke 1.4s ease-out forwards;pointer-events:none}
@keyframes smoke{to{transform:translate(12px,-70px) scale(4);opacity:0}}
.tier{position:relative;border-radius:16px 16px 10px 10px;box-shadow:inset 0 -10px 0 rgba(0,0,0,.08)}
.tier::before{content:'';position:absolute;left:0;right:0;top:0;height:16px;background:#fff;border-radius:16px 16px 0 0}
.tier::after{content:'';position:absolute;left:0;right:0;top:15px;height:14px;
  background:radial-gradient(circle at 10px 0,#fff 9px,transparent 10px) 0 0/20px 14px repeat-x}
.t1{width:190px;height:70px;background:linear-gradient(#ffc2d1,#ff8fab)}
.t2{width:250px;height:80px;background:linear-gradient(#fff1b8,#ffd166)}
.t3{width:310px;height:90px;background:linear-gradient(#bde0fe,#7cc6fe)}
.plate{width:370px;max-width:95vw;height:22px;border-radius:50%;background:linear-gradient(#fff,#d9d9d9);margin-top:-6px;box-shadow:0 14px 25px rgba(0,0,0,.25)}
.sprinkle{position:absolute;width:4px;height:10px;border-radius:2px}
.btns button{font-family:inherit;font-weight:600;font-size:15px;border:none;border-radius:999px;padding:10px 22px;margin:0 6px;cursor:pointer;
  background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;box-shadow:0 6px 18px rgba(0,0,0,.2);transition:transform .2s}
.btns button:hover{transform:translateY(-3px) scale(1.05)}
.wish{font-family:'Pacifico',cursive;font-size:clamp(20px,3vw,28px);opacity:0;transform:translateY(20px);transition:all .8s;text-align:center;color:var(--accent);padding:0 12px}
.wish.show{opacity:1;transform:none}
"""
CAKE_JS = r"""
const N=__N__; const box=document.getElementById('candles'); let lit=N;
function mk(){
  box.innerHTML=''; lit=N;
  for(let i=0;i<N;i++){const c=document.createElement('div');c.className='candle';c.innerHTML='<div class="flame"></div>';c.onclick=()=>out(c);box.appendChild(c);}
  document.getElementById('wish').classList.remove('show');
}
function out(c){
  if(c.classList.contains('out')) return;
  c.classList.add('out');
  const s=document.createElement('div'); s.className='smoke'; c.appendChild(s); setTimeout(()=>s.remove(),1500);
  if(--lit===0) celebrate();
}
function celebrate(){
  const r=box.getBoundingClientRect();
  FX.burst(r.left+r.width/2,r.top,220);
  setTimeout(()=>FX.burst(innerWidth*.15,innerHeight*.5,120),300);
  setTimeout(()=>FX.burst(innerWidth*.85,innerHeight*.5,120),600);
  document.getElementById('wish').classList.add('show');
}
document.getElementById('blow').onclick=()=>[...box.children].forEach((c,i)=>setTimeout(()=>out(c),i*120));
document.getElementById('relight').onclick=mk;
mk();
document.querySelectorAll('.tier').forEach(t=>{for(let i=0;i<14;i++){
  const s=document.createElement('span'); s.className='sprinkle';
  s.style.left=(5+Math.random()*90)+'%'; s.style.top=(40+Math.random()*42)+'%';
  s.style.background=COLORS[i%COLORS.length]; s.style.transform='rotate('+(Math.random()*180)+'deg)'; t.appendChild(s);}});
"""
page(CAKE_BODY, CAKE_CSS, CAKE_JS, height=540, N=max(1, min(turning, 9)))

# --------------------------------------------------------------------------- #
# 4. GREETING CARD — opens in 3D, message types itself out
# --------------------------------------------------------------------------- #
section("💌 A Little Note", "Tap the card to open it")
CARD_BODY = """
<div class="stage">
  <div class="card" id="card">
    <div class="inside">
      <div class="msg" id="msg"></div>
      <div class="sign" id="sign">— __FROM__ 💖</div>
    </div>
    <div class="cover">
      <div class="cover-inner"><div class="emoji">💌</div><div class="ct">For __NAME__</div><div class="tap">tap to open</div></div>
    </div>
  </div>
</div>
"""
CARD_CSS = """
.stage{height:100%;display:flex;align-items:center;justify-content:center;padding:10px}
.card{position:relative;width:min(600px,92vw);height:460px;cursor:pointer;perspective:1600px;animation:float 4s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-10px)}}
.inside{position:absolute;inset:0;color:#3b2f2f;border-radius:18px;padding:34px 38px;box-shadow:0 20px 50px rgba(0,0,0,.3);overflow:auto;
  background:#fffdf7 repeating-linear-gradient(#fffdf7 0 31px,#f1e4d3 31px 32px)}
.msg{font-family:'Caveat',cursive;font-size:26px;line-height:32px;white-space:pre-wrap}
.msg b{color:#c2185b;font-weight:700}
.msg::after{content:'|';animation:blink .8s infinite}
.msg.done::after{content:''}
.sign{font-family:'Pacifico',cursive;text-align:right;margin-top:14px;opacity:0;transition:opacity 1s;color:#c2185b;font-size:20px}
.sign.show{opacity:1}
.cover{position:absolute;inset:0;border-radius:18px;background:linear-gradient(135deg,var(--accent),var(--accent2));
  transform-origin:left center;transition:transform 1.4s cubic-bezier(.7,0,.2,1);backface-visibility:hidden;
  display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 20px 50px rgba(0,0,0,.3);overflow:hidden}
.cover::before{content:'';position:absolute;inset:0;background:radial-gradient(rgba(255,255,255,.25) 2px,transparent 3px) 0 0/24px 24px}
.card.open .cover{transform:rotateY(-170deg)}
.cover-inner{text-align:center;position:relative}
.emoji{font-size:72px;animation:wiggle 1.5s infinite}
@keyframes wiggle{0%,100%{transform:rotate(0)}25%{transform:rotate(-12deg)}75%{transform:rotate(12deg)}}
.ct{font-family:'Pacifico',cursive;font-size:clamp(28px,5vw,40px)}
.tap{opacity:.85;letter-spacing:3px;text-transform:uppercase;font-size:12px;margin-top:6px;animation:blink 1.6s infinite}
"""
CARD_JS = r"""
const SEGMENTS=__SEGMENTS__; let opened=false; const card=document.getElementById('card');
const CHARS=[]; SEGMENTS.forEach(([text,bold])=>{for(const ch of text) CHARS.push([ch,bold]);});
const esc=ch=>ch.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
card.onclick=()=>{ if(opened) return; opened=true; card.classList.add('open');
  FX.burst(innerWidth/2,innerHeight/2,140); setTimeout(type,1200); };
function type(){
  const el=document.getElementById('msg'); const box=el.parentElement; let i=0; let bold=false; let html='';
  (function step(){
    if(i<CHARS.length){
      const [ch,chBold]=CHARS[i++];
      if(chBold && !bold){ html+='<b>'; bold=true; } else if(!chBold && bold){ html+='</b>'; bold=false; }
      html += ch==='\n' ? '<br>' : esc(ch);
      const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 40;
      el.innerHTML=html;
      if(nearBottom) box.scrollTop=box.scrollHeight;
      setTimeout(step, ch==='\n'?220:(/[.,!?]/.test(ch)?170:32));
    } else { el.classList.add('done'); document.getElementById('sign').classList.add('show'); }
  })();
}
"""
page(
    CARD_BODY, CARD_CSS, CARD_JS, height=560,
    NAME=safe_name, FROM=safe_from,
    SEGMENTS=json.dumps(md_bold_segments(final_message)).replace("</", "<\\/"),
)

# --------------------------------------------------------------------------- #
# 5. FUN STATS — animated counters
# --------------------------------------------------------------------------- #
section("📊 By the Numbers", f"{safe_name}'s life so far")
stats = [
    ("🌞", days_alive, "Days of awesome"),
    ("⏰", days_alive * 24, "Hours lived"),
    ("💓", days_alive * 24 * 60 * 80, "Heartbeats (approx.)"),
    ("🌕", round(days_alive / 29.53), "Full moons seen"),
]
tiles = "".join(
    f'<div class="tile" style="--d:{i*0.12}s"><div class="ico">{ico}</div>'
    f'<div class="num" data-v="{val}">0</div><div class="lbl">{lbl}</div></div>'
    for i, (ico, val, lbl) in enumerate(stats)
)
page(
    f'<div class="stats">{tiles}</div>',
    """.stats{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;align-items:center;height:100%;padding:10px}
       .tile{background:var(--card);backdrop-filter:blur(8px);border-radius:20px;padding:20px 16px;width:230px;text-align:center;
             box-shadow:0 10px 30px rgba(0,0,0,.15);border:1px solid rgba(255,255,255,.35);transition:transform .3s;animation:up .8s backwards;animation-delay:var(--d)}
       .tile:hover{transform:translateY(-8px) rotate(-1deg)}
       @keyframes up{from{opacity:0;transform:translateY(40px)}}
       .ico{font-size:34px}
       .num{font-size:30px;font-weight:800;color:var(--accent);margin:4px 0}
       .lbl{font-size:13px;opacity:.85;letter-spacing:1px}""",
    r"""
let ran=false;
function run(){ document.querySelectorAll('.num').forEach(el=>{
  const end=+el.dataset.v, t0=performance.now(), dur=2200;
  (function f(t){const p=Math.min(1,(t-t0)/dur), e=1-Math.pow(1-p,4);
    el.textContent=Math.round(end*e).toLocaleString(); if(p<1) requestAnimationFrame(f);})(t0);
});}
if('IntersectionObserver' in window){
  new IntersectionObserver(es=>{ if(es[0].isIntersecting && !ran){ ran=true; run(); } },{threshold:.3}).observe(document.body);
} else run();
""",
    height=230,
)

# --------------------------------------------------------------------------- #
# 6. MEMORY WALL — polaroids with drop-in animation + lightbox
# --------------------------------------------------------------------------- #
section("📸 Memory Lane", "Hover to straighten, click to zoom")
MEMORY_CAPTIONS = [
    "My Sister",
    "My Best Friend",
    "My Home",
    "My Personal Therapist",
    "My Safe Place",
    "My Biggest Blessing",
    "My Chugli Partner",
    "My Protector",
]
pics = []
if PHOTOS_DIR.exists():
    for p in sorted(PHOTOS_DIR.iterdir()):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            pics.append((p.name, p.read_bytes()))
pics = pics[:12]

rng = random.Random(42)
items = []
for i, (fname, raw) in enumerate(pics, start=1):
    uri = to_data_uri(raw)
    if not uri:
        continue
    caption = MEMORY_CAPTIONS[i - 1] if i - 1 < len(MEMORY_CAPTIONS) else nice_caption(fname, i)
    items.append(
        f'<figure class="pol" style="--r:{rng.uniform(-6, 6):.1f}deg;--d:{(i-1)*0.12:.2f}s">'
        f'<img src="{uri}" alt=""><figcaption>{html.escape(caption)}</figcaption></figure>'
    )
if not items:
    placeholders = [("🎈", "Add photos"), ("🥳", "to the photos/"), ("🍰", "folder next"), ("🎁", "to app.py"), ("🌟", "Best memories"), ("💛", "go here")]
    for i, (emo, cap) in enumerate(placeholders):
        items.append(
            f'<figure class="pol" style="--r:{rng.uniform(-6, 6):.1f}deg;--d:{i*0.12:.2f}s">'
            f'<div class="ph">{emo}</div><figcaption>{cap}</figcaption></figure>'
        )
rows = math.ceil(len(items) / 3)
page(
    f'<div class="gallery">{"".join(items)}</div><div id="lb"><img alt=""></div>',
    """html,body{overflow:auto}
       .gallery{display:flex;flex-wrap:wrap;gap:30px;justify-content:center;padding:30px 10px}
       .pol{position:relative;background:#fff;padding:12px 12px 44px;width:220px;box-shadow:0 12px 30px rgba(0,0,0,.25);
            transform:rotate(var(--r));transition:transform .4s,box-shadow .4s;animation:drop .9s cubic-bezier(.2,1.4,.4,1) backwards;animation-delay:var(--d)}
       .pol::before{content:'';position:absolute;top:-12px;left:50%;width:80px;height:24px;margin-left:-40px;background:rgba(255,255,255,.6);
            box-shadow:0 1px 3px rgba(0,0,0,.15);transform:rotate(-3deg)}
       .pol:hover{transform:rotate(0) scale(1.08);z-index:5;box-shadow:0 22px 44px rgba(0,0,0,.35)}
       .pol img,.ph{width:196px;height:196px;object-fit:cover;display:block}
       .pol img{cursor:zoom-in}
       .ph{display:flex;align-items:center;justify-content:center;font-size:72px;background:linear-gradient(135deg,var(--accent),var(--accent2))}
       figcaption{position:absolute;bottom:8px;left:0;right:0;text-align:center;font-family:'Caveat',cursive;font-size:22px;color:#444}
       @keyframes drop{from{opacity:0;transform:translateY(-90px) rotate(20deg)}}
       #lb{position:fixed;inset:0;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:.3s;z-index:60;cursor:zoom-out}
       #lb.show{opacity:1;pointer-events:auto}
       #lb img{max-width:90%;max-height:90%;border:8px solid #fff;transform:scale(.8);transition:.3s}
       #lb.show img{transform:scale(1)}""",
    r"""
const lb=document.getElementById('lb');
document.querySelectorAll('.pol img').forEach(img=>img.onclick=e=>{lb.querySelector('img').src=img.src;lb.classList.add('show');FX.burst(e.clientX,e.clientY,40);});
lb.onclick=()=>lb.classList.remove('show');
""",
    height=min(80 + rows * 310, 1000),
    scrolling=True,
)

# --------------------------------------------------------------------------- #
# 7. GIFT BOX — shakes, lid flies off, surprise revealed
# --------------------------------------------------------------------------- #
section("🎁 One More Thing…")
GIFT_BODY = """
<div class="g-wrap">
  <div class="gift" id="gift">
    <div class="rays"></div>
    <div class="bottle">🧴</div>
    <div class="lid"><span class="bow">🎀</span></div>
    <div class="box"></div>
  </div>
  <div class="tap" id="tap">Tap the gift 🎁</div>
  <div class="reveal" id="reveal">__SURPRISE__</div>
</div>
"""
GIFT_CSS = """
.g-wrap{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 12px}
.gift{position:relative;width:170px;height:150px;cursor:pointer;animation:hop 2s ease-in-out infinite;margin-top:40px}
@keyframes hop{0%,60%,100%{transform:translateY(0)}70%{transform:translateY(-14px) rotate(-3deg)}80%{transform:translateY(0) rotate(3deg)}}
.box{position:absolute;bottom:0;left:10px;width:150px;height:110px;border-radius:6px;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 15px 30px rgba(0,0,0,.3)}
.box::before,.lid::before{content:'';position:absolute;left:50%;top:0;bottom:0;width:26px;margin-left:-13px;background:rgba(255,255,255,.55)}
.lid{position:absolute;top:10px;left:0;width:170px;height:38px;border-radius:6px;background:linear-gradient(135deg,var(--accent2),var(--accent));
  z-index:2;transition:transform 1s cubic-bezier(.3,1.6,.5,1),opacity 1s;box-shadow:0 6px 12px rgba(0,0,0,.2)}
.bow{position:absolute;top:-36px;left:50%;transform:translateX(-50%);font-size:46px}
.rays{position:absolute;left:50%;top:50%;width:420px;height:420px;margin:-210px 0 0 -210px;border-radius:50%;
  background:repeating-conic-gradient(rgba(255,255,255,.4) 0 10deg,transparent 10deg 20deg);
  -webkit-mask:radial-gradient(circle,#000 25%,transparent 70%);mask:radial-gradient(circle,#000 25%,transparent 70%);
  opacity:0;transition:opacity 1s;animation:spin 14s linear infinite;pointer-events:none}
@keyframes spin{to{transform:rotate(360deg)}}
.gift.shake{animation:shake .6s}
@keyframes shake{20%{transform:rotate(-8deg)}40%{transform:rotate(8deg)}60%{transform:rotate(-6deg)}80%{transform:rotate(6deg)}}
.gift.open{animation:none;cursor:default}
.gift.open .lid{transform:translate(70px,-170px) rotate(35deg);opacity:0}
.gift.open .rays{opacity:1}
.bottle{position:absolute;left:50%;bottom:40px;font-size:54px;opacity:0;z-index:1;
  transform:translate(-50%,0) scale(.4) rotate(-15deg);filter:drop-shadow(0 10px 14px rgba(0,0,0,.3));pointer-events:none}
.gift.open .bottle{animation:bottleRise 1.1s cubic-bezier(.2,1.6,.4,1) .55s forwards}
@keyframes bottleRise{
  0%{transform:translate(-50%,0) scale(.4) rotate(-15deg);opacity:0}
  45%{transform:translate(-50%,-104px) scale(1.08) rotate(5deg);opacity:1}
  75%{transform:translate(-50%,-92px) scale(1) rotate(-3deg);opacity:1}
  100%{transform:translate(-50%,-98px) scale(1) rotate(0deg);opacity:1}
}
.tap{margin-top:18px;font-weight:600;opacity:.85;transition:opacity .5s}
.reveal{margin-top:10px;background:#fff;color:#333;padding:18px 26px;border-radius:18px;font-size:clamp(17px,2.4vw,22px);font-weight:600;
  max-width:560px;text-align:center;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0;transform:scale(.3) translateY(30px);
  transition:all .9s cubic-bezier(.2,1.5,.4,1) .3s}
.reveal.show{opacity:1;transform:none}
"""
GIFT_JS = r"""
const g=document.getElementById('gift'); let done=false;
g.onclick=()=>{ if(done) return; done=true; g.classList.add('shake');
  setTimeout(()=>{ g.classList.remove('shake'); g.classList.add('open');
    const r=g.getBoundingClientRect(); FX.burst(r.left+r.width/2,r.top+40,240);
    setTimeout(()=>FX.burst(r.left+r.width/2,r.top+40,120),400);
    document.getElementById('reveal').classList.add('show'); document.getElementById('tap').style.opacity=0; },650);
};
"""
page(GIFT_BODY, GIFT_CSS, GIFT_JS, height=470, SURPRISE=html.escape(GIFT_SURPRISE))

# --------------------------------------------------------------------------- #
# 8. PARTY CONTROLS — native Streamlit effects + music
# --------------------------------------------------------------------------- #
section("🕺 Let's Dance and Party! 🎉💃")
with st.container(key="party_left"):
    if st.button("🎈 Balloon storm"):
        st.balloons()
with st.container(key="party_right"):
    if st.button("❄️ Make it snow"):
        st.snow()

song_bytes = SONG_FILE.read_bytes() if SONG_FILE.exists() else None
if song_bytes:
    st.markdown("🎵 **Press play for the party song**")
    st.audio(song_bytes, format="audio/mp3", loop=True)
