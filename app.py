import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import datetime

warnings.filterwarnings('ignore')

# ==========================================
# 💎 1. إعدادات الهوية الاحترافية
# ==========================================
st.set_page_config(page_title="منصة ماسة 💎 | Masa Quant", layout="wide", page_icon="💎")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
div[data-testid="metric-container"] { background-color: #1a1c24; border: 1px solid #2d303e; padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); transition: all 0.3s ease; }
div[data-testid="metric-container"]:hover { transform: translateY(-5px); border-color: #00d2ff; box-shadow: 0 6px 12px rgba(0, 210, 255, 0.2); }
.stTabs [data-baseweb="tab-list"] { gap: 15px; }
.stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; padding-top: 10px; padding-bottom: 10px; font-size: 16px; font-weight: 600; color: #888; }
.stTabs [aria-selected="true"] { color: #00d2ff !important; border-bottom: 2px solid #00d2ff; }
/* تصميم عناوين التقارير الجانبية */
.scanner-header { background-color: rgba(46, 125, 50, 0.2); color: #4caf50; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border: 1px solid #4caf50; }
.scanner-header-blue { background-color: rgba(33, 150, 243, 0.2); color: #2196f3; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border: 1px solid #2196f3; }
/* تحسين شكل مربعات الاختيار */
.stCheckbox > label { font-weight: bold; color: #e0e0e0; }
/* جداول قافة */
.qafah-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; text-align: center; background-color: #1e2129; border-radius: 5px; overflow: hidden;}
.qafah-table th { background-color: #2e7d32; color: white; padding: 10px; font-weight: bold; }
.qafah-table td { color: #e0e0e0; padding: 10px; border-bottom: 1px solid #2d303e; }
.th-red { background-color: #c62828 !important; }
.th-gray { background-color: #424242 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# ⚡ 2. محركات السرعة والمسح الآلي
# ==========================================
@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol):
    return yf.Ticker(ticker_symbol).history(period="2y")

# 📡 قائمة مصغرة للسوق السعودي لتعمل كماسح آلي (يمكنك إضافة أي سهم هنا لاحقاً)
WATCHLIST = ['1120.SR', '2222.SR', '2010.SR', '1180.SR', '7010.SR', '4165.SR', '4210.SR', '2360.SR', '1211.SR', '2020.SR', '4050.SR', '4190.SR', '2280.SR']

@st.cache_data(ttl=1800) # يمسح السوق ويحفظ النتيجة لمدة 30 دقيقة لسرعة الموقع
def scan_market():
    breakouts, breakdowns, up_trends, down_trends = [], [], [], []
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    for tk in WATCHLIST:
        try:
            df_s = yf.Ticker(tk).history(period="1mo")
            if len(df_s) > 10:
                c, h, l = df_s['Close'], df_s['High'], df_s['Low']
                h3, l3 = h.rolling(3).max().shift(1), l.rolling(3).min().shift(1)
                
                last_c, prev_c = c.iloc[-1], c.iloc[-2]
                last_h3, prev_h3 = h3.iloc[-1], h3.iloc[-2]
                last_l3, prev_l3 = l3.iloc[-1], l3.iloc[-2]
                
                sym = tk.replace('.SR', '')
                
                # اختراق اليوم (كان السعر تحته أمس، واليوم تجاوزه)
                if last_c > last_h3 and prev_c <= prev_h3: breakouts.append({"السهم": sym, "تاريخ الاختراق": today_str})
                # كسر اليوم
                if last_c < last_l3 and prev_c >= prev_l3: breakdowns.append({"السهم": sym, "تاريخ الكسر": today_str})
                    
                # حساب الترند الحالي
                diff = c.diff()
                direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
                counter = 0
                for d in direction:
                    if d == 1: counter = counter + 1 if counter > 0 else 1
                    elif d == -1: counter = counter - 1 if counter < 0 else -1
                    else: counter = 0
                    
                if counter >= 2: up_trends.append({"السهم": sym, "أيام الصعود": counter, "تاريخ البداية": df_s.index[max(0, len(df_s) - counter)].strftime("%Y-%m-%d")})
                elif counter <= -2: down_trends.append({"السهم": sym, "أيام الهبوط": abs(counter), "تاريخ البداية": df_s.index[max(0, len(df_s) - abs(counter))].strftime("%Y-%m-%d")})
        except:
            continue
            
    return pd.DataFrame(breakouts), pd.DataFrame(breakdowns), pd.DataFrame(up_trends), pd.DataFrame(down_trends)

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d2ff; font-weight: bold;'>💎 مـاسـة</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-top: -15px;'>Masa Quant Platform</p>", unsafe_allow_html=True)
    st.markdown("---")
    ticker = st.text_input("أدخل رمز السهم للتحليل العميق:", value="4165.SR")
    analyze_btn = st.button("استخراج الفرص 💎", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown("### 🛠️ باقة الاستثمار (Pro):")
    st.markdown("- ✅ رادار السيولة وزيرو")
    st.markdown("- ✅ **مخطط الاختراقات التفاعلي 🆕**")
    st.markdown("- ✅ **الماسح الآلي للسوق (التقارير) 🚀**")
    st.markdown("---")
    st.info("💡 **حالة السيرفر:** متصل 🟢\n\n**قوة الخوارزمية:** 100% ⚡")
    st.markdown("<p style='text-align: center; font-size: 11px; color: #555; margin-top: 30px;'>© 2026 Masa Technologies | V9 Pro</p>", unsafe_allow_html=True)

# --- الواجهة الرئيسية ---
st.markdown("<h2 style='text-align: center;'>💎 غرفة عمليات ماسة (Masa Dashboard)</h2>", unsafe_allow_html=True)
st.markdown("---")

if analyze_btn or ticker:
    with st.spinner(f"جاري جلب بيانات {ticker} ومسح السوق..."):
        df = get_stock_data(ticker) 
        df_bup, df_bdn, df_tup, df_tdn = scan_market()
        
        if df.empty:
            st.error("❌ السهم غير موجود، تأكد من الرمز.")
        else:
            close, high, low = df['Close'], df['High'], df['Low']

            # --- الحسابات التراكمية ---
            df['1d_%'] = close.pct_change(1) * 100
            df['3d_%'] = close.pct_change(3) * 100 
            df['5d_%'] = close.pct_change(5) * 100
            df['10d_%'] = close.pct_change(10) * 100
            
            diff = close.diff()
            direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
            counter = []
            curr = 0
            for d in direction:
                if d == 1: curr = curr + 1 if curr > 0 else 1
                elif d == -1: curr = curr - 1 if curr < 0 else -1
                else: curr = 0
                counter.append(curr)
            df['Counter'] = counter
            
            def categorize(val):
                if pd.isna(val): return ""
                abs_val = abs(val)
                if abs_val >= 1.0: cat = "MAJOR"
                elif abs_val >= 0.1: cat = "HIGH"
                else: cat = "MEDIUM"
                if val > 0: return f"🟢 {val:.2f}% ({cat})"
                elif val < 0: return f"🔴 {val:.2f}% ({cat})"
                else: return f"⚪ {val:.2f}% ({cat})"
                
            df['Load_Diff_1D'] = df['1d_%'].apply(categorize)
            df['Load_Diff_3D'] = df['3d_%'].apply(categorize) 
            df['Load_Diff_5D'] = df['5d_%'].apply(categorize)
            df['Load_Diff_10D'] = df['10d_%'].apply(categorize)

            # --- حسابات مخطط الاختراقات الديناميكي ---
            df['High_3D'] = high.rolling(3).max().shift(1)
            df['Low_3D'] = low.rolling(3).min().shift(1)
            df['High_4D'] = high.rolling(4).max().shift(1)
            df['Low_4D'] = low.rolling(4).min().shift(1)
            df['High_10D'] = high.rolling(10).max().shift(1)
            df['Low_10D'] = low.rolling(10).min().shift(1)
            df['High_15D'] = high.rolling(15).max().shift(1)
            df['Low_15D'] = low.rolling(15).min().shift(1)

            df['SMA_20'] = close.rolling(window=20).mean()
            df['SMA_50'] = close.rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            delta_rsi = close.diff()
            up = delta_rsi.clip(lower=0)
            down = -1 * delta_rsi.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))

            df['ZR_High'] = high.rolling(window=300, min_periods=10).max().shift(1)
            df['ZR_Low'] = low.rolling(window=300, min_periods=10).min().shift(1)

            # --- الخلاصة الآلية ---
            last_close = close.iloc[-1]
            prev_close = close.iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            last_sma20, last_sma50 = df['SMA_20'].iloc[-1], df['SMA_50'].iloc[-1]
            last_vol, avg_vol = df['Volume'].iloc[-1], df['Vol_SMA_20'].iloc[-1]
            last_zr_high, last_zr_low = df['ZR_High'].iloc[-1], df['ZR_Low'].iloc[-1]

            if last_close > last_sma20 and last_close > last_sma50: trend, trend_color = "صاعد (إيجابي)", "🟢"
            elif last_close < last_sma20 and last_close < last_sma50: trend, trend_color = "هابط (سلبي)", "🔴"
            else: trend, trend_color = "عرضي (مختلط)", "🟡"

            if last_vol > (avg_vol * 1.5): vol_status, vol_color = "سيولة عالية", "🔥"
            elif last_vol > avg_vol: vol_status, vol_color = "سيولة جيدة", "📈"
            else: vol_status, vol_color = "سيولة ضعيفة", "❄️"
            
            if last_close >= last_zr_high * 0.98: zr_status, zr_color = "يختبر سقف زيرو", "⚠️"
            elif last_close <= last_zr_low * 1.05: zr_status, zr_color = "يختبر قاع زيرو", "💎"
            else: zr_status, zr_color = "في منتصف القناة", "⚖️"

            st.markdown(f"### 🤖 القراءة الآلية لسهم ({ticker}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الإغلاق الأخير", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند العام {trend_color}", trend)
            m3.metric(f"تدفق السيولة {vol_color}", vol_status)
            m4.metric(f"قراءة زيرو {zr_color}", zr_status)
            st.markdown("<br>", unsafe_allow_html=True)

            # ==========================================
            # 🗂️ نوافذ التبويب 
            # ==========================================
            tab1, tab2, tab3 = st.tabs(["🎯 مخطط الاختراقات والتقارير (كما في الصورة)", "📊 الشارت الشامل (الشموع وزيرو)", "📋 جدول البيانات والتحميل"])

            # --- التبويب 1: تصميم (Qafah) التفاعلي ---
            with tab1:
                # تقسيم الشاشة: الشارت يسار (75%) والتقارير يمين (25%) كالصورة
                col_chart, col_reports = st.columns([3, 1.2])
                
                with col_chart:
                    st.markdown("##### 🎛️ مخطط الاختراقات (اختر الفترات للعرض):")
                    c1, c2, c3, c4 = st.columns(4)
                    show_3d = c1.checkbox("عرض 3 أيام 🟠", value=True)
                    show_4d = c2.checkbox("عرض 4 أيام 🟢", value=False)
                    show_10d = c3.checkbox("عرض 10 أيام 🟣", value=True)
                    show_15d = c4.checkbox("عرض 15 يوم 🔴", value=False)
                    
                    df_plot2 = df.tail(150)
                    fig2 = go.Figure()
                    
                    # السعر الأساسي
                    fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Close'], mode='lines+markers', name='السعر', line=dict(color='dodgerblue', width=2), marker=dict(size=5)))
                    
                    # دالة رسم القنوات والاختراقات الحقيقية (تظهر فقط وقت الاختراق الفعلي)
                    def add_channel(fig, h_col, l_col, color, dash, name, marker_color, marker_size, symbol_up, symbol_dn):
                        fig.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2[h_col], line=dict(color=color, width=1.5, dash=dash, shape='hv'), name=f'مقاومة {name}'))
                        fig.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2[l_col], line=dict(color=color, width=1.5, dash=dash, shape='hv'), name=f'دعم {name}'))
                        
                        bo_up = df_plot2[(df_plot2['Close'] > df_plot2[h_col]) & (df_plot2['Close'].shift(1) <= df_plot2[h_col].shift(1))]
                        bo_dn = df_plot2[(df_plot2['Close'] < df_plot2[l_col]) & (df_plot2['Close'].shift(1) >= df_plot2[l_col].shift(1))]
                        
                        fig.add_trace(go.Scatter(x=bo_up.index, y=bo_up['Close'], mode='markers', marker=dict(symbol=symbol_up, size=marker_size, color=marker_color, line=dict(width=1, color='black')), name=f'اختراق {name}'))
                        fig.add_trace(go.Scatter(x=bo_dn.index, y=bo_dn['Close'], mode='markers', marker=dict(symbol=symbol_dn, size=marker_size, color='red', line=dict(width=1, color='black')), name=f'كسر {name}'))

                    if show_3d: add_channel(fig2, 'High_3D', 'Low_3D', 'orange', 'dot', '3 أيام', 'orange', 12, 'triangle-up', 'triangle-down')
                    if show_4d: add_channel(fig2, 'High_4D', 'Low_4D', '#4caf50', 'dash', '4 أيام', '#4caf50', 12, 'triangle-up', 'triangle-down')
                    if show_10d: add_channel(fig2, 'High_10D', 'Low_10D', '#9c27b0', 'solid', '10 أيام', '#9c27b0', 14, 'diamond', 'diamond-tall')
                    if show_15d: add_channel(fig2, 'High_15D', 'Low_15D', '#f44336', 'dashdot', '15 يوم', '#f44336', 16, 'star', 'star-triangle-down')

                    fig2.update_layout(height=650, hovermode='x unified', template='plotly_dark', margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

                with col_reports:
                    st.markdown("<h4 style='text-align: right; color: #fff;'>التقارير</h4>", unsafe_allow_html=True)
                    
                    # جدول الاختراقات
                    st.markdown("<div class='scanner-header'>الاختراق والكسر (اليوم)</div>", unsafe_allow_html=True)
                    if not df_bup.empty:
                        html_bup = "<table class='qafah-table'><tr><th>السهم</th><th>تاريخ الاختراق</th></tr>"
                        for _, row in df_bup.iterrows(): html_bup += f"<tr><td>{row['السهم']}</td><td>{row['التاريخ']}</td></tr>"
                        html_bup += "</table>"
                        st.markdown(html_bup, unsafe_allow_html=True)
                    else:
                        st.markdown("<table class='qafah-table'><tr><th class='th-gray'>لا توجد اختراقات اليوم</th></tr></table>", unsafe_allow_html=True)
                        
                    if not df_bdn.empty:
                        html_bdn = "<table class='qafah-table'><tr><th class='th-red'>السهم</th><th class='th-red'>تاريخ الكسر</th></tr>"
                        for _, row in df_bdn.iterrows(): html_bdn += f"<tr><td>{row['السهم']}</td><td>{row['التاريخ']}</td></tr>"
                        html_bdn += "</table>"
                        st.markdown(html_bdn, unsafe_allow_html=True)

                    # جدول الاتجاهات
                    st.markdown("<div class='scanner-header-blue'>الاتجاهات الحالية</div>", unsafe_allow_html=True)
                    if not df_tup.empty:
                        html_tup = "<table class='qafah-table'><tr><th>السهم صاعد</th><th>تاريخ البداية</th></tr>"
                        for _, row in df_tup.iterrows(): html_tup += f"<tr><td>{row['السهم']}</td><td>{row['تاريخ البداية']}</td></tr>"
                        html_tup += "</table>"
                        st.markdown(html_tup, unsafe_allow_html=True)
                    else:
                        st.markdown("<table class='qafah-table'><tr><th class='th-gray'>لا توجد مسارات صاعدة</th></tr></table>", unsafe_allow_html=True)

            # --- التبويب 2: الشارت الشامل (الشموع وزيرو) ---
            with tab2:
                df_plot = df.tail(180) 
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

                fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_High'], line=dict(color='white', width=2, dash='dot'), name='سقف زيرو'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_Low'], line=dict(color='orange', width=2, dash='dot'), name='قاع زيرو'), row=1, col=1)

                colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
                fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
                fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
                fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")

                fig.update_layout(height=800, template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # --- التبويب 3: الجدول والتصدير ---
            with tab3:
                table = pd.DataFrame({
                    'التاريخ': df.index.strftime('%Y-%m-%d'),
                    'الإغلاق': df['Close'].round(2),
                    'عداد الاتجاه': df['Counter'].astype(int),
                    'تغير 1 يوم': df['Load_Diff_1D'],
                    'تراكمي 3 أيام': df['Load_Diff_3D'], 
                    'تراكمي 5 أيام': df['Load_Diff_5D'],
                    'تراكمي 10 أيام': df['Load_Diff_10D'],
                    'حجم السيولة': df['Volume']
                })
                display_table = table.tail(15).iloc[::-1].copy()
                display_table['حجم السيولة'] = display_table['حجم السيولة'].apply(lambda x: f"{x:,}")
                display_table.set_index('التاريخ', inplace=True)
                st.dataframe(display_table, use_container_width=True, height=550)
                csv = table.tail(30).iloc[::-1].to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 تصدير البيانات للإكسل", data=csv, file_name=f'Masa_{ticker}.csv', mime='text/csv', use_container_width=True)
