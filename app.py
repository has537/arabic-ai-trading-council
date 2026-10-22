
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="stApp"] {
    font-family: 'Cairo', sans-serif;
}

h1, h2, h3, p, label,
[data-testid="stMarkdownContainer"] {
    font-family: 'Cairo', sans-serif;
    text-align: right;
}

[data-testid="stAppViewContainer"] {
    direction: ltr;
}

[data-testid="stMetric"] {
    background: #171a21;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 16px;
    min-width: 0;
}

[data-testid="stMetricLabel"] {
    direction: rtl;
    text-align: right;
}

[data-testid="stMetricValue"] {
    direction: ltr;
    text-align: right;
    unicode-bidi: isolate;
    overflow-wrap: anywhere;
}

.stButton button {
    width: 100%;
    min-height: 46px;
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
    white-space: normal;
}

.agent-card {
    direction: rtl;
    text-align: right;
    background: #171a21;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    overflow-wrap: anywhere;
}

.notice {
    direction: rtl;
    text-align: right;
    background: #292419;
    border-right: 5px solid #e5ad42;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    line-height: 2;
    overflow-wrap: anywhere;
}

[data-testid="stDataFrame"] {
    direction: ltr;
}

@media (max-width: 640px) {
    h1 { font-size: 1.7rem !important; }
    h2 { font-size: 1.35rem !important; }
    [data-testid="stMetric"] { padding: 10px; }
}
</style>
