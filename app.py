
import streamlit as st
import pandas as pd
import numpy as np
import json
import uuid
from pathlib import Path
from datetime import datetime

# =========================================================
# إعدادات التطبيق
# =========================================================
st.set_page_config(
    page_title="مجلس التداول الذكي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TRADES_FILE = DATA_DIR / "paper_trades.json"

COINS = {
    "BTC": {"name": "بيتكوين", "base": 67200.0},
    "ETH": {"name": "إيثيريوم", "base": 3520.0},
    "SOL": {"name": "سولانا", "base": 168.0},
    "BNB": {"name": "باينانس كوين", "base": 590.0},
    "XRP": {"name": "ريبل", "base": 0.61},
    "DOGE": {"name": "دوجكوين", "base": 0.16},
}

AGENTS = [
    "المحلل الفني",
    "المحلل الكمي",
    "مسؤول المخاطر",
    "المراجع المستقل",
]

# =========================================================
# تنسيق الواجهة العربية
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        direction: rtl;
    }

    [data-testid="stAppViewContainer"] {
        direction: rtl;
    }

    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        text-align: right;
    }

    [data-testid="stMetric"] {
        direction: rtl;
        text-align: right;
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.15);
        padding: 14px;
        border-radius: 14px;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 0.8rem;
    }

    .notice {
        padding: 14px;
        border-right: 5px solid #d99a20;
        border-radius: 10px;
        background: rgba(217,154,32,0.12);
        line-height: 1.9;
        overflow-wrap: anywhere;
    }

    .agent-card {
        padding: 16px;
        margin-bottom: 10px;
        border: 1px solid rgba(128,128,128,0.3);
        border-radius: 14px;
        min-height: 120px;
        overflow-wrap: anywhere;
    }

    h1, h2, h3, p {
        overflow-wrap: anywhere;
    }

    @media (max-width: 640px) {
        [data-testid="stAppViewContainer"] .main .block-container {
            padding: 1rem 0.8rem 2rem 0.8rem;
        }

        h1 {
            font-size: 1.7rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        [data-testid="stMetric"] {
            padding: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# حفظ سجل الصفقات وقراءته
# =========================================================
def load_trades():
    if not TRADES_FILE.exists():
        return []

    try:
        data = json.loads(TRADES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_trades(trades):
    temporary_file = TRADES_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(trades, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(TRADES_FILE)


# =========================================================
# بيانات سوق اصطناعية للتجربة فقط
# =========================================================
def market_snapshot():
    rng = np.random.default_rng()

    rows = []
    for symbol, info in COINS.items():
        change = float(rng.normal(0, 1.0))
        volatility = float(rng.uniform(0.2, 2.8))
        price = info["base"] * (1 + change / 100)

        if change > 0.35:
            trend = "صاعد"
        elif change < -0.35:
            trend = "هابط"
        else:
            trend = "عرضي"

        rows.append({
            "الرمز": symbol,
            "العملة": info["name"],
            "السعر التجريبي": round(price, 6),
            "التغير %": round(change, 3),
            "التذبذب": round(volatility, 3),
            "الاتجاه": trend,
        })

    return pd.DataFrame(rows)


# =========================================================
# تصويت الوكلاء
# هذه قواعد توضيحية وليست نموذج ذكاء اصطناعي تنبؤي
# =========================================================
def agent_vote(name, change, volatility):
    if name == "المحلل الفني":
        if change > 0.8:
            vote = "شراء"
        elif change < -0.8:
            vote = "بيع"
        else:
            vote = "انتظار"
        reason = "يفحص اتجاه التغير السعري."

    elif name == "المحلل الكمي":
        if change > 1.2:
            vote = "شراء"
        elif change < -1.2:
            vote = "بيع"
        else:
            vote = "انتظار"
        reason = "يطبق حدودًا رقمية بسيطة."

    elif name == "مسؤول المخاطر":
        if volatility > 2.2:
            vote = "انتظار"
        elif change > 1.0:
            vote = "شراء"
        elif change < -1.0:
            vote = "بيع"
        else:
            vote = "انتظار"
        reason = "يرفض الإشارة عند ارتفاع التذبذب."

    else:
        if change > 1.5:
            vote = "شراء"
        elif change < -1.5:
            vote = "بيع"
        else:
            vote = "انتظار"
        reason = "يطلب حركة سعرية أوضح."

    return {
        "الوكيل": name,
        "التصويت": vote,
        "التفسير": reason,
    }


def council_decision(row):
    votes = [
        agent_vote(
            name,
            float(row["التغير %"]),
            float(row["التذبذب"]),
        )
        for name in AGENTS
    ]

    directions = [vote["التصويت"] for vote in votes]

    unanimous = (
        len(directions) == 4
        and directions[0] in ("شراء", "بيع")
        and all(direction == directions[0] for direction in directions)
    )

    decision = directions[0] if unanimous else "انتظار"
    return votes, decision, unanimous


# =========================================================
# عنوان الصفحة والتحذير
# =========================================================
st.title("🧠 مجلس التداول الذكي")
st.caption(
    "واجهة عربية تجريبية لأربعة وكلاء، "
    "مع اشتراط الإجماع الكامل قبل فتح أي صفقة ورقية."
)

st.markdown(
    """
    <div class="notice">
    <b>تنبيه:</b>
    الأسعار في هذه النسخة اصطناعية وليست أسعار سوق حية.
    التطبيق لا يتصل بـ Phantom أو Hyperliquid،
    ولا يرسل أوامر تداول حقيقية.
    لا تدخل عبارة استرداد المحفظة أو مفتاحها الخاص.
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# إعدادات المحاكاة
# =========================================================
with st.sidebar:
    st.header("⚙️ إعدادات المحاكاة")

    initial_balance = st.number_input(
        "الرصيد الافتراضي USDC",
        min_value=100.0,
        max_value=1_000_000.0,
        value=10_000.0,
        step=500.0,
    )

    risk_pct = st.slider(
        "المخاطرة الافتراضية (%)",
        min_value=0.1,
        max_value=2.0,
        value=0.5,
        step=0.1,
    )

    leverage = st.selectbox(
        "الرافعة التجريبية",
        [1, 2, 3, 5],
        index=0,
    )

    st.info(
        "الإجماع ثابت عند 4/4. "
        "هذه الإعدادات لا تتصل بأي منصة تداول."
    )

    if st.button("🧹 مسح سجل الصفقات", use_container_width=True):
        save_trades([])
        st.session_state.confirmed_balance = float(initial_balance)
        st.success("تم مسح سجل الصفقات.")
        st.rerun()

if "paper_balance" not in st.session_state:
    st.session_state.paper_balance = float(initial_balance)

if "confirmed_balance" not in st.session_state:
    st.session_state.confirmed_balance = float(initial_balance)

if "market" not in st.session_state:
    st.session_state.market = market_snapshot()

if "last_run" not in st.session_state:
    st.session_state.last_run = None

# =========================================================
# أزرار التحكم
# =========================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 تحديث بيانات المحاكاة", use_container_width=True):
        st.session_state.market = market_snapshot()
        st.session_state.last_run = None
        st.rerun()

with col2:
    if st.button("↺ إعادة ضبط الرصيد", use_container_width=True):
        st.session_state.paper_balance = float(initial_balance)
        st.session_state.confirmed_balance = float(initial_balance)
        st.rerun()

market = st.session_state.market.copy()
trades = load_trades()

open_trades = [t for t in trades if t.get("الحالة") == "مفتوحة"]
closed_trades = [t for t in trades if t.get("الحالة") == "مغلقة"]

wins = sum(
    1 for trade in closed_trades
    if float(trade.get("النتيجة USDC", 0)) > 0
)

win_rate = (
    wins / len(closed_trades) * 100
    if closed_trades else 0.0
)

# =========================================================
# مؤشرات المحاكاة
# =========================================================
m1, m2, m3 = st.columns(3)

m1.metric(
    "الرصيد الافتراضي",
    f"{st.session_state.paper_balance:,.2f} USDC",
)

m2.metric("الصفقات المفتوحة", len(open_trades))
m3.metric("الصفقات المغلقة", len(closed_trades))

st.metric("نسبة الفوز للصفقات المغلقة", f"{win_rate:.1f}%")

# =========================================================
# أقسام التطبيق
# =========================================================
tab_market, tab_agents, tab_trades, tab_security = st.tabs([
    "📊 السوق",
    "🧠 الوكلاء",
    "📒 سجل الصفقات",
    "🔐 الربط والأمان",
])

# =========================================================
# قسم السوق والتحليل
# =========================================================
with tab_market:
    st.subheader("أسعار السوق التجريبية")
    st.caption("هذه الأسعار مولدة محليًا ولا تمثل أسعار السوق الفعلية.")

    st.dataframe(
        market,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("تشغيل جولة تحليل")

    chosen = st.selectbox(
        "اختر العملة",
        list(COINS.keys()),
        format_func=lambda symbol: (
            f"{symbol} · {COINS[symbol]['name']}"
        ),
    )

    if st.button(
        "🧠 تشغيل الوكلاء الأربعة",
        type="primary",
        use_container_width=True,
    ):
        row = market.loc[market["الرمز"] == chosen].iloc[0]
        votes, decision, unanimous = council_decision(row)

        st.session_state.last_run = {
            "symbol": chosen,
            "price": float(row["السعر التجريبي"]),
            "change": float(row["التغير %"]),
            "volatility": float(row["التذبذب"]),
            "votes": votes,
            "decision": decision,
            "unanimous": unanimous,
        }

    run = st.session_state.last_run

    if run:
        st.markdown(f"### نتيجة التحليل: {run['symbol']}")

        if run["unanimous"]:
            st.success(
                f"إجماع كامل 4/4 على {run['decision']} "
                "ضمن المحاكاة فقط."
            )
        else:
            st.warning(
                "لا يوجد إجماع كامل 4/4. "
                "القرار النهائي هو انتظار ولا تُفتح صفقة."
            )

        st.write(f"السعر التجريبي: {run['price']:,.6f}")
        st.write(f"التغير: {run['change']:+.3f}%")
        st.write(f"التذبذب: {run['volatility']:.3f}")

        st.dataframe(
            pd.DataFrame(run["votes"]),
            use_container_width=True,
            hide_index=True,
        )

        if run["unanimous"]:
            st.warning(
                "فتح الصفقة هنا ينشئ سجلًا ورقيًا فقط. "
                "لا يتم إرسال أي أمر إلى منصة."
            )

            if st.button(
                "📝 فتح صفقة ورقية",
                type="primary",
                use_container_width=True,
            ):
                trades = load_trades()

                # فحص الإجماع مرة أخرى قبل إنشاء الصفقة
                directions = [
                    item["التصويت"] for item in run["votes"]
                ]

                valid_consensus = (
                    len(directions) == 4
                    and directions[0] in ("شراء", "بيع")
                    and all(
                        direction == directions[0]
                        for direction in directions
                    )
                )

                if not valid_consensus:
                    st.error("فشل فحص الإجماع. لم تُفتح صفقة.")
                    st.stop()

                risk_amount = (
                    st.session_state.paper_balance
                    * risk_pct / 100
                )

                # قيمة اسمية توضيحية، وليست قياسًا دقيقًا
                # للمخاطرة الفعلية للعقود الدائمة
                notional = risk_amount * leverage

                if risk_amount <= 0 or notional <= 0:
                    st.error("لا يمكن إنشاء صفقة بحجم غير صالح.")
                    st.stop()

                trade = {
                    "المعرف": str(uuid.uuid4())[:8],
                    "الوقت": datetime.now().astimezone().isoformat(
                        timespec="seconds"
                    ),
                    "العملة": run["symbol"],
                    "الاتجاه": run["decision"],
                    "سعر الدخول": run["price"],
                    "حجم الصفقة USDC": round(notional, 2),
                    "المخاطرة التقديرية USDC": round(
                        risk_amount, 2
                    ),
                    "الرافعة": leverage,
                    "الحالة": "مفتوحة",
                    "النتيجة USDC": 0.0,
                    "نوع البيانات": "اصطناعية",
                }

                trades.append(trade)
                save_trades(trades)

                st.success(
                    "تم إنشاء صفقة ورقية محلية فقط."
                )
                st.rerun()

# =========================================================
# قسم الوكلاء
# =========================================================
with tab_agents:
    st.subheader("الوكلاء الأربعة")

    descriptions = [
        (
            "📈 المحلل الفني",
            "يفحص التغير السعري ويطبق قواعد اتجاه بسيطة.",
        ),
        (
            "🧮 المحلل الكمي",
            "يستخدم حدودًا رقمية محددة مسبقًا.",
        ),
        (
            "🛡️ مسؤول المخاطر",
            "يصوّت انتظار عند ارتفاع التذبذب.",
        ),
        (
            "🔎 المراجع المستقل",
            "يتطلب حركة أوضح قبل تأييد الاتجاه.",
        ),
    ]

    for title, description in descriptions:
        st.markdown(
            f"""
            <div class="agent-card">
                <h3>{title}</h3>
                <p>{description}</p>
                <p><b>الصلاحية:</b> التصويت فقط، وليس فتح الصفقة منفردًا.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("قاعدة الإجماع")
    st.code(
        "فتح صفقة ورقية = إجماع 4/4 على شراء أو بيع",
        language="text",
    )
    st.write(
        "إذا صوّت أي وكيل انتظار أو خالف اتجاه الآخرين، "
        "يكون القرار النهائي انتظارًا."
    )

# =========================================================
# سجل الصفقات الورقية
# =========================================================
with tab_trades:
    st.subheader("سجل التداول الورقي")

    trades = load_trades()

    if not trades:
        st.info("لا توجد صفقات في السجل.")
    else:
        st.dataframe(
            pd.DataFrame(trades),
            use_container_width=True,
            hide_index=True,
        )

        open_ids = [
            trade["المعرف"]
            for trade in trades
            if trade.get("الحالة") == "مفتوحة"
        ]

        if open_ids:
            st.info(
                "إغلاق الصفقة لا يحسب ربحًا أو خسارة تلقائيًا، "
                "لأن هذه النسخة لا تستقبل أسعار خروج حقيقية."
            )

            selected_id = st.selectbox(
                "اختر صفقة لإغلاقها في السجل",
                open_ids,
            )

            exit_price = st.number_input(
                "سعر الخروج التجريبي",
                min_value=0.000001,
                value=1.0,
                format="%.6f",
                help="أدخل سعرًا افتراضيًا يدويًا. لا يُجلب من السوق.",
            )

            if st.button(
                "إغلاق الصفقة بالسعر المدخل",
                use_container_width=True,
            ):
                updated = False

                for trade in trades:
                    if (
                        trade.get("المعرف") == selected_id
                        and trade.get("الحالة") == "مفتوحة"
                    ):
                        entry = float(trade["سعر الدخول"])
                        direction = trade["الاتجاه"]
                        notional = float(
                            trade["حجم الصفقة USDC"]
                        )

                        if entry <= 0 or exit_price <= 0:
                            st.error("السعر يجب أن يكون أكبر من صفر.")
                            st.stop()

                        if direction == "شراء":
                            move = (exit_price - entry) / entry
                        else:
                            move = (entry - exit_price) / entry

                        pnl = notional * move

                        trade["سعر الخروج"] = float(exit_price)
                        trade["النتيجة USDC"] = round(pnl, 2)
                        trade["الحالة"] = "مغلقة"
                        trade["نوع النتيجة"] = (
                            "محسوبة من أسعار مدخلة يدويًا"
                        )

                        st.session_state.paper_balance += pnl
                        updated = True
                        break

                if updated:
                    save_trades(trades)
                    st.success(
                        "أُغلقت الصفقة في السجل الورقي. "
                        "النتيجة ليست نتيجة تداول حقيقي."
                    )
                    st.rerun()

# =========================================================
# قسم الربط والأمان
# =========================================================
with tab_security:
    st.subheader("حالة الربط")

    st.write("حالة النظام: محاكاة محلية فقط.")
    st.write("الاتصال بـ Phantom: غير مفعّل.")
    st.write("الاتصال بـ Hyperliquid: غير مفعّل.")
    st.write("بيانات السوق المباشرة: غير مفعّلة.")
    st.write("التنفيذ الحقيقي: غير مفعّل.")

    st.warning(
        "لا تدخل العبارة السرية أو المفتاح الخاص للمحفظة "
        "في هذا التطبيق أو في مستودع GitHub."
    )

    st.markdown(
        "[موقع Phantom الرسمي](https://phantom.com)"
        " · "
        "[وثائق المطورين](https://docs.phantom.com)"
        " · "
        "[Hyperliquid](https://hyperliquid.xyz)"
    )

    st.subheader("حدود النسخة")
    st.write(
        "الوكلاء الأربعة يستخدمون قواعد توضيحية، "
        "ولا يمثلون أربعة نماذج ذكاء اصطناعي مستقلة. "
        "الأسعار اصطناعية، ونتائج الاختبار لا تتنبأ بالأرباح. "
        "حجم الصفقة المعروض تقديري ولا يضمن حصر الخسارة."
    )

st.divider()
st.caption(
    "مجلس التداول الذكي | نسخة تجريبية عربية | "
    "لا ينفذ تداولًا حقيقيًا ولا يقدم ضمانًا للربح."
)
