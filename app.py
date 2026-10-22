import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import random
import json
from pathlib import Path

st.set_page_config(page_title="مجلس التداول الذكي", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# RTL Arabic interface styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, [class*="css"], .stApp { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }
[data-testid="stSidebar"] { direction: rtl; text-align: right; }
div[data-testid="stMetric"] { direction: rtl; text-align: right; background: rgba(120,120,120,.07); padding: 14px; border-radius: 14px; }
div[data-testid="stMetric"] label { text-align: right !important; }
.block-container { padding-top: 1.4rem; }
.agent-card { border: 1px solid rgba(128,128,128,.3); border-radius: 16px; padding: 16px; min-height: 145px; background: rgba(128,128,128,.04); }
.status { display:inline-block; padding:4px 10px; border-radius:999px; background:#e6f4ea; color:#176b36; font-weight:700; }
.warning { border-right: 4px solid #d99a20; padding: 12px 16px; background: rgba(217,154,32,.10); border-radius: 8px; }
.small { color: #777; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

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

def load_trades():
    if TRADES_FILE.exists():
        try:
            return json.loads(TRADES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_trades(trades):
    TRADES_FILE.write_text(json.dumps(trades, ensure_ascii=False, indent=2), encoding="utf-8")

def market_snapshot():
    rng = np.random.default_rng(int(datetime.now().timestamp() // 60))
    rows = []
    for sym, info in COINS.items():
        change = float(rng.normal(0, 1.6))
        price = info["base"] * (1 + change / 100)
        vol = float(rng.uniform(0.2, 2.8))
        trend = "صاعد" if change > .35 else ("هابط" if change < -.35 else "عرضي")
        rows.append({"الرمز": sym, "العملة": info["name"], "السعر التجريبي": price, "التغير %": change, "التذبذب": vol, "الاتجاه": trend})
    return pd.DataFrame(rows)

def agent_vote(name, symbol, change, volatility, mode):
    # Transparent demo heuristics, not a predictive AI model.
    if name == "المحلل الفني":
        vote = "شراء" if change > .45 else ("بيع" if change < -.45 else "انتظار")
        reason = "يعتمد على اتجاه التغير السعري اللحظي التجريبي."
    elif name == "المحلل الكمي":
        vote = "شراء" if change > .9 else ("بيع" if change < -.9 else "انتظار")
        reason = "يقارن حركة السعر بحدود كمية بسيطة."
    elif name == "مسؤول المخاطر":
        vote = "انتظار" if volatility > 2.2 else ("شراء" if change > .7 else ("بيع" if change < -.7 else "انتظار"))
        reason = "يرفض الإشارة عند ارتفاع التذبذب التجريبي."
    else:
        vote = "شراء" if change > 1.1 else ("بيع" if change < -1.1 else "انتظار")
        reason = "يراجع الإشارة ويطلب حركة أوضح قبل التصويت."
    return {"الوكيل": name, "التصويت": vote, "التفسير": reason}

def council_decision(row, threshold=4):
    names = ["المحلل الفني", "المحلل الكمي", "مسؤول المخاطر", "المراجع المستقل"]
    votes = [agent_vote(n, row["الرمز"], row["التغير %"], row["التذبذب"], "يومي") for n in names]
    action = votes[0]["التصويت"]
    unanimous = action in ("شراء", "بيع") and all(v["التصويت"] == action for v in votes)
    return votes, (action if unanimous else "انتظار"), unanimous

st.title("🧠 مجلس التداول الذكي")
st.caption("منصة عربية تجريبية لإدارة أربعة وكلاء مستقلين وإجماع 4 من 4. لا تنفذ أي صفقة حقيقية.")
st.markdown('<div class="warning"><b>تنبيه مهم:</b> هذه نسخة محاكاة تستخدم أسعارًا اصطناعية، وليست متصلة بـ Phantom أو Hyperliquid ولا تقدم تنبؤات مالية موثوقة. لا تدخل العبارة السرية أو المفتاح الخاص في أي مكان.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ إعدادات المحاكاة")
    st.write("كل الإعدادات هنا للتداول الورقي فقط.")
    balance = st.number_input("الرصيد الافتراضي (USDC)", min_value=100.0, max_value=1000000.0, value=10000.0, step=500.0)
    risk_pct = st.slider("المخاطرة الافتراضية لكل صفقة (%)", 0.1, 2.0, 0.5, 0.1)
    leverage = st.selectbox("الرافعة التجريبية", [1, 2, 3, 5], index=0)
    consensus = st.select_slider("الإجماع المطلوب", options=[2, 3, 4], value=4)
    st.info("موصى به: إبقاء الإجماع عند 4/4 والرافعة عند 1x أثناء الاختبار.")
    if st.button("🧹 مسح سجل الصفقات التجريبية", use_container_width=True):
        save_trades([])
        st.success("تم مسح سجل المحاكاة.")

if "paper_balance" not in st.session_state:
    st.session_state.paper_balance = balance
if "market" not in st.session_state:
    st.session_state.market = market_snapshot()
if "last_run" not in st.session_state:
    st.session_state.last_run = None

# Refresh market snapshot button
top1, top2, top3 = st.columns([1,1,2])
with top1:
    if st.button("🔄 تحديث بيانات المحاكاة", use_container_width=True):
        st.session_state.market = market_snapshot()
        st.session_state.last_run = None
with top2:
    if st.button("↺ إعادة ضبط الرصيد", use_container_width=True):
        st.session_state.paper_balance = balance
with top3:
    st.markdown(f"<div style='text-align:left;color:#888;padding-top:8px'>آخر عرض: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

market = st.session_state.market.copy()
trades = load_trades()
open_trades = [t for t in trades if t.get("الحالة") == "مفتوحة"]
closed_trades = [t for t in trades if t.get("الحالة") == "مغلقة"]
wins = sum(1 for t in closed_trades if t.get("النتيجة USDC", 0) > 0)
win_rate = (wins / len(closed_trades) * 100) if closed_trades else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("الرصيد الافتراضي", f"{st.session_state.paper_balance:,.2f} USDC")
m2.metric("الصفقات المفتوحة", str(len(open_trades)))
m3.metric("الصفقات المغلقة", str(len(closed_trades)))
m4.metric("نسبة الفوز التجريبية", f"{win_rate:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة السوق", "🧠 مجلس الوكلاء", "📒 سجل التداول", "🔌 الربط والأمان"])

with tab1:
    st.subheader("أسعار السوق التجريبية")
    st.caption("تتغير القيم عند تحديث المحاكاة. الأرقام ليست أسعارًا حية.")
    show = market.copy()
    show["السعر التجريبي"] = show["السعر التجريبي"].map(lambda x: f"{x:,.4f}")
    show["التغير %"] = show["التغير %"].map(lambda x: f"{x:+.2f}%")
    show["التذبذب"] = show["التذبذب"].map(lambda x: f"{x:.2f}")
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.subheader("تشغيل جولة تحليل")
    chosen = st.selectbox("اختر عملة للتحليل", list(COINS.keys()), format_func=lambda s: f"{s} · {COINS[s]['name']}")
    if st.button("تشغيل الوكلاء الأربعة", type="primary", use_container_width=True):
        row = market[market["الرمز"] == chosen].iloc[0]
        votes, decision, unanimous = council_decision(row, consensus)
        st.session_state.last_run = {"symbol": chosen, "votes": votes, "decision": decision, "unanimous": unanimous, "price": float(row["السعر التجريبي"]), "change": float(row["التغير %"]), "volatility": float(row["التذبذب"])}
    if st.session_state.last_run:
        run = st.session_state.last_run
        st.markdown(f"### نتيجة المجلس: **{run['symbol']}**")
        if run["unanimous"]:
            st.success(f"إجماع كامل 4/4: {run['decision']} (قرار محاكاة فقط)")
        else:
            st.warning("لا يوجد إجماع كامل 4/4، لذلك القرار النهائي: انتظار. لا تُفتح صفقة.")
        st.write(f"السعر الافتراضي: {run['price']:,.4f} · التغير: {run['change']:+.2f}% · التذبذب: {run['volatility']:.2f}")
        st.dataframe(pd.DataFrame(run["votes"]), use_container_width=True, hide_index=True)
        if run["unanimous"]:
            if st.button("فتح صفقة ورقية وفق الإجماع", type="primary"):
                risk_amount = st.session_state.paper_balance * (risk_pct / 100)
                notional = risk_amount * leverage
                trade = {
                    "المعرف": f"P-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "الوقت": datetime.now().isoformat(timespec="seconds"),
                    "العملة": run["symbol"],
                    "الاتجاه": run["decision"],
                    "سعر الدخول": run["price"],
                    "حجم الصفقة USDC": notional,
                    "المخاطرة USDC": risk_amount,
                    "الرافعة": leverage,
                    "الحالة": "مفتوحة",
                    "النتيجة USDC": 0.0
                }
                trades.append(trade)
                save_trades(trades)
                st.success("تم إنشاء صفقة ورقية محلية. لا يوجد تنفيذ على Phantom أو منصة تداول.")
                st.rerun()

with tab2:
    st.subheader("الوكلاء المستقلون")
    agents = [
        ("📈", "المحلل الفني", "يراقب اتجاه الحركة السعرية والإشارات الفنية المبسطة."),
        ("🧮", "المحلل الكمي", "يطبق قواعد رقمية واضحة على التغير والتذبذب."),
        ("🛡️", "مسؤول المخاطر", "يمكنه رفض الإشارة إذا ارتفع التذبذب."),
        ("🔎", "المراجع المستقل", "يتحقق من وضوح الإشارة قبل التصويت النهائي."),
    ]
    cols = st.columns(2)
    for i, (emoji, name, desc) in enumerate(agents):
        with cols[i % 2]:
            st.markdown(f'<div class="agent-card"><h3>{emoji} {name}</h3><p>{desc}</p><p><b>القاعدة:</b> لا يمكن لأي وكيل بمفرده فتح صفقة.</p></div>', unsafe_allow_html=True)
    st.markdown("### قاعدة الإجماع")
    st.write("الافتراضي هو 4 أصوات متطابقة من أصل 4. إذا اختلف وكيل واحد أو صوّت أي وكيل «انتظار»، لا تُفتح صفقة.")
    st.code("فتح صفقة = (الأصوات الأربعة متطابقة) AND (القرار شراء أو بيع) AND (اجتياز حدود المخاطر)", language="text")

with tab3:
    st.subheader("سجل التداول الورقي")
    trades = load_trades()
    if not trades:
        st.info("لا توجد صفقات مسجلة بعد. شغّل تحليلًا أولًا، ثم افتح صفقة ورقية عند تحقق الإجماع.")
    else:
        st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
        open_ids = [t["المعرف"] for t in trades if t.get("الحالة") == "مفتوحة"]
        if open_ids:
            selected_trade = st.selectbox("اختر صفقة لإغلاقها في المحاكاة", open_ids)
            if st.button("إغلاق الصفقة الورقية بنتيجة عشوائية تجريبية"):
                for t in trades:
                    if t["المعرف"] == selected_trade and t.get("الحالة") == "مفتوحة":
                        move = random.uniform(-1.5, 1.5) / 100
                        pnl = t["حجم الصفقة USDC"] * move * (1 if t["الاتجاه"] == "شراء" else -1)
                        t["النتيجة USDC"] = round(pnl, 2)
                        t["الحالة"] = "مغلقة"
                        t["سعر الخروج"] = round(t["سعر الدخول"] * (1 + move), 6)
                        st.session_state.paper_balance += pnl
                save_trades(trades)
                st.success("أُغلقت الصفقة بنتيجة اصطناعية لأغراض العرض فقط.")
                st.rerun()

with tab4:
    st.subheader("حالة الربط")
    st.markdown("""
**حالة النسخة الحالية:** مستقلة ومحلية، ولا تتصل بمحفظة Phantom أو Hyperliquid.

- **Phantom:** محفظة وتطبيق تداول؛ واجهة Phantom وحدها لا تعني وجود API آمن لتشغيل هذا البرنامج آليًا.
- **العقود الدائمة (Perps):** قد تتوفر عبر Phantom/Hyperliquid حسب البلد والحساب. التداول بالرافعة قد يؤدي إلى تصفية المركز وخسارة الرصيد.
- **المرحلة التالية:** يمكن إضافة مصدر بيانات سوق موثوق أولًا، ثم بيئة اختبار API منفصلة إن كانت متاحة. لا تنتقل للتداول الحقيقي قبل اختبار طويل ومراجعة مستقلة.
- **الأسرار:** لا تضع عبارة الاسترداد أو المفتاح الخاص في ملف الإعدادات أو المحادثات. لا يحتاج هذا المشروع أيًّا منها.
""")
    st.markdown("[موقع Phantom الرسمي](https://phantom.com) · [وثائق المطورين](https://docs.phantom.com) · [Hyperliquid](https://hyperliquid.xyz)")
    st.subheader("حدود النسخة")
    st.write("هذه واجهة أولية تعليمية. لا تستخدم نموذج ذكاء اصطناعي مدرّبًا ولا بيانات سوق مباشرة ولا تنفّذ أوامر حقيقية. التصويت قائم على قواعد توضيحية بسيطة، والنتائج التجريبية لا تتنبأ بالربح.")

st.divider()
st.caption("مجلس التداول الذكي · نسخة عربية تجريبية · لا يقدم نصيحة استثمارية ولا ينفذ تداولًا حقيقيًا.")
