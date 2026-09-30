"""import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from crew import research_crew

#naya
import json
from pathlib import Path
from urllib.parse import quote   # ADDED (for X post link)

load_dotenv()

st.set_page_config(
    page_title="Scientific AI Content Generator",
    page_icon="🤖"
)

st.title("🤖 Scientific AI Content Generator")

st.write("Upload scientific resources and generate research-based content.")

# PDF Upload
pdf_files = st.file_uploader(
    "📄 Upload Research Papers / Scientific PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

pdf_text = ""

if pdf_files:
    st.success(f"{len(pdf_files)} PDF uploaded")

    for pdf in pdf_files:
        reader = PdfReader(pdf)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        # Keep each PDF reasonably small for the free API limit
        max_chars = 5000

        if len(text) > max_chars:
            text = text[:max_chars]

        pdf_text += f"\n\n--- {pdf.name} ---\n{text}"

        st.write("📄", pdf.name)
        st.write("Pages:", len(reader.pages))


# Dataset Upload
dataset_files = st.file_uploader(
    "📊 Upload Dataset",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

# Image Upload
image_files = st.file_uploader(
    "🖼️ Upload Scientific Images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

st.divider()

topic = st.text_area(
    "✍️ What do you want the AI to generate?",
    placeholder="Example: Explain the main findings of this research paper."
)

if st.button("🚀 Generate"):

    if not pdf_files:
        st.warning("Please upload at least one research PDF.")

    elif not topic:
        st.warning("Please enter your topic/instruction.")

    else:

        with st.spinner("🤖 Research Agent is analyzing the scientific material..."):

            try:

                result = research_crew.kickoff(
                    inputs={
                        "topic": topic,
                        "pdf_text": pdf_text
                    }
                )
                #st.session_state.content_result = result

                #st.success("Research analysis generated!")

                #st.subheader("🔬 Research Analysis")

                #st.write(result)
                #st.markdown(result.raw)
                #naya bhi
                st.session_state.content_result = result

                st.success("Research analysis generated!")

                st.subheader("🔬 Research Analysis")
                st.markdown(result.raw)

                st.subheader("📝 Generated Content")

                edited_content = st.text_area(
                     "✏️ Edit your content before scheduling:",
                     value=result.raw,
                    height=350
                )

                st.session_state.edited_content = edited_content

            except Exception as e:

                st.error("Something went wrong.")
                st.code(str(e))



#ye naya dala hai                
st.divider()

st.subheader("📅 Schedule Post")

schedule_date = st.date_input("Select Date")
schedule_time = st.time_input("Select Time")

if st.button("📅 Schedule Post"):

    if not st.session_state.get("content_result"):
        st.warning("Please generate content first.")

    else:
        post_data = {
            "date": str(schedule_date),
            "time": str(schedule_time),
            "content": st.session_state.get(
                "edited_content",
                st.session_state.content_result.raw
            ),
            "status": "Scheduled"
        }

        file_path = Path("scheduled_posts.json")

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                posts = json.load(f)
        else:
            posts = []

        posts.append(post_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=4, ensure_ascii=False)

        st.success("✅ Post scheduled successfully!")


# ======================================================================
# ADDED: Human-in-the-loop "Post on X" (free, no API)
# ======================================================================
st.divider()

st.subheader("🐦 Post on X (Human Approval)")

if not st.session_state.get("content_result"):
    st.info("Generate content first to post on X.")

else:
    TWEET_LIMIT = 280

    source_text = st.session_state.get(
        "edited_content",
        st.session_state.content_result.raw
    )

    # When new content is generated, rebuild the tweet draft from it
    if st.session_state.get("tweet_source") != source_text:
        short = " ".join(source_text.split())
        if len(short) > TWEET_LIMIT:
            short = short[: TWEET_LIMIT - 1].rsplit(" ", 1)[0] + "…"
        st.session_state.tweet_source = source_text
        st.session_state.tweet_draft = short

    tweet = st.text_area(
        "✏️ Tweet (max 280 chars, edit if needed)",
        key="tweet_draft",
        height=140
    )

    remaining = TWEET_LIMIT - len(tweet)

    if remaining < 0:
        st.error(f"❌ {-remaining} characters too long")
    else:
        st.caption(f"{remaining} characters left")

    if image_files:
        st.write("🖼️ Image X pe automatically attach nahi hoti. Download karke compose box mein daalo:")
        for img in image_files:
            st.image(img, width=250)
            st.download_button(
                f"⬇️ Download {img.name}",
                img.getvalue(),
                file_name=img.name,
                key=f"dl_{img.name}"
            )

    approved = st.checkbox("✅ I have reviewed this content and approve it")

    if approved and tweet.strip() and remaining >= 0:
        st.link_button(
            "🐦 Post on X",
            "https://twitter.com/intent/tweet?text=" + quote(tweet),
            type="primary"
        )
        st.caption("X khulega with tweet pre-filled. Aap login ho toh bas Post dabao.")"""

import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from crew import research_crew

#naya
import json
from pathlib import Path
from urllib.parse import quote   # ADDED (for X post link)
from datetime import datetime    # ADDED (for queue due check)
import html                      # ADDED (safe text in cards)
import re                        # ADDED (tweet builder)
import base64                    # ADDED (hero image)
import random                    # ADDED (snow effect)

load_dotenv()

# ======================================================================
# ADDED: Smart short-tweet builder (Hook + best line + top hashtags)
# ======================================================================
_HEADS = ("hook", "post / caption", "post/caption", "caption", "post",
          "short description", "hashtags", "references")


def _trim(text, n):
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    return text[: n - 1].rsplit(" ", 1)[0] + "…"


def _parse_sections(text):
    sections, cur = {}, None
    for line in text.splitlines():
        clean = re.sub(r"^[\W_]+|[\W_]+$", "", line).strip().lower()
        m = re.match(r"^[\W_]*(" + "|".join(re.escape(h) for h in _HEADS) + r")[\W_]*:\s*(.+)$",
                     line, re.I)
        if m:                                   # "Hook: text" on same line
            cur = m.group(1).lower()
            sections[cur] = [m.group(2)]
        elif clean in _HEADS:                   # heading on its own line
            cur = clean
            sections[cur] = []
        elif cur:
            sections[cur].append(line)
    return {k: " ".join(" ".join(v).split()) for k, v in sections.items()}


def make_tweet(text, limit=280):
    sec = _parse_sections(text)

    hook = sec.get("hook", "")
    body = (sec.get("post / caption") or sec.get("post/caption")
            or sec.get("caption") or sec.get("post")
            or sec.get("short description", ""))
    tags = [t for t in sec.get("hashtags", "").split() if t.startswith("#")][:3]
    tag_str = " ".join(tags)
    reserve = len(tag_str) + 2 if tag_str else 0

    main = hook or body
    if not main:                                # unknown format -> plain trim
        return _trim(text, limit)

    tweet = _trim(main, limit - reserve)

    # add the first sentence of the caption if there is room
    if hook and body:
        first = re.split(r"(?<=[.!?])\s+", body)[0]
        if len(tweet) + 1 + len(first) + reserve <= limit:
            tweet = tweet + " " + first

    return tweet + ("\n\n" + tag_str if tag_str else "")


st.set_page_config(
    page_title="Scientific AI Content Generator",
    page_icon="🤖",
    layout="centered"
)

# ======================================================================
# ADDED: UI / theme (presentation only - no logic change)
# ======================================================================
_img = Path(__file__).parent / "assets" / "arctic.jpg"
if _img.exists():
    _photo = "url(data:image/jpeg;base64," + base64.b64encode(_img.read_bytes()).decode() + ")"
else:
    _photo = "linear-gradient(135deg,#0a4c86,#1ea7d8)"

_CSS = """
:root {
    --photo: __PHOTO__;
    --deep: #0a4c86; --sky: #1ea7d8; --ink: #10304a; --line: #cfe6f5;
}

/* ---------- page ---------- */
.stApp {
    background:
        linear-gradient(180deg, rgba(228,242,251,.93) 0%, rgba(245,250,254,.96) 45%, #ffffff 100%),
        var(--photo) center top / cover fixed;
}
header[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

.block-container {
    max-width: 920px;
    margin-top: 1rem;
    padding: 2rem 2.2rem 3rem 2.2rem !important;
    background: rgba(255,255,255,.74);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,.95);
    border-radius: 28px;
    box-shadow: 0 24px 70px rgba(10,76,134,.16);
    animation: fadein .6s ease;
}
@media (max-width: 640px) {
    .block-container { padding: 1.2rem 1rem 2rem 1rem !important; border-radius: 18px; }
}
@keyframes fadein { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

/* ---------- snow ---------- */
.snow { position: fixed; inset: 0; pointer-events: none; z-index: 5; overflow: hidden; }
.flake { position: absolute; top: -30px; color: #a9d9f2; opacity: .55; animation: fall linear infinite; }
@keyframes fall { to { transform: translateY(112vh) rotate(360deg); } }

/* ---------- hero ---------- */
.hero {
    position: relative; height: 290px; border-radius: 24px; overflow: hidden;
    background: var(--photo) center 60% / cover;
    box-shadow: 0 18px 44px rgba(10,76,134,.38);
    margin-bottom: 18px;
}
.hero::before {
    content: ""; position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(120deg, rgba(10,76,134,.55), rgba(30,167,216,.12) 60%, rgba(255,255,255,0));
}
.hero::after {
    content: ""; position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(180deg, rgba(8,45,80,0) 30%, rgba(8,45,80,.88) 100%);
}
.hero-text { position: absolute; left: 28px; right: 28px; bottom: 22px; z-index: 2; color: #fff; }
.hero-text .tag  { font-size: 12px; letter-spacing: 3px; text-transform: uppercase; opacity: .92; }
.hero-text .head { font-size: 32px; font-weight: 800; line-height: 1.15; margin: 6px 0 4px; text-shadow: 0 2px 14px rgba(0,0,0,.4); }
.hero-text .sub  { font-size: 15px; opacity: .95; margin-bottom: 12px; }
.chips span {
    display: inline-block; margin: 0 8px 6px 0; padding: 5px 14px; border-radius: 999px;
    background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.5);
    backdrop-filter: blur(6px); font-size: 12.5px; font-weight: 600;
}
@media (max-width: 640px) { .hero { height: 250px; } .hero-text .head { font-size: 24px; } }

/* ---------- stepper ---------- */
.stepper { display: flex; gap: 8px; flex-wrap: wrap; margin: 4px 0 6px; }
.stepper .s {
    flex: 1; min-width: 120px; text-align: center; padding: 10px 8px; border-radius: 14px;
    background: linear-gradient(180deg, #fff, #eaf5fc); border: 1px solid var(--line);
    font-size: 13px; font-weight: 700; color: var(--deep);
    box-shadow: 0 4px 12px rgba(10,76,134,.08);
}
.stepper .s b {
    display: inline-flex; width: 22px; height: 22px; border-radius: 50%;
    background: linear-gradient(135deg, var(--deep), var(--sky)); color: #fff;
    align-items: center; justify-content: center; font-size: 12px; margin-right: 6px;
}

/* ---------- stat tiles ---------- */
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 12px 0 4px; }
.tile {
    padding: 14px 16px; border-radius: 16px;
    background: linear-gradient(135deg, #fff, #eaf5fc); border: 1px solid var(--line);
    box-shadow: 0 6px 18px rgba(10,76,134,.10);
}
.tile .n { font-size: 28px; font-weight: 800; color: var(--deep); line-height: 1; }
.tile .l { font-size: 11.5px; letter-spacing: 1.2px; text-transform: uppercase; color: #5b7d94; margin-top: 7px; }

/* ---------- section headers ---------- */
.sec { display: flex; align-items: center; gap: 14px; margin: 34px 0 12px; }
.sec .num {
    flex: none; width: 42px; height: 42px; border-radius: 13px;
    background: linear-gradient(135deg, var(--deep), var(--sky)); color: #fff;
    font-weight: 800; font-size: 19px; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 18px rgba(30,167,216,.42);
}
.sec .t { font-size: 22px; font-weight: 800; color: var(--deep); line-height: 1.1; }
.sec .d { font-size: 13.5px; color: #4a6b82; margin-top: 3px; }

h2, h3 { font-weight: 700 !important; color: var(--deep); }
hr { border-color: #bfdff2 !important; }

/* ---------- inputs ---------- */
textarea, input { border-radius: 12px !important; }
div[data-baseweb="textarea"], div[data-baseweb="input"] {
    border-radius: 12px !important; background: #fff !important;
    box-shadow: 0 2px 10px rgba(10,76,134,.07);
}
div[data-baseweb="textarea"]:focus-within, div[data-baseweb="input"]:focus-within {
    box-shadow: 0 0 0 3px rgba(30,167,216,.35) !important;
}
div[data-testid="stFileUploader"] section {
    border-radius: 16px !important; border: 2px dashed #7cc4e8 !important;
    background: rgba(255,255,255,.8) !important; transition: all .2s ease;
}
div[data-testid="stFileUploader"] section:hover { border-color: var(--sky) !important; background: #f2faff !important; }

/* ---------- buttons ---------- */
div[data-testid="stButton"] > button,
div[data-testid="stLinkButton"] a,
div[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important; font-weight: 600 !important;
    border: 1px solid #b9dcf1 !important;
    transition: transform .15s ease, box-shadow .15s ease;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stLinkButton"] a:hover,
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-2px); box-shadow: 0 8px 18px rgba(11,127,199,.30);
}
button[kind="primary"], button[data-testid="stBaseButton-primary"],
a[kind="primary"], a[data-testid="stBaseLinkButton-primary"] {
    background: linear-gradient(135deg, #0a4c86, #1ea7d8) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 8px 20px rgba(30,167,216,.40);
}

/* ---------- progress / alerts ---------- */
div[data-testid="stProgress"] > div > div > div > div { background: linear-gradient(90deg, #0a4c86, #1ea7d8); }
div[data-testid="stAlert"] { border-radius: 14px; }

/* ---------- tweet / queue ---------- */
.tweet-box {
    border-left: 4px solid #1d9bf0; background: rgba(29,155,240,.10);
    padding: 12px 16px; border-radius: 10px; white-space: pre-wrap; margin: 6px 0 12px 0;
}
.badge { padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.badge-due { background: #ff4b4b; color: #fff; animation: pulse 1.2s infinite; }
.badge-up  { background: #dbeefb; color: #0a4c86; }
.due-banner {
    padding: 14px 18px; border-radius: 14px; margin-bottom: 12px;
    background: linear-gradient(90deg, #ff4b4b, #ff8f3f);
    color: #fff; font-weight: 700; font-size: 17px; animation: pulse 1.2s infinite;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(255,75,75,.55); }
    70%  { box-shadow: 0 0 0 12px rgba(255,75,75,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,75,75,0); }
}

/* ---------- footer ---------- */
.foot { text-align: center; color: #5b7d94; font-size: 13px; margin-top: 40px; }
"""

st.markdown("<style>" + _CSS.replace("__PHOTO__", _photo) + "</style>", unsafe_allow_html=True)

# falling snow (fixed positions -> no flicker on rerun)
_rng = random.Random(7)
_flakes = "".join(
    f'<span class="flake" style="left:{_rng.randint(0, 98)}%;'
    f'animation-duration:{_rng.randint(10, 22)}s;animation-delay:-{_rng.randint(0, 18)}s;'
    f'font-size:{_rng.randint(10, 22)}px">❄</span>'
    for _ in range(22)
)
st.markdown(f'<div class="snow">{_flakes}</div>', unsafe_allow_html=True)


def section(num, title, sub=""):
    st.markdown(
        f'<div class="sec"><div class="num">{num}</div>'
        f'<div><div class="t">{title}</div><div class="d">{sub}</div></div></div>',
        unsafe_allow_html=True
    )


def _queue_stats():
    fp = Path("scheduled_posts.json")
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    sched = [p for p in data if p.get("status") == "Scheduled"]
    done = [p for p in data if p.get("status") == "Posted"]
    due = 0
    for p in sched:
        try:
            if datetime.fromisoformat(f"{p['date']}T{p['time']}") <= datetime.now():
                due += 1
        except ValueError:
            pass
    return len(sched), due, len(done)


# ---------- hero ----------
st.markdown(
    '<div class="hero"><div class="hero-text">'
    '<div class="tag">❄️ NCPOR · Polar Science Outreach</div>'
    '<div class="head">🤖 Scientific AI Content Generator</div>'
    '<div class="sub">Upload scientific resources and generate research-based content.</div>'
    '<div class="chips"><span>📄 PDF → Insights</span><span>✍️ Content Studio</span>'
    '<span>🧑‍💻 Human-in-the-loop</span><span>🆓 Free posting</span></div>'
    '</div></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="stepper">'
    '<div class="s"><b>1</b>Upload</div><div class="s"><b>2</b>Generate</div>'
    '<div class="s"><b>3</b>Schedule</div><div class="s"><b>4</b>Post on X</div>'
    '<div class="s"><b>5</b>Queue</div></div>',
    unsafe_allow_html=True
)

_s, _d, _p = _queue_stats()
st.markdown(
    '<div class="tiles">'
    f'<div class="tile"><div class="n">{_s}</div><div class="l">Scheduled</div></div>'
    f'<div class="tile"><div class="n">{_d}</div><div class="l">Due now</div></div>'
    f'<div class="tile"><div class="n">{_p}</div><div class="l">Posted</div></div>'
    '</div>',
    unsafe_allow_html=True
)

# ======================================================================
# 1. UPLOAD
# ======================================================================
section(1, "Upload Sources", "Research papers, datasets and images")

# PDF Upload
pdf_files = st.file_uploader(
    "📄 Upload Research Papers / Scientific PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

pdf_text = ""

if pdf_files:
    st.success(f"{len(pdf_files)} PDF uploaded")

    for pdf in pdf_files:
        reader = PdfReader(pdf)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        # Keep each PDF reasonably small for the free API limit
        max_chars = 5000

        if len(text) > max_chars:
            text = text[:max_chars]

        pdf_text += f"\n\n--- {pdf.name} ---\n{text}"

        st.write("📄", pdf.name)
        st.write("Pages:", len(reader.pages))


# Dataset Upload
dataset_files = st.file_uploader(
    "📊 Upload Dataset",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

# Image Upload
image_files = st.file_uploader(
    "🖼️ Upload Scientific Images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# ======================================================================
# 2. GENERATE
# ======================================================================
section(2, "Generate Content", "Tell the AI what you need, then let the research agent work")

topic = st.text_area(
    "✍️ What do you want the AI to generate?",
    placeholder="Example: Explain the main findings of this research paper."
)

if st.button("🚀 Generate", type="primary"):

    if not pdf_files:
        st.warning("Please upload at least one research PDF.")

    elif not topic:
        st.warning("Please enter your topic/instruction.")

    else:

        with st.spinner("🤖 Research Agent is analyzing the scientific material..."):

            try:

                result = research_crew.kickoff(
                    inputs={
                        "topic": topic,
                        "pdf_text": pdf_text
                    }
                )
                #st.session_state.content_result = result

                #st.success("Research analysis generated!")

                #st.subheader("🔬 Research Analysis")

                #st.write(result)
                #st.markdown(result.raw)
                #naya bhi
                st.session_state.content_result = result

                st.success("Research analysis generated!")

                st.subheader("🔬 Research Analysis")
                st.markdown(result.raw)

                st.subheader("📝 Generated Content")

                edited_content = st.text_area(
                     "✏️ Edit your content before scheduling:",
                     value=result.raw,
                    height=350
                )

                st.session_state.edited_content = edited_content

            except Exception as e:

                st.error("Something went wrong.")
                st.code(str(e))


# ======================================================================
# 3. SCHEDULE
# ======================================================================
section(3, "Schedule Post", "Pick a date and time - the queue below reminds you when it is due")

_c1, _c2 = st.columns(2)
with _c1:
    schedule_date = st.date_input("Select Date")
with _c2:
    schedule_time = st.time_input("Select Time")

if st.button("📅 Schedule Post", type="primary"):

    if not st.session_state.get("content_result"):
        st.warning("Please generate content first.")

    else:
        post_data = {
            "date": str(schedule_date),
            "time": str(schedule_time),
            "content": st.session_state.get(
                "edited_content",
                st.session_state.content_result.raw
            ),
            "status": "Scheduled"
        }

        file_path = Path("scheduled_posts.json")

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                posts = json.load(f)
        else:
            posts = []

        posts.append(post_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=4, ensure_ascii=False)

        st.success("✅ Post scheduled successfully!")


# ======================================================================
# 4. POST ON X (human approval, free)
# ======================================================================
section(4, "Post on X", "Review the tweet, approve it, then click Post - free, no API")

if not st.session_state.get("content_result"):
    st.info("Generate content first to post on X.")

else:
    TWEET_LIMIT = 280

    source_text = st.session_state.get(
        "edited_content",
        st.session_state.content_result.raw
    )

    # When new content is generated, rebuild the tweet draft from it
    if st.session_state.get("tweet_source") != source_text:
        short = make_tweet(source_text, TWEET_LIMIT)
        st.session_state.tweet_source = source_text
        st.session_state.tweet_draft = short

    tweet = st.text_area(
        "✏️ Tweet (max 280 chars, edit if needed)",
        key="tweet_draft",
        height=140
    )

    remaining = TWEET_LIMIT - len(tweet)

    st.progress(min(max(len(tweet) / TWEET_LIMIT, 0.0), 1.0))

    if remaining < 0:
        st.error(f"❌ {-remaining} characters too long")
    else:
        st.caption(f"{remaining} characters left")

    if image_files:
        st.write("🖼️ Image X pe automatically attach nahi hoti. Download karke compose box mein daalo:")
        for img in image_files:
            st.image(img, width=250)
            st.download_button(
                f"⬇️ Download {img.name}",
                img.getvalue(),
                file_name=img.name,
                key=f"dl_{img.name}"
            )

    approved = st.checkbox("✅ I have reviewed this content and approve it")

    if approved and tweet.strip() and remaining >= 0:
        st.link_button(
            "🐦 Post on X",
            "https://twitter.com/intent/tweet?text=" + quote(tweet),
            type="primary"
        )
        st.caption("X khulega with tweet pre-filled. Aap login ho toh bas Post dabao.")


# ======================================================================
# 5. SCHEDULED QUEUE - auto-checks every 5 sec while the app is open.
# When the scheduled date/time arrives -> alert + one-click Post on X.
# ======================================================================
section(5, "Scheduled Queue", "Live - checks every 5 seconds while this page is open")

# st.fragment(run_every=...) needs Streamlit 1.37+ ; older version = manual refresh
_fragment = getattr(st, "fragment", None)


def _live(fn):
    return _fragment(run_every=5)(fn) if _fragment else fn


@_live
def scheduled_queue():

    queue_file = Path("scheduled_posts.json")

    if queue_file.exists():
        with open(queue_file, "r", encoding="utf-8") as f:
            queue_posts = json.load(f)
    else:
        queue_posts = []

    pending = [(i, p) for i, p in enumerate(queue_posts) if p.get("status") == "Scheduled"]

    if not pending:
        st.info("No scheduled posts.")
        return

    now = datetime.now()

    def is_due(p):
        try:
            return datetime.fromisoformat(f"{p['date']}T{p['time']}") <= now
        except ValueError:
            return False

    due_count = sum(1 for _, p in pending if is_due(p))

    if due_count:
        st.markdown(
            f'<div class="due-banner">🔔 {due_count} post(s) ka time ho gaya! '
            f'Neeche "Post on X" dabao.</div>',
            unsafe_allow_html=True
        )

    notified = st.session_state.setdefault("notified_posts", set())

    for i, p in pending:

        due = is_due(p)
        key = f"{p['date']}|{p['time']}|{p['content'][:40]}"

        if due and key not in notified:
            st.toast("🔔 Scheduled post ka time ho gaya!", icon="🐦")
            notified.add(key)

        with st.container(border=True):

            badge = (
                '<span class="badge badge-due">🔔 DUE NOW</span>'
                if due else
                '<span class="badge badge-up">🕒 Upcoming</span>'
            )
            st.markdown(f"{badge} &nbsp; 📅 {p['date']} &nbsp; ⏰ {p['time']}", unsafe_allow_html=True)

            st.write(p["content"])

            short_tweet = make_tweet(p["content"])
            st.markdown(f"**🐦 Tweet-ready (short) — {len(short_tweet)}/280**")
            st.markdown(f'<div class="tweet-box">{html.escape(short_tweet)}</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.link_button(
                    "🐦 Post on X",
                    "https://twitter.com/intent/tweet?text=" + quote(short_tweet),
                    type="primary" if due else "secondary"
                )

            with col2:
                if st.button("✔️ Mark as Posted", key=f"done_{i}"):
                    queue_posts[i]["status"] = "Posted"
                    with open(queue_file, "w", encoding="utf-8") as f:
                        json.dump(queue_posts, f, indent=4, ensure_ascii=False)
                    st.rerun()


scheduled_queue()

st.markdown(
    '<div class="foot">❄️ Built for polar science outreach · Human-in-the-loop posting · '
    'Free, no API needed</div>',
    unsafe_allow_html=True
)





