import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# ⚡ 2. محرك السرعة
# ==========================================
@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol):
    return yf.Ticker(ticker_symbol).history(period="2y")

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d2ff; font-weight: bold;'>💎 مـاسـة</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-top: -15px;'>Masa Quant Platform</p>", unsafe_allow_html=True)
    st.markdown("---")
    ticker = st.text_input("أدخل رمز السهم (مثال: 4210.SR):", value="4210.SR")
    analyze_btn = st.button("استخراج الفرص 💎", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown("### 🛠️ باقة الاستثمار (Pro):")
    st.markdown("- ✅ رادار السيولة المتقدم")
    st.markdown("- ✅ خوارزمية زيرو انعكاس")
    st.markdown("- ✅ **شارت الزخم الكلاسيكي 🆕**")
    st.markdown("- ✅ التحليل التراكمي للزخم")
    st.markdown("---")
    st.info("💡 **حالة السيرفر:** متصل 🟢\n\n**قوة الخوارزمية:** 100% ⚡")
    st.markdown("<p style='text-align: center; font-size: 11px; color: #555; margin-top: 30px;'>© 2026 Masa Technologies | V7 Pro</p>", unsafe_allow_html=True)

# --- الواجهة الرئيسية ---
st.markdown("<h2 style='text-align: center;'>💎 غرفة عمليات ماسة (Masa Dashboard)</h2>", unsafe_allow_html=True)
st.markdown("---")

if analyze_btn or ticker:
    with st.spinner(f"جاري معالجة بيانات {ticker} بسرعة فائقة..."):
        df = get_stock_data(ticker) 
        
        if df.empty:
            st.error("❌ السهم غير موجود، تأكد من الرمز.")
        else:
            close = df['Close']
            high = df['High']
            low = df['Low']

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
            
            # --- حسابات الشارت الكلاسيكي (3 أيام و 10 أيام) ---
            df['High_3D'] = high.rolling(3).max().shift(1)
            df['Low_3D'] = low.rolling(3).min().shift(1)
            df['High_10D'] = high.rolling(10).max().shift(1)
            df['Low_10D'] = low.rolling(10).min().shift(1)

            df['SMA_20'] = close.rolling(window=20).mean()
            df['SMA_50'] = close.rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            delta_rsi = close.diff()
            up = delta_rsi.clip(lower=0)
            down = -1 * delta_rsi.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))

            zr_period = 300 
            df['ZR_High'] = high.rolling(window=zr_period, min_periods=10).max().shift(1)
            df['ZR_Low'] = low.rolling(window=zr_period, min_periods=10).min().shift(1)

            pivot_len = 10
            df['Pivot_High'] = high[high == high.rolling(window=2*pivot_len+1, center=True).max()]
            df['Pivot_Low'] = low[low == low.rolling(window=2*pivot_len+1, center=True).min()]
            recent_res = df['Pivot_High'].dropna().tail(3)
            recent_sup = df['Pivot_Low'].dropna().tail(3)

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
            # 🗂️ 3. نوافذ التبويب (الآن أصبحت 3 تبويبات)
            # ==========================================
            tab1, tab2, tab3 = st.tabs(["📊 الشارت التفاعلي (زيرو والسيولة)", "📈 شارت الزخم الكلاسيكي (صورتك)", "📋 جدول البيانات والتحميل"])

            # --- التبويب 1: الشارت الشامل ---
            with tab1:
                df_plot = df.tail(180) 
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

                fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_High'], line=dict(color='white', width=2, dash='dot'), name='سقف زيرو'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_Low'], line=dict(color='orange', width=2, dash='dot'), name='قاع زيرو'), row=1, col=1)

                bo_up_3d = df_plot[df_plot['Close'] > df_plot['High_3D']]
                fig.add_trace(go.Scatter(x=bo_up_3d.index, y=bo_up_3d['Close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='green', line=dict(width=1, color='black')), name='اختراق'), row=1, col=1)
                bo_down_3d = df_plot[df_plot['Close'] < df_plot['Low_3D']]
                fig.add_trace(go.Scatter(x=bo_down_3d.index, y=bo_down_3d['Close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='red', line=dict(width=1, color='black')), name='كسر'), row=1, col=1)

                for p_idx, p_val in recent_res.items():
                    if p_idx in df_plot.index or p_idx < df_plot.index[0]: fig.add_hline(y=p_val, line_dash="solid", row=1, col=1, line_color="#2196f3", line_width=1.5, opacity=0.8)
                for t_idx, t_val in recent_sup.items():
                    if t_idx in df_plot.index or t_idx < df_plot.index[0]: fig.add_hline(y=t_val, line_dash="solid", row=1, col=1, line_color="#ca8a04", line_width=1.5, opacity=0.8)

                colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
                fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
                fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
                fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")

                fig.update_layout(height=800, template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
            # --- التبويب 2: الشارت الكلاسيكي (الذي طلبته) ---
            with tab2:
                df_plot2 = df.tail(150) # فترة 150 يوم ليكون الخط واضحاً كالصورة
                fig2 = go.Figure()
                
                # خط السعر البسيط مع النقاط
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Close'], mode='lines+markers', name='السعر', line=dict(color='dodgerblue', width=2)))
                
                # خطوط 3 أيام (متقطعة برتقالية وتتخذ شكل درجات السلم)
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['High_3D'], line=dict(color='orange', width=1.5, dash='dot', shape='hv'), name='مقاومة 3 أيام'))
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Low_3D'], line=dict(color='orange', width=1.5, dash='dot', shape='hv'), name='دعم 3 أيام'))
                
                # خطوط 10 أيام (متصلة بنفسجية وتتخذ شكل درجات السلم)
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['High_10D'], line=dict(color='purple', width=1.5, shape='hv'), name='مقاومة 10 أيام'))
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Low_10D'], line=dict(color='purple', width=1.5, shape='hv'), name='دعم 10 أيام'))
                
                # إشارات الاختراق (الأسهم الخضراء والحمراء)
                bo_up = df_plot2[df_plot2['Close'] > df_plot2['High_3D']]
                fig2.add_trace(go.Scatter(x=bo_up.index, y=bo_up['Close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='green', line=dict(width=1, color='black')), name='اختراق 🔼'))
                
                bo_down = df_plot2[df_plot2['Close'] < df_plot2['Low_3D']]
                fig2.add_trace(go.Scatter(x=bo_down.index, y=bo_down['Close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='red', line=dict(width=1, color='black')), name='كسر 🔽'))
                
                # تم دمج الشارت مع الخلفية الداكنة الفخمة للموقع الجديد
                fig2.update_layout(height=650, hovermode='x unified', template='plotly_dark', margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

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
                st.download_button(label="📥 تصدير البيانات للإكسل (Excel / CSV)", data=csv, file_name=f'Masa_Quant_{ticker}.csv', mime='text/csv', use_container_width=True)
