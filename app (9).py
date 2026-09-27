import streamlit as st
import base64
import json
import re
import difflib

# ============================================================
# BILLYTICS — Pakistan Bill Decoder & Household Savings Tool
# Team Two Devs — Umamah Nasir & Chaudhary Muhammad Huzaifa Ali
# Made in Pakistan, for Pakistan 🇵🇰
# ============================================================

st.set_page_config(page_title="Billytics", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ------------------------------------------------------------
# ⚠️ DEV NOTE — VERIFY BEFORE DEMO (kept as a code comment only,
# not shown on screen, per team request). Update these two tables
# with current, dated figures before presenting:
#   - IESCO / NEPRA notified tariff: https://iesco.com.pk / https://nepra.org.pk
#   - DRAP medicine prices: https://dra.gov.pk
# ------------------------------------------------------------
IESCO_SLABS = [
    (100, 14.0),
    (200, 22.0),
    (300, 27.0),
    (400, 32.0),
    (700, 40.0),
    (float("inf"), 45.0),
]
GST_RATE = 0.17
FC_SURCHARGE_PER_UNIT = 0.43
TV_FEE = 35

MEDICINES = [
    {"name": "Panadol 500mg", "salt": "Paracetamol", "price": 25, "pack": "10 tablets"},
    {"name": "Calpol 500mg", "salt": "Paracetamol", "price": 20, "pack": "10 tablets"},
    {"name": "Brufen 400mg", "salt": "Ibuprofen", "price": 45, "pack": "10 tablets"},
    {"name": "Augmentin 625mg", "salt": "Amoxicillin+Clavulanate", "price": 450, "pack": "10 tablets"},
    {"name": "Amoxil 500mg", "salt": "Amoxicillin", "price": 120, "pack": "10 tablets"},
    {"name": "Disprin", "salt": "Aspirin", "price": 15, "pack": "10 tablets"},
    {"name": "Risek 20mg", "salt": "Omeprazole", "price": 180, "pack": "14 capsules"},
    {"name": "Omezol 20mg", "salt": "Omeprazole", "price": 90, "pack": "14 capsules"},
    {"name": "Flagyl 400mg", "salt": "Metronidazole", "price": 60, "pack": "10 tablets"},
    {"name": "Ponstan 500mg", "salt": "Mefenamic Acid", "price": 70, "pack": "10 tablets"},
    {"name": "Arinac Forte", "salt": "Paracetamol+Phenylephrine+CPM", "price": 65, "pack": "10 tablets"},
    {"name": "Flumax", "salt": "Paracetamol+Phenylephrine+CPM", "price": 40, "pack": "10 tablets"},
    {"name": "Zyrtec 10mg", "salt": "Cetirizine", "price": 95, "pack": "10 tablets"},
    {"name": "Cetrizine (generic)", "salt": "Cetirizine", "price": 25, "pack": "10 tablets"},
    {"name": "Panadol CF", "salt": "Paracetamol+Phenylephrine+CPM", "price": 55, "pack": "10 tablets"},
    {"name": "Buscopan", "salt": "Hyoscine", "price": 110, "pack": "10 tablets"},
    {"name": "Nexum 40mg", "salt": "Esomeprazole", "price": 210, "pack": "14 capsules"},
    {"name": "Glucophage 500mg", "salt": "Metformin", "price": 130, "pack": "20 tablets"},
    {"name": "Metric 500mg", "salt": "Metformin", "price": 55, "pack": "20 tablets"},
    {"name": "Concor 5mg", "salt": "Bisoprolol", "price": 250, "pack": "14 tablets"},
    {"name": "Lipiget 10mg", "salt": "Atorvastatin", "price": 140, "pack": "10 tablets"},
    {"name": "Rigix 10mg", "salt": "Atorvastatin", "price": 70, "pack": "10 tablets"},
    {"name": "Surbex-Z", "salt": "Multivitamin+Zinc", "price": 260, "pack": "30 capsules"},
    {"name": "Neurobion Forte", "salt": "Vitamin B Complex", "price": 220, "pack": "30 tablets"},
    {"name": "Calpol Syrup", "salt": "Paracetamol Syrup", "price": 110, "pack": "60ml"},
]

APPLIANCE_TIPS = [
    {"en": "Reduce AC use by 2 hours/day", "ur": "AC کا استعمال روزانہ 2 گھنٹے کم کریں", "units": 60},
    {"en": "Switch 5 bulbs to LED", "ur": "5 بلب LED میں تبدیل کریں", "units": 20},
    {"en": "Use geyser 30 min less/day", "ur": "گیزر روزانہ 30 منٹ کم چلائیں", "units": 25},
    {"en": "Turn off standby devices at night", "ur": "رات کو اضافی آلات بند کر دیں", "units": 10},
    {"en": "Service AC filters (improves efficiency)", "ur": "AC فلٹر صاف کروائیں", "units": 15},
    {"en": "Use washing machine on full loads only", "ur": "واشنگ مشین صرف بھری ہوئی چلائیں", "units": 8},
    {"en": "Reduce iron use / iron in bulk", "ur": "استری کا استعمال کم / اکٹھا کریں", "units": 6},
]

# ------------------------------------------------------------
# LANGUAGE
# ------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"

def T(en, ur):
    return ur if st.session_state.lang == "ur" else en

def toggle_lang():
    st.session_state.lang = "ur" if st.session_state.lang == "en" else "en"

# ------------------------------------------------------------
# THEME — deep blue / solid grey / electric blue / orange accents
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(43,109,255,0.10) 0%, transparent 40%),
        radial-gradient(circle at 85% 90%, rgba(255,140,0,0.06) 0%, transparent 40%),
        linear-gradient(180deg, #05070d 0%, #0a0e1a 40%, #14161c 100%);
    color: #dbe7ff;
}

h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #7ec8ff; }

.billytics-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #4fd0ff, #2b6dff, #ffb347);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite;
}
@keyframes shine { to { background-position: 200% center; } }

.billytics-tag { text-align:center; color:#9fb7dd; font-size:1.05rem; margin-top:-8px; margin-bottom: 10px;}

.bolt { display:inline-block; animation: flicker 1.6s infinite; }
@keyframes flicker {
  0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 8px #4fd0ff, 0 0 18px #2b6dff; }
  20%, 22%, 24%, 55% { opacity: 0.35; text-shadow: none; }
}
.coin { display:inline-block; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%,100%{ transform: translateY(0px);} 50%{ transform: translateY(-10px);} }

.bg-float {
    position: fixed;
    font-size: 2.2rem;
    opacity: 0.10;
    z-index: 0;
    animation: bgfloat 9s ease-in-out infinite;
    pointer-events: none;
}
@keyframes bgfloat {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-30px) rotate(8deg); }
}

.spark-field { position: relative; height: 0; }
.spark {
    position: absolute; bottom: 0; width: 2px; height: 2px; border-radius: 50%;
    background: #4fd0ff; box-shadow: 0 0 8px 2px #4fd0ff;
    animation: rise 4s linear infinite;
}
@keyframes rise {
    0% { transform: translateY(0) scale(1); opacity: 0; }
    10% { opacity: 1; }
    100% { transform: translateY(-160px) scale(0.3); opacity: 0; }
}

.feature-icon {
    font-size: 2.6rem;
    text-align: center;
    display: block;
    margin-bottom: 4px;
    animation: pulseglow 2.4s ease-in-out infinite;
}
@keyframes pulseglow {
    0%, 100% { filter: drop-shadow(0 0 4px rgba(79,208,255,0.4)); }
    50% { filter: drop-shadow(0 0 14px rgba(79,208,255,0.9)); }
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(22,34,60,0.85), rgba(12,16,28,0.9));
    border: 1px solid rgba(79,208,255,0.3) !important;
    border-radius: 16px !important;
    transition: 0.25s;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #ff9d3d !important;
    box-shadow: 0 0 22px rgba(255,157,61,0.25);
}

.footer-box {
    text-align:center;
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid rgba(79,208,255,0.25);
    color: #7fa8d9;
    font-size: 0.95rem;
}
.pk-line { color: #ffb347; font-weight: 600; margin-top: 6px; }

div.stButton > button {
    background: linear-gradient(135deg, #ff8a1e, #ff5e1e);
    color: #10131c;
    border: 1px solid #ffb347;
    border-radius: 12px;
    padding: 12px 10px;
    font-weight: 800;
    width: 100%;
    transition: 0.2s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #ffb347, #ff8a1e);
    color: #05070d;
    border-color: #4fd0ff;
    box-shadow: 0 0 18px rgba(255,157,61,0.6);
    transform: translateY(-2px);
}
.back-btn button, .lang-btn button {
    background: #161b2c !important;
    color: #7ec8ff !important;
    border: 1px solid #2b6dff !important;
    font-weight:600 !important;
}
.back-btn button:hover, .lang-btn button:hover {
    background: #1f2740 !important;
    box-shadow: 0 0 10px rgba(79,208,255,0.5);
}

.metric-good { color: #4ade80; font-weight:700; }
.metric-bad { color: #f87171; font-weight:700; }
.metric-warn { color: #fbbf24; font-weight:700; }

.info-box {
    background: rgba(43,109,255,0.10);
    border: 1px solid rgba(79,208,255,0.35);
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    color: #cfe4ff;
}
</style>
<div class="spark-field">
  <div class="spark" style="left:8%; animation-delay:0s;"></div>
  <div class="spark" style="left:22%; animation-delay:1s;"></div>
  <div class="spark" style="left:41%; animation-delay:2s;"></div>
  <div class="spark" style="left:63%; animation-delay:0.6s;"></div>
  <div class="spark" style="left:78%; animation-delay:1.8s;"></div>
  <div class="spark" style="left:92%; animation-delay:2.6s;"></div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "bill_data" not in st.session_state:
    st.session_state.bill_data = None

def go(page):
    st.session_state.page = page
    st.rerun()

def header_bar(show_back=True):
    col1, col2, col3 = st.columns([1, 1.3, 5])
    with col1:
        if show_back:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button(T("⬅ Home", "⬅ ہوم")):
                go("home")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="lang-btn">', unsafe_allow_html=True)
        label = "🌐 اردو" if st.session_state.lang == "en" else "🌐 English"
        if st.button(label):
            toggle_lang()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# CALCULATION HELPERS (pure math — no AI guessing on numbers)
# ------------------------------------------------------------
def bill_from_units(units):
    remaining = units
    lower = 0
    cost = 0.0
    breakdown = []
    for cap, rate in IESCO_SLABS:
        slab_units = max(0, min(remaining, cap - lower))
        if slab_units > 0:
            slab_cost = slab_units * rate
            breakdown.append((f"{lower+1}-{cap if cap != float('inf') else '∞'} units @ Rs{rate}", slab_units, slab_cost))
            cost += slab_cost
            remaining -= slab_units
        lower = cap
        if remaining <= 0:
            break
    fc_surcharge = units * FC_SURCHARGE_PER_UNIT
    gst = (cost + fc_surcharge) * GST_RATE
    total = cost + fc_surcharge + gst + TV_FEE
    return {"energy_cost": cost, "fc_surcharge": fc_surcharge, "gst": gst, "tv_fee": TV_FEE, "total": total, "breakdown": breakdown}

def next_slab_info(units):
    for cap, rate in IESCO_SLABS:
        if units <= cap:
            if cap == float("inf"):
                return None
            units_left = cap - units
            current_bill = bill_from_units(units)["total"]
            next_bill = bill_from_units(cap + 1)["total"]
            return {"units_left": units_left, "next_cap": cap, "jump_cost": next_bill - current_bill}
    return None

def bill_health_check(stated_amount, computed_amount, prev_units=None, curr_units=None):
    flags = []
    status = "green"
    if stated_amount and computed_amount:
        diff_pct = abs(stated_amount - computed_amount) / computed_amount * 100
        if diff_pct > 15:
            flags.append(T(f"Stated amount is {diff_pct:.0f}% different from our calculated amount — worth double-checking.",
                            f"بل کی رقم ہمارے حساب سے {diff_pct:.0f}% مختلف ہے — دوبارہ چیک کریں۔"))
            status = "red"
        elif diff_pct > 7:
            flags.append(T(f"Stated amount is {diff_pct:.0f}% off from our calculation — minor mismatch.",
                            f"رقم میں {diff_pct:.0f}% کا معمولی فرق ہے۔"))
            status = "amber" if status == "green" else status
    if prev_units and curr_units:
        change_pct = (curr_units - prev_units) / prev_units * 100 if prev_units else 0
        if change_pct > 40:
            flags.append(T(f"Usage jumped {change_pct:.0f}% vs last month — check for new appliances or a meter issue.",
                            f"استعمال پچھلے مہینے سے {change_pct:.0f}% بڑھ گیا — چیک کریں۔"))
            status = "red"
        elif change_pct > 20:
            flags.append(T(f"Usage rose {change_pct:.0f}% vs last month.", f"استعمال {change_pct:.0f}% بڑھا ہے۔"))
            status = "amber" if status == "green" else status
    if not flags:
        flags.append(T("Nothing unusual found. Bill looks consistent with standard tariff calculation.",
                        "کوئی مسئلہ نہیں ملا۔ بل معمول کے مطابق ہے۔"))
    return status, flags

def solar_payback(avg_monthly_bill, system_cost_per_kw=180000, unit_rate=35):
    monthly_units = avg_monthly_bill / unit_rate if unit_rate else 0
    kw_needed = max(1, round(monthly_units / 120, 1))
    system_cost = kw_needed * system_cost_per_kw
    monthly_saving = avg_monthly_bill * 0.85
    payback_years = system_cost / (monthly_saving * 12) if monthly_saving else 0
    return {"kw_needed": kw_needed, "system_cost": system_cost, "monthly_saving": monthly_saving, "payback_years": payback_years}

def fuzzy_find_medicine(query):
    names = [m["name"] for m in MEDICINES]
    salts = [m["salt"] for m in MEDICINES]
    matches = difflib.get_close_matches(query, names, n=5, cutoff=0.3)
    if not matches:
        matches = difflib.get_close_matches(query, salts, n=5, cutoff=0.3)
        results = [m for m in MEDICINES if m["salt"] in matches]
    else:
        results = [m for m in MEDICINES if m["name"] in matches]
    return results

def alternatives_by_salt(salt):
    return sorted([m for m in MEDICINES if m["salt"] == salt], key=lambda x: x["price"])

# ------------------------------------------------------------
# GROQ API — used ONLY to read/extract bill fields & explain in Urdu.
# All money math is done by the functions above, never by the model.
# ------------------------------------------------------------
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_TEXT_MODEL = "llama-3.3-70b-versatile"

def call_groq(messages, model, max_tokens=1024):
    try:
        from groq import Groq
    except ImportError:
        st.error("The 'groq' package isn't installed. Add it to requirements.txt.")
        return None
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        st.error("No GROQ_API_KEY found in Streamlit secrets.")
        return None
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
    return resp.choices[0].message.content

def extract_bill_fields(image_bytes, media_type):
    b64 = base64.b64encode(image_bytes).decode()
    data_url = f"data:{media_type};base64,{b64}"
    system = (
        "You extract fields from a Pakistani electricity bill photo. "
        "Return ONLY valid JSON, no extra text, with keys: "
        "units_consumed (number), stated_amount (number), billing_month (string), "
        "due_date (string), meter_number (string or null). "
        "If a field is unreadable, use null. Never invent numbers."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": [
            {"type": "text", "text": "Extract the bill fields as instructed."},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]},
    ]
    raw = call_groq(messages, model=GROQ_VISION_MODEL, max_tokens=400)
    if not raw:
        return None
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return None

def urdu_explain(bill_calc, units):
    system = "Explain this electricity bill breakdown in simple, friendly Roman Urdu (Urdu written in English letters). Keep it under 120 words. Use the exact numbers given — never change them."
    text = (f"Units: {units}, Energy cost: Rs {bill_calc['energy_cost']:.0f}, "
            f"Fuel surcharge: Rs {bill_calc['fc_surcharge']:.0f}, GST: Rs {bill_calc['gst']:.0f}, "
            f"TV fee: Rs {bill_calc['tv_fee']}, Total: Rs {bill_calc['total']:.0f}")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": text}]
    return call_groq(messages, model=GROQ_TEXT_MODEL, max_tokens=300)

def draft_complaint(flags, bill_data):
    system = "Write a short, polite, formal complaint letter (English) to a Pakistani electricity company (IESCO-style) about the billing issues listed. Under 150 words. Include placeholders [Your Name], [Account Number], [Address]."
    text = "Issues found: " + "; ".join(flags) + f"\nBill data: {bill_data}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": text}]
    return call_groq(messages, model=GROQ_TEXT_MODEL, max_tokens=350)

# ==============================================================
# PAGE: HOME
# ==============================================================
def page_home():
    header_bar(show_back=False)

    st.markdown("""
    <div class="bg-float" style="top:15%; left:6%;">⚡</div>
    <div class="bg-float" style="top:70%; left:10%; animation-delay:2s;">💰</div>
    <div class="bg-float" style="top:25%; left:88%; animation-delay:4s;">🪙</div>
    <div class="bg-float" style="top:78%; left:85%; animation-delay:1s;">⚡</div>
    """, unsafe_allow_html=True)

    logo_col = st.columns([1, 0.5, 1])[1]
    with logo_col:
        try:
            b64_logo = base64.b64encode(open("logo.png", "rb").read()).decode()
            st.markdown(
                f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{b64_logo}" width="140"></div>',
                unsafe_allow_html=True,
            )
        except Exception:
            pass

    st.markdown('<div class="billytics-title">BILLYTICS</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="billytics-tag"><span class="bolt">⚡</span> {T("Your Bill Decoder · Pakistan", "آپ کا بل ڈی کوڈر · پاکستان")} <span class="coin">💰</span></div>',
        unsafe_allow_html=True,
    )
    st.write("")

    features = [
        ("⚡", T("Bill Decoder", "بل ڈی کوڈر"), "bill_decoder", T("Upload your bill photo, get a full breakdown.", "اپنا بل اپ لوڈ کریں، مکمل تفصیل حاصل کریں۔")),
        ("🎯", T("Slab Trap Checker", "سلیب ٹریپ چیکر"), "slab_trap", T("See how close you are to the next pricier slab.", "دیکھیں اگلا مہنگا سلیب کتنا قریب ہے۔")),
        ("💰", T("Savings Calculator", "بچت کیلکولیٹر"), "savings", T("Find out how much simple habit changes save.", "چھوٹی تبدیلیوں سے کتنی بچت ہوگی، جانیں۔")),
        ("🩺", T("Bill Health Check", "بل ہیلتھ چیک"), "health_check", T("Spot errors or unusual jumps in your bill.", "بل میں غلطی یا غیر معمولی اضافہ چیک کریں۔")),
        ("☀️", T("Solar Payback", "سولر پے بیک"), "solar", T("Estimate solar system size & payback years.", "سولر سسٹم کا سائز اور بچت کا وقت جانیں۔")),
        ("📝", T("Complaint Letter", "شکایتی خط"), "complaint", T("Auto-draft a complaint if something looks wrong.", "مسئلہ ہو تو خودکار شکایتی خط بنائیں۔")),
        ("🌐", T("Urdu Explainer", "اردو وضاحت"), "urdu", T("Get your bill explained in simple Roman Urdu.", "اپنا بل آسان اردو میں سمجھیں۔")),
        ("💊", T("Dawa Sasti", "دوا سستی"), "dawa_sasti", T("Find medicine prices & cheaper alternatives.", "دوا کی قیمت اور سستا متبادل تلاش کریں۔")),
    ]

    cols = st.columns(4)
    for i, (icon, label, key, desc) in enumerate(features):
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f'<span class="feature-icon">{icon}</span>', unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-weight:700; margin-bottom:4px;'>{label}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-size:0.85rem; color:#9fb7dd; min-height:48px;'>{desc}</div>", unsafe_allow_html=True)
                if st.button(T("Open", "کھولیں"), key=f"btn_{key}"):
                    go(key)

    st.markdown(
        f"""
        <div class="footer-box">
            <b>{T("Team Two Devs", "ٹیم ٹو ڈیوز")}</b><br>
            Umamah Nasir &nbsp;•&nbsp; Chaudhary Muhammad Huzaifa Ali<br>
            <span style="font-size:0.8rem;">{T("Built for Imaginathon — banao.pk", "امیجینیتھون کے لیے بنایا گیا — banao.pk")}</span>
            <div class="pk-line">{T("Made in Pakistan, for Pakistan", "پاکستان میں، پاکستان کے لیے بنایا گیا")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================
# PAGE: BILL DECODER
# ==============================================================
def page_bill_decoder():
    header_bar()
    st.header(f"⚡ {T('Bill Decoder', 'بل ڈی کوڈر')}")
    st.markdown(f'<div class="info-box">{T("Upload a photo of your electricity bill and this tool reads the units and amount, then calculates the exact slab-by-slab cost, surcharges, tax and total — using real tariff math, not guesswork.", "اپنا بجلی کا بل اپ لوڈ کریں، یہ ٹول یونٹس اور رقم پڑھ کر مکمل حساب لگاتا ہے۔")}</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([T("📷 Upload Bill Photo", "📷 بل کی تصویر"), T("✍️ Manual Entry", "✍️ خود لکھیں")])

    with tab1:
        uploaded = st.file_uploader(T("Upload bill image", "بل کی تصویر اپ لوڈ کریں"), type=["png", "jpg", "jpeg"])
        if uploaded and st.button(T("Decode Bill", "بل پڑھیں"), key="decode_btn"):
            with st.spinner(T("Reading your bill...", "بل پڑھا جا رہا ہے...")):
                fields = extract_bill_fields(uploaded.getvalue(), uploaded.type)
            if fields and fields.get("units_consumed"):
                st.session_state.bill_data = fields
                st.success(T("Bill read successfully. See breakdown below.", "بل کامیابی سے پڑھا گیا۔"))
            else:
                st.error(T("Couldn't read the bill clearly. Try Manual Entry instead.", "بل صاف نہیں پڑھا جا سکا۔ خود لکھیں۔"))

    with tab2:
        units_manual = st.number_input(T("Units consumed", "استعمال شدہ یونٹس"), min_value=0, value=0, step=1)
        amount_manual = st.number_input(T("Stated bill amount (Rs)", "بل کی رقم (روپے)"), min_value=0, value=0, step=100)
        if st.button(T("Calculate", "حساب لگائیں"), key="manual_btn"):
            st.session_state.bill_data = {"units_consumed": units_manual, "stated_amount": amount_manual, "billing_month": None}

    data = st.session_state.bill_data
    if data and data.get("units_consumed"):
        units = float(data["units_consumed"])
        calc = bill_from_units(units)
        st.subheader(f"📊 {T('Breakdown', 'تفصیل')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(T("Units", "یونٹس"), f"{units:.0f}")
        c2.metric(T("Energy Cost", "توانائی لاگت"), f"Rs {calc['energy_cost']:.0f}")
        c3.metric(T("Fuel Surcharge", "فیول سرچارج"), f"Rs {calc['fc_surcharge']:.0f}")
        c4.metric(T("Estimated Total", "کل تخمینہ"), f"Rs {calc['total']:.0f}")

        with st.expander(T("See slab-by-slab detail", "سلیب کی تفصیل دیکھیں")):
            for label, u, c in calc["breakdown"]:
                st.write(f"- {label}: {u:.0f} units → Rs {c:.0f}")
            st.write(f"GST ({GST_RATE*100:.0f}%): Rs {calc['gst']:.0f}")
            st.write(f"TV Fee: Rs {calc['tv_fee']}")

        if data.get("stated_amount"):
            diff = data["stated_amount"] - calc["total"]
            if abs(diff) > calc["total"] * 0.1:
                st.warning(T(f"Your stated bill differs from our calculation by Rs {abs(diff):.0f}. Check Bill Health Check.", f"آپ کے بل میں Rs {abs(diff):.0f} کا فرق ہے۔"))
            else:
                st.success(T("Your stated bill matches our calculation closely. ✅", "آپ کا بل ہمارے حساب سے میل کھاتا ہے۔ ✅"))

        nxt = next_slab_info(units)
        if nxt:
            st.info(T(f"🎯 You're **{nxt['units_left']:.0f} units** away from the next slab. Crossing it adds **Rs {nxt['jump_cost']:.0f}**.",
                      f"🎯 اگلے سلیب سے **{nxt['units_left']:.0f} یونٹس** دور ہیں۔ اس کے بعد **Rs {nxt['jump_cost']:.0f}** بڑھ جائیں گے۔"))
    else:
        st.info(T("Upload a bill or enter units to see your breakdown.", "بل اپ لوڈ کریں یا یونٹس درج کریں۔"))

# ==============================================================
# PAGE: SLAB TRAP CHECKER
# ==============================================================
def page_slab_trap():
    header_bar()
    st.header(f"🎯 {T('Slab Trap Checker', 'سلیب ٹریپ چیکر')}")
    st.markdown(f'<div class="info-box">{T("Electricity tariffs jump in slabs — a few extra units can push your whole bill into a pricier rate. This tool shows exactly how many units of room you have left.", "بجلی کا ریٹ سلیب میں بڑھتا ہے — چند یونٹس بھی پورا بل مہنگا کر سکتے ہیں۔")}</div>', unsafe_allow_html=True)
    default_units = float(st.session_state.bill_data.get("units_consumed", 0)) if st.session_state.bill_data else 0
    units = st.number_input(T("Units consumed this month", "اس ماہ کے یونٹس"), min_value=0, value=int(default_units), step=1)
    if units:
        nxt = next_slab_info(units)
        if nxt:
            units_left_txt = f"{nxt['units_left']:.0f}"
            jump_cost_txt = f"{nxt['jump_cost']:.0f}"
            st.markdown("### " + T(f"You are **{units_left_txt} units** away from the next slab.",
                                    f"اگلے سلیب سے **{units_left_txt} یونٹس** دور ہیں۔"))
            st.markdown(T(f"Crossing into the next slab would add **Rs {jump_cost_txt}** to your total bill.",
                           f"اگلے سلیب میں جانے سے **Rs {jump_cost_txt}** بڑھ جائیں گے۔"))
            st.progress(min(1.0, units / nxt["next_cap"]))
        else:
            st.info(T("You're already in the highest slab — no further slab jump ahead.", "آپ سب سے اونچے سلیب میں ہیں۔"))

# ==============================================================
# PAGE: SAVINGS CALCULATOR
# ==============================================================
def page_savings():
    header_bar()
    st.header(f"💰 {T('Savings Calculator', 'بچت کیلکولیٹر')}")
    st.markdown(f'<div class="info-box">{T("Tick the changes you\'re willing to make, and see the estimated monthly savings in both units and rupees.", "جو تبدیلیاں کرنا چاہیں وہ منتخب کریں، ماہانہ بچت دیکھیں۔")}</div>', unsafe_allow_html=True)
    default_units = float(st.session_state.bill_data.get("units_consumed", 200)) if st.session_state.bill_data else 200
    unit_rate = st.number_input(T("Your approx. rate per unit (Rs)", "فی یونٹ تخمینی ریٹ (روپے)"), min_value=1.0, value=30.0, step=1.0)

    total_units_saved = 0
    for tip in APPLIANCE_TIPS:
        label = f"{T(tip['en'], tip['ur'])}  (~{tip['units']} {T('units/month', 'یونٹس/ماہ')})"
        if st.checkbox(label):
            total_units_saved += tip["units"]

    if total_units_saved:
        rs_saved = total_units_saved * unit_rate
        st.markdown(f"### 💸 {T(f'Estimated savings: **Rs {rs_saved:.0f}/month**', f'تخمینی بچت: **Rs {rs_saved:.0f}/ماہ**')}")
        new_units = max(0, default_units - total_units_saved)
        old_bill = bill_from_units(default_units)["total"]
        new_bill = bill_from_units(new_units)["total"]
        st.write(T(f"Your bill could drop from **Rs {old_bill:.0f}** to about **Rs {new_bill:.0f}**.", f"آپ کا بل **Rs {old_bill:.0f}** سے **Rs {new_bill:.0f}** تک آ سکتا ہے۔"))
    else:
        st.info(T("Select at least one change above to see your savings.", "بچت دیکھنے کے لیے کم از کم ایک تبدیلی منتخب کریں۔"))

# ==============================================================
# PAGE: BILL HEALTH CHECK
# ==============================================================
def page_health_check():
    header_bar()
    st.header(f"🩺 {T('Bill Health Check', 'بل ہیلتھ چیک')}")
    st.markdown(f'<div class="info-box">{T("Runs quick checks on your bill: does the amount match the units, and did your usage jump unusually versus last month.", "آپ کے بل پر فوری چیک: رقم اور یونٹس میل کھاتے ہیں یا نہیں، اور استعمال میں غیر معمولی اضافہ تو نہیں۔")}</div>', unsafe_allow_html=True)
    data = st.session_state.bill_data or {}
    units = st.number_input(T("This month's units", "اس ماہ کے یونٹس"), min_value=0, value=int(data.get("units_consumed", 0)))
    amount = st.number_input(T("Stated bill amount (Rs)", "بل کی رقم (روپے)"), min_value=0, value=int(data.get("stated_amount", 0)))
    prev_units = st.number_input(T("Last month's units (optional)", "پچھلے ماہ کے یونٹس (اختیاری)"), min_value=0, value=0)

    if st.button(T("Run Health Check", "چیک کریں")):
        calc = bill_from_units(units)
        status, flags = bill_health_check(amount, calc["total"], prev_units or None, units)
        color_class = {"green": "metric-good", "amber": "metric-warn", "red": "metric-bad"}[status]
        label = {"green": T("✅ HEALTHY", "✅ ٹھیک ہے"), "amber": T("⚠️ CHECK THIS", "⚠️ چیک کریں"), "red": T("🚨 NEEDS ATTENTION", "🚨 توجہ درکار ہے")}[status]
        st.markdown(f"<h3 class='{color_class}'>{label}</h3>", unsafe_allow_html=True)
        for f in flags:
            st.write(f"- {f}")

# ==============================================================
# PAGE: SOLAR PAYBACK
# ==============================================================
def page_solar():
    header_bar()
    st.header(f"☀️ {T('Solar Payback Estimator', 'سولر پے بیک اندازہ')}")
    st.markdown(f'<div class="info-box">{T("A rough estimate of solar system size and how many years it takes to pay for itself, based on your average bill. Actual results depend on installer quotes and sunlight hours.", "سولر سسٹم کا سائز اور واپسی کا وقت — یہ ایک تخمینہ ہے، اصل نتائج مختلف ہو سکتے ہیں۔")}</div>', unsafe_allow_html=True)
    avg_bill = st.number_input(T("Average monthly bill (Rs)", "اوسط ماہانہ بل (روپے)"), min_value=0, value=15000, step=500)
    if avg_bill:
        result = solar_payback(avg_bill)
        c1, c2, c3 = st.columns(3)
        c1.metric(T("System size needed", "درکار سسٹم سائز"), f"{result['kw_needed']} kW")
        c2.metric(T("Est. system cost", "تخمینی لاگت"), f"Rs {result['system_cost']:,.0f}")
        c3.metric(T("Payback period", "واپسی کا وقت"), f"{result['payback_years']:.1f} {T('years','سال')}")

# ==============================================================
# PAGE: COMPLAINT LETTER
# ==============================================================
def page_complaint():
    header_bar()
    st.header(f"📝 {T('Complaint Letter Generator', 'شکایتی خط بنائیں')}")
    st.markdown(f'<div class="info-box">{T("Describe what looks wrong with your bill (or run Bill Health Check first) and this drafts a polite, formal complaint letter you can send to your electricity company.", "بل میں مسئلہ بیان کریں، یہ ایک باضابطہ شکایتی خط بنا دے گا۔")}</div>', unsafe_allow_html=True)
    issue = st.text_area(T("Describe the issue", "مسئلہ بیان کریں"), height=100)
    if st.button(T("Generate Letter", "خط بنائیں")):
        if not issue:
            issue = "Bill amount seems inconsistent with the units consumed this month."
        with st.spinner(T("Drafting your letter...", "خط لکھا جا رہا ہے...")):
            letter = draft_complaint([issue], st.session_state.bill_data or {})
        if letter:
            st.text_area(T("Your draft letter", "آپ کا خط"), letter, height=250)
        else:
            st.error(T("Couldn't generate the letter. Check your API key in secrets.", "خط نہیں بن سکا، API key چیک کریں۔"))

# ==============================================================
# PAGE: URDU EXPLAINER
# ==============================================================
def page_urdu():
    header_bar()
    st.header(f"🌐 {T('Urdu Explainer', 'اردو وضاحت')}")
    st.markdown(f'<div class="info-box">{T("Get your already-decoded bill explained in simple, friendly Roman Urdu — same numbers, easier words.", "اپنا بل آسان اردو میں سمجھیں — وہی اعداد، آسان الفاظ۔")}</div>', unsafe_allow_html=True)
    data = st.session_state.bill_data
    if not data or not data.get("units_consumed"):
        st.info(T("Decode a bill first (Bill Decoder page), then come back here.", "پہلے بل ڈی کوڈر میں بل پڑھیں۔"))
        return
    units = float(data["units_consumed"])
    calc = bill_from_units(units)
    if st.button(T("Explain in Urdu", "اردو میں سمجھائیں")):
        with st.spinner(T("Translating...", "ترجمہ ہو رہا ہے...")):
            explanation = urdu_explain(calc, units)
        if explanation:
            st.markdown(f"### {explanation}")
        else:
            st.error(T("Couldn't generate explanation. Check your API key in secrets.", "وضاحت نہیں بن سکی۔"))

# ==============================================================
# PAGE: DAWA SASTI
# ==============================================================
def page_dawa_sasti():
    header_bar()
    st.header(f"💊 {T('Dawa Sasti', 'دوا سستی')}")
    st.markdown(f'<div class="info-box">{T("Search a medicine name to see its price and any cheaper alternatives that share the same active salt.", "دوا کا نام لکھیں، قیمت اور سستا متبادل دیکھیں۔")}</div>', unsafe_allow_html=True)
    query = st.text_input(T("Medicine name", "دوا کا نام"))
    if query:
        results = fuzzy_find_medicine(query)
        if results:
            for med in results:
                st.markdown(f"**{med['name']}** ({med['pack']}) — Rs {med['price']} · {T('Salt', 'نمک')}: _{med['salt']}_")
                alts = [m for m in alternatives_by_salt(med["salt"]) if m["name"] != med["name"]]
                cheaper = [a for a in alts if a["price"] < med["price"]]
                if cheaper:
                    st.success(T("Cheaper alternatives with the same salt:", "سستے متبادل:"))
                    for a in cheaper:
                        st.write(f"  - {a['name']} — Rs {a['price']} ({a['pack']})")
                st.write("---")
        else:
            st.warning(T("No match found in our sample database. Try a different spelling.", "کوئی نتیجہ نہیں ملا۔"))

# ==============================================================
# ROUTER
# ==============================================================
PAGES = {
    "home": page_home,
    "bill_decoder": page_bill_decoder,
    "slab_trap": page_slab_trap,
    "savings": page_savings,
    "health_check": page_health_check,
    "solar": page_solar,
    "complaint": page_complaint,
    "urdu": page_urdu,
    "dawa_sasti": page_dawa_sasti,
}

PAGES[st.session_state.page]()
