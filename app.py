
import streamlit as st
import pandas as pd
import random
import json
from pathlib import Path
from datetime import datetime

# -----------------------------
# إعداد الصفحة
# -----------------------------
st.set_page_config(
    page_title="مجلس التداول الذكي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# تنسيق الواجهة العربية
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="stApp"] {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    direction: rtl;
}

[data-testid="stAppViewContainer"] {
    direction: rtl;
}

h1, h2, h3, p, label {
    text-align: right;
}

div[data-testid="stMetric"] {
    direction: rtl;
    text-align: right;
    background: #171a21;
    border: 1px solid #303642;
    padding: 18px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    text-align: right;
}

div[data-testid="stMetricValue"] {
    direction: ltr;
    text-align: right;
    unicode-bidi: isolate;
    font-variant-numeric: tabular-nums;
}

div[data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
}

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
}

.agent-card {
    background: #171a21;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    overflow-wrap: anywhere;
}

.notice {
    background: #292419;
    border-right: 5px solid #e5ad42;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    line-height: 1.9;
}

.small-note {
    color: #aeb5c2;
    font-size: 0.9rem;
    line-height: 1.8;
}

div[data-testid="stDataFrame"] {
    direction: ltr;
}

@media (max-width: 640px) {
    h1 { font-size: 1.7rem !important; }
    h2 { font-size: 1.35rem !important; }
    div[data-testid="stMetric"] { padding: 12px; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# ملفات البيانات
# -----------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TRADES_FILE = DATA_DIR / "paper_trades.json"

COINS = {
    "BTC": {"name": "بيتكوين", "base": 65000.0},
    "ETH": {"name": "إيثيريوم", "base": 3200.0},
    "SOL": {"name": "سولانا", "base": 150.0},
    "BNB": {"name": "باينانس كوين", "base": 600.0},
    "XRP": {"name": "ريبل", "base": 0.60},
    "DOGE": {"name": "دوجكوين", "base": 0.15},
}

AGENTS = [
    ("📈", "المحلل الفني", "يفحص اتجاه السعر والزخم"),
    ("📊", "المحلل الكمي", "يقيّم الحركة والتذبذب"),
    ("🛡️", "مدير المخاطر", "يراجع المخاطرة وحجم الصفقة"),
    ("🔍", "المراجع المستقل", "يتحقق من توافق القرار"),
]

# -----------------------------
# إدارة الحالة
# -----------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 10000.0

if "trades" not in st.session_state:
    if TRADES_FILE.exists():
        try:
            st.session_state.trades = json.loads(
                TRADES_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            st.session_state.trades = []
    else:
        st.session_state.trades = []

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

if "prices" not in st.session_state:
    st.session_state.prices = {
        symbol: info["base"] for symbol, info in COINS.items()
    }

def save_trades():
    try:
        TRADES_FILE.write_text(
            json.dumps(st.session_state.trades, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        st.warning("تعذر حفظ سجل الصفقات في الملف.")

def fmt_money(value):
    return f"${value:,.2f}"

def fmt_price(value):
    return f"{value:,.4f}" if value < 10 else f"{value:,.2f}"

# -----------------------------
# عنوان التطبيق
# -----------------------------
st.title("🧠 مجلس التداول الذكي")
st.caption("محاكاة تداول تجريبية بأربعة وكلاء مستقلين")

st.markdown("""
<div class="notice">
<b>تنبيه مهم:</b>
هذه النسخة تجريبية، والأسعار المعروضة اصطناعية وليست أسعار سوق مباشرة.
لا يوجد اتصال بـ Phantom أو Hyperliquid، ولا تُرسل أوامر تداول حقيقية.
إجماع الوكلاء لا يضمن الربح ولا يجعل التوقع موثوقًا تلقائيًا.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# الشريط الجانبي
# -----------------------------
with st.sidebar:
    st.header("⚙️ الإعدادات")

    selected_coin = st.selectbox(
        "العملة",
        list(COINS.keys()),
        format_func=lambda x: f"{x} - {COINS[x]['name']}",
    )

    trade_style = st.selectbox(
        "نوع التحليل",
        ["يومي", "قصير الأجل"],
    )

    risk_percent = st.slider(
        "المخاطرة الافتراضية لكل صفقة (%)",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.5,
    )

    st.markdown("---")
    st.caption("وضع التنفيذ: محاكاة فقط")

# -----------------------------
# لوحة المؤشرات
# -----------------------------
open_trades = [
    trade for trade in st.session_state.trades
    if trade.get("status") == "مفتوحة"
]

closed_trades = [
    trade for trade in st.session_state.trades
    if trade.get("status") == "مغلقة"
]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("الرصيد التجريبي", fmt_money(st.session_state.balance))

with c2:
    st.metric("الصفقات المفتوحة", len(open_trades))

with c3:
    st.metric("الصفقات المغلقة", len(closed_trades))

st.markdown("---")

# -----------------------------
# عرض الوكلاء
# -----------------------------
st.header("🤖 فريق التحليل")

agent_columns = st.columns(2)

for i, agent in enumerate(AGENTS):
    icon, name, description = agent
    with agent_columns[i % 2]:
        st.markdown(
            f"""
            <div class="agent-card">
                <h3>{icon} {name}</h3>
                <p>{description}</p>
                <span>الحالة: جاهز للتحليل التجريبي</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# إنشاء بيانات اصطناعية
# -----------------------------
def generate_analysis(symbol):
    base = st.session_state.prices[symbol]

    # تغيّر اصطناعي لأغراض اختبار الواجهة فقط
    change = random.uniform(-0.025, 0.025)
    current = max(base * (1 + change), base * 0.5)
    st.session_state.prices[symbol] = current

    scores = [
        random.choice(["شراء", "بيع", "انتظار"]),
        random.choice(["شراء", "بيع", "انتظار"]),
        random.choice(["شراء", "بيع", "انتظار"]),
        random.choice(["شراء", "بيع", "انتظار"]),
    ]

    unanimous = len(set(scores)) == 1
    decision = scores[0] if unanimous else "انتظار"

    return {
        "symbol": symbol,
        "price": current,
        "change_pct": change * 100,
        "votes": scores,
        "decision": decision,
        "unanimous": unanimous,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# -----------------------------
# التحليل والإجماع
# -----------------------------
st.header("🔎 التحليل والإجماع")

st.write(
    f"العملة المختارة: **{selected_coin} - "
    f"{COINS[selected_coin]['name']}**"
)

if st.button("🔄 تحديث بيانات المحاكاة وتحليل العملة"):
    st.session_state.last_analysis = generate_analysis(selected_coin)

analysis = st.session_state.last_analysis

if analysis and analysis["symbol"] == selected_coin:
    p1, p2 = st.columns(2)

    with p1:
        st.metric(
            "السعر الاصطناعي",
            fmt_price(analysis["price"]),
            f"{analysis['change_pct']:+.2f}%",
        )

    with p2:
        st.metric(
            "قرار المجلس",
            analysis["decision"],
            "إجماع 4/4" if analysis["unanimous"] else "لا يوجد إجماع",
        )

    st.subheader("أصوات الوكلاء")

    for (icon, name, _), vote in zip(AGENTS, analysis["votes"]):
        st.write(f"{icon} **{name}:** {vote}")

    if analysis["unanimous"]:
        st.success(
            f"تحقق إجماع 4/4 على قرار: {analysis['decision']} "
            "ضمن بيانات المحاكاة فقط."
        )
    else:
        st.warning(
            "لم يتحقق إجماع 4/4. لن تُفتح صفقة تجريبية تلقائيًا."
        )

    st.caption(f"وقت التحليل: {analysis['time']}")

else:
    st.info("اضغط زر التحليل لإنشاء بيانات تجريبية جديدة.")

# -----------------------------
# فتح صفقة تجريبية يدويًا
# -----------------------------
st.markdown("---")
st.header("🧪 تنفيذ صفقة تجريبية")

st.caption(
    "فتح الصفقة هنا يدوي داخل المحاكاة فقط. "
    "لن يتم إرسال أي أمر إلى منصة تداول."
)

side = st.radio(
    "اتجاه الصفقة",
    ["شراء", "بيع"],
    horizontal=True,
)

position_size = st.number_input(
    "حجم الصفقة بالدولار",
    min_value=10.0,
    max_value=1000.0,
    value=100.0,
    step=10.0,
)

if st.button("فتح صفقة تجريبية"):
    if not analysis or analysis["symbol"] != selected_coin:
        st.error("نفّذ التحليل أولًا.")
    elif not analysis["unanimous"]:
        st.error("مرفوض: لا يوجد إجماع 4/4.")
    elif analysis["decision"] != side:
        st.error("اتجاه الصفقة لا يطابق قرار المجلس.")
    elif position_size > st.session_state.balance:
        st.error("الرصيد التجريبي لا يكفي.")
    else:
        price = analysis["price"]
        risk_amount = st.session_state.balance * risk_percent / 100
        stop_distance = max(price * 0.01, 0.000001)
        quantity = position_size / price

        trade = {
            "id": len(st.session_state.trades) + 1,
            "symbol": selected_coin,
            "side": side,
            "entry_price": price,
            "quantity": quantity,
            "position_usd": position_size,
            "risk_budget": risk_amount,
            "status": "مفتوحة",
            "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        st.session_state.trades.append(trade)
        st.session_state.balance -= position_size
        save_trades()
        st.success("تم فتح الصفقة التجريبية.")
        st.rerun()

# -----------------------------
# إغلاق الصفقة التجريبية
# -----------------------------
st.markdown("---")
st.header("📚 سجل الصفقات")

if open_trades:
    for trade in open_trades:
        with st.container(border=True):
            st.write(
                f"**#{trade['id']} | {trade['symbol']} | "
                f"{trade['side']}**"
            )
            st.write(f"سعر الدخول: {fmt_price(trade['entry_price'])}")
            st.write(f"حجم الصفقة: {fmt_money(trade['position_usd'])}")

            close_price = st.number_input(
                "سعر الإغلاق التجريبي",
                min_value=0.000001,
                value=float(st.session_state.prices[trade["symbol"]]),
                key=f"close_price_{trade['id']}",
                format="%.6f",
            )

            if st.button("إغلاق الصفقة", key=f"close_{trade['id']}"):
                if trade["side"] == "شراء":
                    pnl = (
                        close_price - trade["entry_price"]
                    ) * trade["quantity"]
                else:
                    pnl = (
                        trade["entry_price"] - close_price
                    ) * trade["quantity"]

                trade["status"] = "مغلقة"
                trade["exit_price"] = close_price
                trade["pnl"] = pnl
                trade["closed_at"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                st.session_state.balance += (
                    trade["position_usd"] + pnl
                )
                save_trades()
                st.rerun()
else:
    st.info("لا توجد صفقات مفتوحة.")

if st.session_state.trades:
    history = pd.DataFrame(st.session_state.trades)
    st.dataframe(history, use_container_width=True, hide_index=True)

    csv_data = history.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ تنزيل سجل الصفقات CSV",
        data=csv_data,
        file_name="paper_trades.csv",
        mime="text/csv",
    )

if st.button("إعادة ضبط المحاكاة"):
    st.session_state.balance = 10000.0
    st.session_state.trades = []
    st.session_state.last_analysis = None
    st.session_state.prices = {
        symbol: info["base"] for symbol, info in COINS.items()
    }

    if TRADES_FILE.exists():
        try:
            TRADES_FILE.unlink()
        except OSError:
            st.warning("تعذر حذف ملف سجل الصفقات.")

    st.rerun()

st.markdown("---")
st.markdown(
    '<p class="small-note">'
    'هذه أداة اختبار تعليمية وليست توصية استثمارية. '
    'بيانات السعر والقرارات عشوائية ولا تمثل السوق الحقيقي.'
    '</p>',
    unsafe_allow_html=True,
)
