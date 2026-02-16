import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="الرادار الخوارزمي | Pro Max", layout="wide")
st.title("🚀 نظام التداول الخوارزمي (إصدار V3: زيرو انعكاس + دعوم/مقاومات)")
st.markdown("---")

col1, col2 = st.columns([1, 3])
with col1:
    ticker = st.text_input("أدخل رمز السهم (مثال: 2222.SR, 1120.SR, AAPL)", value="1120.SR")
    analyze_btn = st.button("تحليل احترافي 🔍")

if analyze_btn or ticker:
    with st.spinner(f"جاري تطبيق خوارزميات زيرو انعكاس لسهم {ticker}..."):
        # سحب بيانات سنتين لضمان دقة مسح الـ 300 شمعة
        df = yf.Ticker(ticker).history(period="2y") 
        
        if df.empty:
            st.error("❌ تأكد من رمز السهم، لا توجد بيانات.")
        else:
            # 1. الحسابات الفنية الأساسية
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            # حساب مؤشر القوة النسبية (RSI)
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))

            # ==========================================
            # 🌟 خوارزميات زيرو انعكاس والدعوم/المقاومات 🌟
            # ==========================================
            
            # أ. خطوط زيرو انعكاس (سقف وأرضية 300 شمعة)
            zr_period = 300 
            df['ZR_High'] = df['High'].rolling(window=zr_period, min_periods=10).max().shift(1)
            df['ZR_Low'] = df['Low'].rolling(window=zr_period, min_periods=10).min().shift(1)

            # ب. تحديد الدعوم والمقاومات (Pivots) - تماماً مثل TradingView
            pivot_len = 10
            df['Pivot_High'] = df['High'][df['High'] == df['High'].rolling(window=2*pivot_len+1, center=True).max()]
            df['Pivot_Low'] = df['Low'][df['Low'] == df['Low'].rolling(window=2*pivot_len+1, center=True).min()]
            
            recent_res = df['Pivot_High'].dropna().tail(3)
            recent_sup = df['Pivot_Low'].dropna().tail(3)

            # 2. الخلاصة الآلية (صندوق القرار)
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            
            last_sma20 = df['SMA_20'].iloc[-1]
            last_sma50 = df['SMA_50'].iloc[-1]
            last_vol = df['Volume'].iloc[-1]
            avg_vol = df['Vol_SMA_20'].iloc[-1]
            
            last_zr_high = df['ZR_High'].iloc[-1]
            last_zr_low = df['ZR_Low'].iloc[-1]

            if last_close > last_sma20 and last_close > last_sma50: trend, trend_color = "صاعد (إيجابي)", "🟢"
            elif last_close < last_sma20 and last_close < last_sma50: trend, trend_color = "هابط (سلبي)", "🔴"
            else: trend, trend_color = "عرضي (مختلط)", "🟡"

            if last_vol > (avg_vol * 1.5): vol_status, vol_color = "سيولة عالية (دخول هوامير)", "🔥"
            elif last_vol > avg_vol: vol_status, vol_color = "سيولة جيدة", "📈"
            else: vol_status, vol_color = "سيولة ضعيفة", "❄️"
            
            # قراءة زيرو انعكاس الآلية
            if last_close >= last_zr_high * 0.98: zr_status, zr_color = "يختبر سقف زيرو (مقاومة)", "⚠️"
            elif last_close <= last_zr_low * 1.05: zr_status, zr_color = "يختبر قاع زيرو (فرصة ارتداد)", "💎"
            else: zr_status, zr_color = "في منتصف القناة", "⚖️"

            st.markdown(f"### 🤖 قراءة الرادار الآلية لسهم ({ticker}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الإغلاق الأخير", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند العام {trend_color}", trend)
            m3.metric(f"تدفق السيولة {vol_color}", vol_status)
            m4.metric(f"قراءة زيرو انعكاس {zr_color}", zr_status)
            st.markdown("---")

            # 3. رسم الشارت الاحترافي (3 أجزاء)
            df_plot = df.tail(200) # عرض آخر 200 يوم ليكون الشارت واسعاً
            
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

            # القسم الأول: الشموع والمؤشرات
            fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], 
                                         low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
            
            # --- رسم خطوط زيرو انعكاس ---
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_High'], line=dict(color='white', width=2, dash='dot'), name='سقف زيرو'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_Low'], line=dict(color='orange', width=2, dash='dot'), name='قاع زيرو'), row=1, col=1)

            # --- رسم الدعوم والمقاومات (Pivots) ---
            # مقاومات (أزرق كما في كودك)
            for p_idx, p_val in recent_res.items():
                if p_idx in df_plot.index or p_idx < df_plot.index[0]:
                    fig.add_hline(y=p_val, line_dash="solid", row=1, col=1, line_color="#2196f3", line_width=1.5, opacity=0.8, annotation_text="مقاومة رئيسية", annotation_font_color="#2196f3")
            # دعوم (ذهبي كما في كودك)
            for t_idx, t_val in recent_sup.items():
                if t_idx in df_plot.index or t_idx < df_plot.index[0]:
                    fig.add_hline(y=t_val, line_dash="solid", row=1, col=1, line_color="#ca8a04", line_width=1.5, opacity=0.8, annotation_text="دعم رئيسي", annotation_font_color="#ca8a04")

            # القسم الثاني: السيولة (Volume)
            colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)

            # القسم الثالث: مؤشر RSI
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
            fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
            fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")

            fig.update_layout(title=f'زيرو انعكاس + دعوم ومقاومات | ({ticker})', height=850, 
                              template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. جدول الأداء
            st.markdown("### 📋 جدول السيولة ومستويات زيرو التاريخية")
            table = pd.DataFrame({
                'التاريخ': df.index.strftime('%Y-%m-%d'),
                'الإغلاق': df['Close'].round(2),
                'السيولة': df['Volume'].apply(lambda x: f"{x:,}"),
                'سقف زيرو (مقاومة)': df['ZR_High'].round(2),
                'أرضية زيرو (دعم)': df['ZR_Low'].round(2)
            })
            display_table = table.tail(10).iloc[::-1].set_index('التاريخ')
            st.dataframe(display_table, use_container_width=True)
