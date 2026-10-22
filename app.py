
import json
import random
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="مجلس التداول الذكي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. تنسيق عربي آمن ومتجاوب
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="stApp"] {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    overflow-x: hidden;
}

.block-container {
    width: 100%;
    max-width: 1100px;
    padding: 1.5rem 1rem 3rem 1rem;
}

h1, h2, h3, p, label {
    font-family: 'Cairo', sans-serif !important;
}

h1, h2, h3 {
    text-align: right;
}

[data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
}

.arabic-text {
    direction: rtl;
    text-align: right;
    line-height: 1.9;
    overflow-wrap: anywhere;
}

.notice {
    direction: rtl;
    text-align: right;
    line-height: 1.9;
    overflow-wrap: anywhere;
    background: #292419;
    border-right: 5px solid #e5ad42;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0 20px 0;
}

.agent-card {
    direction: rtl;
    text-align: right;
    overflow-wrap: anywhere;
    background: #171a21;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    min-height: 125px;
}

.metric-card {
    background: #171a21;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    min-width: 0;
}

.metric-label {
    direction: rtl;
    text-align: right;
    color: #c4c9d4;
    font-size: 0.95rem;
}

.metric-value {
    direction: ltr;
    unicode-bidi: isolate;
    text-align: left;
    font-size: clamp(1.25rem, 4vw, 2rem);
    font-weight: 700;
    overflow-wrap: anywhere;
    font-variant-numeric: tabular-nums;
}

div.stButton > button {
    width: 100%;
    min-height: 45px;
    white-space: normal;
    font-family: 'Cairo', sans-serif !important;
    border-radius: 10px;
}

[data-testid="stMetric"] {
    min-width: 0;
}

[data-testid="stMetricLabel"] {
    text-align: right;
}

[data-testid="stMetricValue"] {
    direction: ltr;
    unicode-bidi: isolate;
    overflow-wrap: anywhere;
    font-variant-numeric: tabular-nums;
}

[data-testid="stDataFrame"] {
    direction: ltr;
}

@media (max-width: 640px) {
    .block-container {
        padding: 1rem 0.7rem 2rem 0.7rem;
    }

    h1 {
        font-size: 1.65rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
    }

    .agent-card, .metric-card {
        padding: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. الإعدادات والبيانات
# ==========================================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TRADES_FILE = DATA_DIR / "paper_trades.json"

STARTING_BALANCE = 10_000.0

COINS = {
    "BTC": {"name": "بيتكوين", "price": 65000.0},
    "ETH": {"name": "إيثيريوم", "price": 3200.0},
    "SOL": {"name": "سولانا", "price": 150.0},
    "BNB": {"name": "باينانس كوين", "price": 600.0},
    "XRP": {"name": "ريبل", "price": 0.60},
    "DOGE": {"name": "دوجكوين", "price": 0.15},
}

AGENTS = [
    {
        "name": "المحلل الفني",
        "icon": "📈",
        "description": "يراجع اتجاه السعر والزخم.",
    },
    {
        "name": "المحلل الكمي",
        "icon": "📊",
        "description": "يراجع التذبذب والتغيرات السعرية.",
    },
    {
        "name": "مدير المخاطر",
        "icon": "🛡️",
        "description": "يراجع حجم الصفقة والمخاطر.",
    },
    {
        "name": "المراجع المستقل",
        "icon": "🔍",
        "description": "يراجع القرار النهائي والإجماع.",
    },
]

# ==========================================
# 4. تهيئة حالة التطبيق
# ==========================================
if "balance" not in st.session_state:
    st.session_state.balance = STARTING_BALANCE

if "prices" not in st.session_state:
    st.session_state.prices = {
        symbol: details["price"]
        for symbol, details in COINS.items()
    }

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "trades" not in st.session_state:
    try:
        if TRADES_FILE.exists():
            st.session_state.trades = json.loads(
                TRADES_FILE.read_text(encoding="utf-8")
            )
        else:
            st.session_state.trades = []
    except (OSError, json.JSONDecodeError):
        st.session_state.trades = []

# ==========================================
# 5. دوال مساعدة
# ==========================================
def money(value):
    return f"${value:,.2f}"


def price_text(value):
    if value < 1:
        return f"${value:.5f}"
    return f"${value:,.2f}"


def save_trades():
    try:
        TRADES_FILE.write_text(
            json.dumps(
                st.session_state.trades,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        st.warning("تعذر حفظ الملف محليًا.")


def get_open_trades():
    return [
        trade for trade in st.session_state.trades
        if trade.get("status") == "مفتوحة"
    ]


def get_closed_trades():
    return [
        trade for trade in st.session_state.trades
        if trade.get("status") == "مغلقة"
    ]


def run_demo_analysis(symbol):
    """
    تحليل توضيحي باستخدام بيانات اصطناعية.
    لا يستخدم أسعار سوق مباشرة ولا يتنبأ بالسوق الحقيقي.
    """
    old_price = st.session_state.prices[symbol]

    market_change = random.uniform(-0.02, 0.02)
    new_price = max(old_price * (1 + market_change), 0.00001)

    st.session_state.prices[symbol] = new_price

    # إشارات مستقلة لأغراض اختبار الإجماع.
    # هذه الإشارات عشوائية وليست استراتيجية ربحية.
    votes = [
        random.choice(["شراء", "بيع", "انتظار"])
        for _ in AGENTS
    ]

    unanimous = len(set(votes)) == 1
    decision = votes[0] if unanimous else "انتظار"

    return {
        "symbol": symbol,
        "price": new_price,
        "change_pct": market_change * 100,
        "votes": votes,
        "decision": decision,
        "unanimous": unanimous,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ==========================================
# 6. عنوان الصفحة
# ==========================================
st.title("🧠 مجلس التداول الذكي")
st.markdown(
    '<div class="arabic-text">'
    'واجهة عربية لمحاكاة التداول وفحص إجماع أربعة وكلاء مستقلين.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="notice">
<b>تنبيه مهم:</b>
هذه نسخة تجريبية. الأسعار والقرارات اصطناعية وليست بيانات سوق مباشرة.
لا يوجد اتصال بمحفظة Phantom أو Hyperliquid، ولا تُرسل أوامر تداول حقيقية.
إجماع الوكلاء لا يضمن الربح ولا يُعد توقعًا موثوقًا للسوق.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. الإعدادات
# ==========================================
with st.sidebar:
    st.header("⚙️ الإعدادات")

    selected_coin = st.selectbox(
        "اختر العملة",
        list(COINS.keys()),
        format_func=lambda symbol: (
            f"{symbol} - {COINS[symbol]['name']}"
        ),
    )

    trade_style = st.selectbox(
        "أسلوب التداول",
        ["يومي", "قصير الأجل"],
    )

    risk_percent = st.slider(
        "نسبة المخاطرة النظرية (%)",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.5,
    )

    st.caption("وضع التشغيل: محاكاة فقط")

# ==========================================
# 8. لوحة المؤشرات
# ==========================================
open_trades = get_open_trades()
closed_trades = get_closed_trades()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "الرصيد التجريبي",
        money(st.session_state.balance),
    )

with col2:
    st.metric("الصفقات المفتوحة", len(open_trades))

with col3:
    st.metric("الصفقات المغلقة", len(closed_trades))

st.divider()

# ==========================================
# 9. عرض الوكلاء
# ==========================================
st.header("🤖 الوكلاء الأربعة")

agent_col1, agent_col2 = st.columns(2)

for index, agent in enumerate(AGENTS):
    target_col = agent_col1 if index % 2 == 0 else agent_col2

    with target_col:
        st.markdown(
            f"""
            <div class="agent-card">
                <h3>{agent["icon"]} {agent["name"]}</h3>
                <p>{agent["description"]}</p>
                <p>الحالة: جاهز للتحليل التجريبي</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 10. تحليل العملة
# ==========================================
st.divider()
st.header("🔎 تحليل العملة والإجماع")

st.write(
    f"العملة المختارة: **{selected_coin} - "
    f"{COINS[selected_coin]['name']}**"
)

if st.button("🔄 تحديث بيانات المحاكاة وتحليل العملة"):
    st.session_state.analysis = run_demo_analysis(selected_coin)

analysis = st.session_state.analysis

if analysis and analysis["symbol"] == selected_coin:
    price_col, decision_col = st.columns(2)

    with price_col:
        st.metric(
            "السعر الاصطناعي",
            price_text(analysis["price"]),
            f"{analysis['change_pct']:+.2f}%",
        )

    with decision_col:
        status_text = (
            "إجماع 4/4"
            if analysis["unanimous"]
            else "لا يوجد إجماع"
        )
        st.metric("قرار المجلس", analysis["decision"], status_text)

    st.subheader("نتائج الوكلاء")

    for agent, vote in zip(AGENTS, analysis["votes"]):
        st.markdown(
            f'<div class="agent-card">'
            f'<b>{agent["icon"]} {agent["name"]}</b>'
            f'<p>القرار: {vote}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if analysis["unanimous"]:
        st.success(
            f"تحقق إجماع 4/4 على قرار {analysis['decision']} "
            "ضمن المحاكاة فقط."
        )
    else:
        st.warning(
            "لم يتحقق إجماع 4/4. لن يُسمح بفتح صفقة تجريبية."
        )

    st.caption(f"وقت التحليل: {analysis['timestamp']}")

else:
    st.info("اضغط زر التحليل لإنشاء تحليل اصطناعي جديد.")

# ==========================================
# 11. فتح صفقة تجريبية
# ==========================================
st.divider()
st.header("🧪 فتح صفقة تجريبية")

st.caption(
    "هذا القسم للمحاكاة فقط. لا يوجد اتصال بمنصة تداول."
)

side = st.radio(
    "اتجاه الصفقة",
    ["شراء", "بيع"],
    horizontal=True,
)

position_size = st.number_input(
    "قيمة الصفقة بالدولار",
    min_value=10.0,
    max_value=1000.0,
    value=100.0,
    step=10.0,
)

if st.button("فتح صفقة تجريبية"):
    analysis = st.session_state.analysis

    if not analysis or analysis["symbol"] != selected_coin:
        st.error("حلّل العملة المختارة أولًا.")
    elif not analysis["unanimous"]:
        st.error("تم رفض الصفقة: لا يوجد إجماع 4/4.")
    elif analysis["decision"] != side:
        st.error("اتجاه الصفقة لا يطابق قرار المجلس.")
    elif position_size > st.session_state.balance:
        st.error("الرصيد التجريبي غير كافٍ.")
    else:
        entry_price = analysis["price"]
        quantity = position_size / entry_price
        risk_budget = st.session_state.balance * risk_percent / 100

        trade_id = (
            max(
                [t.get("id", 0) for t in st.session_state.trades],
                default=0,
            )
            + 1
        )

        trade = {
            "id": trade_id,
            "symbol": selected_coin,
            "side": side,
            "entry_price": entry_price,
            "quantity": quantity,
            "position_usd": position_size,
            "risk_budget": risk_budget,
            "status": "مفتوحة",
            "opened_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        st.session_state.trades.append(trade)
        st.session_state.balance -= position_size
        save_trades()

        st.success("تم فتح الصفقة التجريبية.")
        st.rerun()

# ==========================================
# 12. إدارة الصفقات المفتوحة
# ==========================================
st.divider()
st.header("📂 الصفقات المفتوحة")

open_trades = get_open_trades()

if not open_trades:
    st.info("لا توجد صفقات مفتوحة حاليًا.")

for trade in open_trades:
    with st.container(border=True):
        st.subheader(
            f"#{trade['id']} | {trade['symbol']} | {trade['side']}"
        )

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.write(f"سعر الدخول: {price_text(trade['entry_price'])}")

        with info_col2:
            st.write(f"حجم الصفقة: {money(trade['position_usd'])}")

        close_price = st.number_input(
            "سعر الإغلاق التجريبي",
            min_value=0.000001,
            value=float(st.session_state.prices[trade["symbol"]]),
            format="%.6f",
            key=f"close_price_{trade['id']}",
        )

        if st.button("إغلاق الصفقة", key=f"close_trade_{trade['id']}"):
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

            # إعادة رأس المال المحجوز مع الربح أو الخسارة.
            st.session_state.balance += trade["position_usd"] + pnl

            save_trades()
            st.success(f"تم إغلاق الصفقة. النتيجة: {money(pnl)}")
            st.rerun()

# ==========================================
# 13. سجل الصفقات
# ==========================================
st.divider()
st.header("📚 سجل الصفقات")

if st.session_state.trades:
    history = pd.DataFrame(st.session_state.trades)

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = history.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ تنزيل سجل الصفقات CSV",
        data=csv_bytes,
        file_name="paper_trades.csv",
        mime="text/csv",
    )
else:
    st.info("لم تُسجّل أي صفقات حتى الآن.")

# ==========================================
# 14. إعادة ضبط المحاكاة
# ==========================================
st.divider()
st.header("🔧 إدارة المحاكاة")

if st.button("إعادة ضبط الرصيد والصفقات"):
    st.session_state.balance = STARTING_BALANCE
    st.session_state.trades = []
    st.session_state.analysis = None
    st.session_state.prices = {
        symbol: details["price"]
        for symbol, details in COINS.items()
    }

    try:
        if TRADES_FILE.exists():
            TRADES_FILE.unlink()
    except OSError:
        st.warning("تعذر حذف ملف السجل المحلي.")

    st.rerun()

st.markdown("""
<div class="notice">
<b>ملاحظة:</b>
هذه النسخة لا تجلب أسعارًا حقيقية، ولا تنفّذ تداولًا آليًا.
الأصوات عشوائية لاختبار شرط الإجماع، وليست تحليلًا ماليًا فعليًا.
قد تُفقد البيانات المحفوظة محليًا عند إعادة تشغيل بعض بيئات الاستضافة.
</div>
""", unsafe_allow_html=True)
