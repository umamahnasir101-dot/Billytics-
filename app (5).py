import streamlit as st
import base64
import json
import re
import difflib
from datetime import datetime

# ============================================================
# BILLYTICS — Pakistan Bill Decoder & Household Savings Tool
# Team Two Devs — Umamah Nasir & Chaudhary Muhammad Huzaifa Ali
# ============================================================

st.set_page_config(page_title="Billytics", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ------------------------------------------------------------
# ⚠️ VERIFY BEFORE DEMO ⚠️
# These are SAMPLE / PLACEHOLDER rates for the MVP demo.
# You MUST check the latest official rates before presenting:
#   - IESCO / NEPRA notified tariff: https://iesco.com.pk / https://nepra.org.pk
#   - DRAP medicine prices: https://dra.gov.pk
# Update the two dictionaries below (IESCO_SLABS, MEDICINES) with real,
# dated figures and change LAST_VERIFIED_DATE. Judges will ask about accuracy.
# ------------------------------------------------------------
LAST_VERIFIED_DATE = "NOT YET VERIFIED — update this before your demo"

# Domestic (non-life-line) approximate per-unit slabs in Rs/unit — SAMPLE ONLY
IESCO_SLABS = [
    (100, 14.0),
    (200, 22.0),
    (300, 27.0),
    (400, 32.0),
    (700, 40.0),
    (float("inf"), 45.0),
]
GST_RATE = 0.17          # General Sales Tax — verify current %
FC_SURCHARGE_PER_UNIT = 0.43   # Fuel Cost surcharge — verify current value
TV_FEE = 35              # PTV fee, flat — verify

# Small sample medicine price list — SAMPLE ONLY, verify against DRAP
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
    {"label": "Reduce AC use by 2 hours/day", "units_saved_per_month": 60},
    {"label": "Switch 5 bulbs to LED", "units_saved_per_month": 20},
    {"label": "Use geyser 30 min less/day", "units_saved_per_month": 25},
    {"label": "Turn off standby devices at night", "units_saved_per_month": 10},
    {"label": "Service AC filters (improves efficiency)", "units_saved_per_month": 15},
    {"label": "Use washing machine on full loads only", "units_saved_per_month": 8},
    {"label": "Reduce iron use / iron in bulk", "units_saved_per_month": 6},
]

# ------------------------------------------------------------
# THEME — Electric Blue / Dark Blue / Grey + animations
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 20% 20%, #10182b 0%, #0a0f1e 45%, #05070d 100%);
    color: #dbe7ff;
}

h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #7ec8ff; }

.billytics-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #4fd0ff, #2b6dff, #b6e6ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
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

.glow-card {
    background: linear-gradient(160deg, rgba(20,32,58,0.9), rgba(10,16,30,0.9));
    border: 1px solid rgba(79,208,255,0.35);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 0 18px rgba(43,109,255,0.15);
    transition: 0.25s;
}
.glow-card:hover { box-shadow: 0 0 28px rgba(79,208,255,0.45); border-color: #4fd0ff; }

.footer-box {
    text-align:center;
    margin-top: 50px;
    padding: 18px;
    border-top: 1px solid rgba(79,208,255,0.25);
    color: #7fa8d9;
    font-size: 0.95rem;
}

div.stButton > button {
    background: linear-gradient(135deg, #0f2244, #163a70);
    color: #cfe8ff;
    border: 1px solid #2b6dff;
    border-radius: 12px;
    padding: 14px 10px;
    font-weight: 700;
    width: 100%;
    transition: 0.2s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #163a70, #2b6dff);
    color: white;
    border-color: #7ec8ff;
    box-shadow: 0 0 16px rgba(79,208,255,0.6);
    transform: translateY(-2px);
}

.back-btn button { background: #1a1f33 !important; border: 1px solid #445 !important; font-weight:600 !important; }

.metric-good { color: #4ade80; font-weight:700; }
.metric-bad { color: #f87171; font-weight:700; }
.metric-warn { color: #fbbf24; font-weight:700; }

.verify-banner {
    background: rgba(251,191,36,0.12);
    border: 1px solid #fbbf24;
    color: #fde68a;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 0.85rem;
    margin-bottom: 14px;
}
</style>
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

def back_button():
    col1, _ = st.columns([1, 6])
    with col1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅ Home"):
            go("home")
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
    return {
        "energy_cost": cost,
        "fc_surcharge": fc_surcharge,
        "gst": gst,
        "tv_fee": TV_FEE,
        "total": total,
        "breakdown": breakdown,
    }

def next_slab_info(units):
    lower = 0
    for cap, rate in IESCO_SLABS:
        if units <= cap:
            if cap == float("inf"):
                return None
            units_left = cap - units
            current_bill = bill_from_units(units)["total"]
            next_bill = bill_from_units(cap + 1)["total"]
            jump = next_bill - current_bill
            return {"units_left": units_left, "next_cap": cap, "jump_cost": jump}
        lower = cap
    return None

def bill_health_check(stated_amount, computed_amount, prev_units=None, curr_units=None):
    flags = []
    status = "green"
    if stated_amount and computed_amount:
        diff_pct = abs(stated_amount - computed_amount) / computed_amount * 100
        if diff_pct > 15:
            flags.append(f"Stated amount is {diff_pct:.0f}% different from our calculated amount — worth double-checking.")
            status = "red"
        elif diff_pct > 7:
            flags.append(f"Stated amount is {diff_pct:.0f}% off from our calculation — minor mismatch, keep an eye on it.")
            status = "amber" if status == "green" else status
    if prev_units and curr_units:
        change_pct = (curr_units - prev_units) / prev_units * 100 if prev_units else 0
        if change_pct > 40:
            flags.append(f"Usage jumped {change_pct:.0f}% vs last month — check for new appliances or a meter issue.")
            status = "red"
        elif change_pct > 20:
            flags.append(f"Usage rose {change_pct:.0f}% vs last month.")
            status = "amber" if status == "green" else status
    if not flags:
        flags.append("Nothing unusual found. Bill looks consistent with standard tariff calculation.")
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
# CLAUDE API — used ONLY to read/extract bill fields & explain in Urdu.
# All money math is done by the functions above, never by the model.
# ------------------------------------------------------------
def call_claude(messages, system=None, max_tokens=1024):
    try:
        import anthropic
    except ImportError:
        st.error("The 'anthropic' package isn't installed. Add it to requirements.txt.")
        return None
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if not api_key:
        st.error("No ANTHROPIC_API_KEY found in Streamlit secrets.")
        return None
    client = anthropic.Anthropic(api_key=api_key)
    model = st.secrets.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system
    resp = client.messages.create(**kwargs)
    return "".join(block.text for block in resp.content if block.type == "text")

def extract_bill_fields(image_bytes, media_type):
    b64 = base64.b64encode(image_bytes).decode()
    system = (
        "You extract fields from a Pakistani electricity bill photo. "
        "Return ONLY valid JSON, no extra text, with keys: "
        "units_consumed (number), stated_amount (number), billing_month (string), "
        "due_date (string), meter_number (string or null). "
        "If a field is unreadable, use null. Never invent numbers."
    )
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": "Extract the bill fields as instructed."}
        ]
    }]
    raw = call_claude(messages, system=system, max_tokens=400)
    if not raw:
        return None
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return None

def urdu_explain(bill_calc, units):
    system = "Explain this electricity bill breakdown in simple, friendly Roman Urdu (Urdu written in English letters). Keep it under 120 words. Use the exact numbers given — never change them."
    text = (
        f"Units: {units}, Energy cost: Rs {bill_calc['energy_cost']:.0f}, "
        f"Fuel surcharge: Rs {bill_calc['fc_surcharge']:.0f}, GST: Rs {bill_calc['gst']:.0f}, "
        f"TV fee: Rs {bill_calc['tv_fee']}, Total: Rs {bill_calc['total']:.0f}"
    )
    messages = [{"role": "user", "content": text}]
    return call_claude(messages, system=system, max_tokens=300)

def draft_complaint(flags, bill_data):
    system = "Write a short, polite, formal complaint letter (English) to a Pakistani electricity company (IESCO-style) about the billing issues listed. Under 150 words. Include placeholders [Your Name], [Account Number], [Address]."
    text = "Issues found: " + "; ".join(flags) + f"\nBill data: {bill_data}"
    messages = [{"role": "user", "content": text}]
    return call_claude(messages, system=system, max_tokens=350)

# ==============================================================
# PAGE: HOME
# ==============================================================
def page_home():
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        try:
            st.image("logo.png", use_container_width=True)
        except Exception:
            pass

    st.markdown('<div class="billytics-title">BILLYTICS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="billytics-tag"><span class="bolt">⚡</span> Your Bill Decoder · Pakistan <span class="coin">💰</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="verify-banner">⚠️ Demo build — tariff &amp; medicine rates are sample figures. Last verified: {LAST_VERIFIED_DATE}. Verify against NEPRA/IESCO and DRAP before presenting.</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    features = [
        ("⚡ Bill Decoder", "bill_decoder", "Upload your bill photo, get a full breakdown."),
        ("🎯 Slab Trap Checker", "slab_trap", "See how close you are to the next pricier slab."),
        ("💰 Savings Calculator", "savings", "Find out how much simple habit changes save."),
        ("🩺 Bill Health Check", "health_check", "Spot errors or unusual jumps in your bill."),
        ("☀️ Solar Payback", "solar", "Estimate solar system size & payback years."),
        ("📝 Complaint Letter", "complaint", "Auto-draft a complaint if something looks wrong."),
        ("🌐 Urdu Explainer", "urdu", "Get your bill explained in simple Roman Urdu."),
        ("💊 Dawa Sasti", "dawa_sasti", "Find medicine prices & cheaper alternatives."),
    ]
    cols = st.columns(4)
    for i, (label, key, desc) in enumerate(features):
        with cols[i % 4]:
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown(f"**{label}**")
            st.caption(desc)
            if st.button("Open", key=f"btn_{key}"):
                go(key)
            st.markdown('</div>', unsafe_allow_html=True)
        if i % 4 == 3:
            st.write("")

    st.markdown(
        """
        <div class="footer-box">
            <b>Team Two Devs</b><br>
            Umamah Nasir &nbsp;•&nbsp; Chaudhary Muhammad Huzaifa Ali<br>
            <span style="font-size:0.8rem;">Built for Imaginathon — banao.pk</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================
# PAGE: BILL DECODER
# ==============================================================
def page_bill_decoder():
    back_button()
    st.header("⚡ Bill Decoder")
    st.caption("Upload a photo of your electricity bill, or enter units manually.")

    tab1, tab2 = st.tabs(["📷 Upload Bill Photo", "✍️ Manual Entry"])

    with tab1:
        uploaded = st.file_uploader("Upload bill image", type=["png", "jpg", "jpeg"])
        if uploaded and st.button("Decode Bill", key="decode_btn"):
            with st.spinner("Reading your bill..."):
                media_type = uploaded.type
                fields = extract_bill_fields(uploaded.getvalue(), media_type)
            if fields and fields.get("units_consumed"):
                st.session_state.bill_data = fields
                st.success("Bill read successfully. See breakdown below.")
            else:
                st.error("Couldn't read the bill clearly. Try Manual Entry instead, or a clearer photo.")

    with tab2:
        units_manual = st.number_input("Units consumed", min_value=0, value=0, step=1)
        amount_manual = st.number_input("Stated bill amount (Rs)", min_value=0, value=0, step=100)
        if st.button("Calculate", key="manual_btn"):
            st.session_state.bill_data = {"units_consumed": units_manual, "stated_amount": amount_manual, "billing_month": None}

    data = st.session_state.bill_data
    if data and data.get("units_consumed"):
        units = float(data["units_consumed"])
        calc = bill_from_units(units)
        st.subheader("📊 Breakdown")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Units", f"{units:.0f}")
        c2.metric("Energy Cost", f"Rs {calc['energy_cost']:.0f}")
        c3.metric("Fuel Surcharge", f"Rs {calc['fc_surcharge']:.0f}")
        c4.metric("Estimated Total", f"Rs {calc['total']:.0f}")

        with st.expander("See slab-by-slab detail"):
            for label, u, c in calc["breakdown"]:
                st.write(f"- {label}: {u:.0f} units → Rs {c:.0f}")
            st.write(f"GST ({GST_RATE*100:.0f}%): Rs {calc['gst']:.0f}")
            st.write(f"TV Fee: Rs {calc['tv_fee']}")

        if data.get("stated_amount"):
            diff = data["stated_amount"] - calc["total"]
            if abs(diff) > calc["total"] * 0.1:
                st.warning(f"Your stated bill (Rs {data['stated_amount']:.0f}) differs from our calculation by Rs {abs(diff):.0f}. Check the Bill Health Check page.")
            else:
                st.success("Your stated bill matches our calculation closely. ✅")

        nxt = next_slab_info(units)
        if nxt:
            st.info(f"🎯 You're **{nxt['units_left']:.0f} units** away from the next slab. Crossing it adds **Rs {nxt['jump_cost']:.0f}** to your bill.")
    else:
        st.info("Upload a bill or enter units to see your breakdown.")

# ==============================================================
# PAGE: SLAB TRAP CHECKER
# ==============================================================
def page_slab_trap():
    back_button()
    st.header("🎯 Slab Trap Checker")
    default_units = float(st.session_state.bill_data.get("units_consumed", 0)) if st.session_state.bill_data else 0
    units = st.number_input("Units consumed this month", min_value=0, value=int(default_units), step=1)
    if units:
        nxt = next_slab_info(units)
        if nxt:
            st.markdown(f"### You are **{nxt['units_left']:.0f} units** away from the next slab.")
            st.markdown(f"Crossing into the next slab would add **Rs {nxt['jump_cost']:.0f}** to your total bill.")
            st.progress(min(1.0, units / nxt["next_cap"]))
        else:
            st.info("You're already in the highest slab — no further slab jump ahead.")

# ==============================================================
# PAGE: SAVINGS CALCULATOR
# ==============================================================
def page_savings():
    back_button()
    st.header("💰 Savings Calculator")
    st.caption("Tick the changes you're willing to make, see estimated monthly savings.")
    default_units = float(st.session_state.bill_data.get("units_consumed", 200)) if st.session_state.bill_data else 200
    unit_rate = st.number_input("Your approx. rate per unit (Rs)", min_value=1.0, value=30.0, step=1.0)

    total_units_saved = 0
    for tip in APPLIANCE_TIPS:
        checked = st.checkbox(f"{tip['label']}  (~{tip['units_saved_per_month']} units/month)")
        if checked:
            total_units_saved += tip["units_saved_per_month"]

    if total_units_saved:
        rs_saved = total_units_saved * unit_rate
        st.markdown(f"### 💸 Estimated savings: **Rs {rs_saved:.0f}/month** ({total_units_saved} units)")
        new_units = max(0, default_units - total_units_saved)
        old_bill = bill_from_units(default_units)["total"]
        new_bill = bill_from_units(new_units)["total"]
        st.write(f"Your bill could drop from **Rs {old_bill:.0f}** to about **Rs {new_bill:.0f}**.")
    else:
        st.info("Select at least one change above to see your savings.")

# ==============================================================
# PAGE: BILL HEALTH CHECK
# ==============================================================
def page_health_check():
    back_button()
    st.header("🩺 Bill Health Check")
    data = st.session_state.bill_data or {}
    units = st.number_input("This month's units", min_value=0, value=int(data.get("units_consumed", 0)))
    amount = st.number_input("Stated bill amount (Rs)", min_value=0, value=int(data.get("stated_amount", 0)))
    prev_units = st.number_input("Last month's units (optional)", min_value=0, value=0)

    if st.button("Run Health Check"):
        calc = bill_from_units(units)
        status, flags = bill_health_check(amount, calc["total"], prev_units or None, units)
        color_class = {"green": "metric-good", "amber": "metric-warn", "red": "metric-bad"}[status]
        label = {"green": "✅ HEALTHY", "amber": "⚠️ CHECK THIS", "red": "🚨 NEEDS ATTENTION"}[status]
        st.markdown(f"<h3 class='{color_class}'>{label}</h3>", unsafe_allow_html=True)
        for f in flags:
            st.write(f"- {f}")

# ==============================================================
# PAGE: SOLAR PAYBACK
# ==============================================================
def page_solar():
    back_button()
    st.header("☀️ Solar Payback Estimator")
    st.caption("Rough estimate only — actual payback depends on installer quotes & sunlight hours.")
    avg_bill = st.number_input("Average monthly bill (Rs)", min_value=0, value=15000, step=500)
    if avg_bill:
        result = solar_payback(avg_bill)
        c1, c2, c3 = st.columns(3)
        c1.metric("System size needed", f"{result['kw_needed']} kW")
        c2.metric("Est. system cost", f"Rs {result['system_cost']:,.0f}")
        c3.metric("Payback period", f"{result['payback_years']:.1f} years")
        st.caption("Estimate assumes ~85% bill reduction and Rs 180,000/kW installation cost. Update these in code with current market rates.")

# ==============================================================
# PAGE: COMPLAINT LETTER
# ==============================================================
def page_complaint():
    back_button()
    st.header("📝 Complaint Letter Generator")
    issue = st.text_area("Describe the issue (or run Bill Health Check first)", height=100)
    if st.button("Generate Letter"):
        if not issue:
            issue = "Bill amount seems inconsistent with the units consumed this month."
        with st.spinner("Drafting your letter..."):
            letter = draft_complaint([issue], st.session_state.bill_data or {})
        if letter:
            st.text_area("Your draft letter", letter, height=250)
        else:
            st.error("Couldn't generate the letter. Check your API key in secrets.")

# ==============================================================
# PAGE: URDU EXPLAINER
# ==============================================================
def page_urdu():
    back_button()
    st.header("🌐 Urdu Explainer")
    data = st.session_state.bill_data
    if not data or not data.get("units_consumed"):
        st.info("Decode a bill first (Bill Decoder page), then come back here.")
        return
    units = float(data["units_consumed"])
    calc = bill_from_units(units)
    if st.button("Explain in Urdu"):
        with st.spinner("Translating..."):
            explanation = urdu_explain(calc, units)
        if explanation:
            st.markdown(f"### {explanation}")
        else:
            st.error("Couldn't generate explanation. Check your API key in secrets.")

# ==============================================================
# PAGE: DAWA SASTI
# ==============================================================
def page_dawa_sasti():
    back_button()
    st.header("💊 Dawa Sasti")
    st.caption("Search a medicine name to see its price and cheaper alternatives with the same salt.")
    query = st.text_input("Medicine name")
    if query:
        results = fuzzy_find_medicine(query)
        if results:
            for med in results:
                st.markdown(f"**{med['name']}** ({med['pack']}) — Rs {med['price']} · Salt: _{med['salt']}_")
                alts = [m for m in alternatives_by_salt(med["salt"]) if m["name"] != med["name"]]
                if alts:
                    cheaper = [a for a in alts if a["price"] < med["price"]]
                    if cheaper:
                        st.success("Cheaper alternatives with the same salt:")
                        for a in cheaper:
                            st.write(f"  - {a['name']} — Rs {a['price']} ({a['pack']})")
                st.write("---")
        else:
            st.warning("No match found in our sample database. Try a different spelling.")

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
