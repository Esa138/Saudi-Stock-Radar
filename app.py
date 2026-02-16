import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="الرادار الخوارزمي | Pro", layout="wide")
st.title("🚀 نظام التداول الخوارزمي (النسخة الاحترافية V2)")
st.markdown("---")

col1, col2 = st.columns([1, 3])
with col1:
    ticker = st.text_input("أدخل رمز السهم (مثال: 2222.SR, 1120.SR, AAPL)", value="1120.SR")
    analyze_btn = st.button("تحليل احترافي 🔍")

if analyze_btn or ticker:
    with st.spinner(f"جاري الفحص العميق لسيولة وزخم {ticker}..."):
        df = yf.Ticker(ticker).history(period="1y")
        
        if df.empty:
            st.error("❌ تأكد من رمز السهم، لا توجد بيانات.")
        else:
            # 1. الحسابات الفنية
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

            # 2. الخلاصة الآلية (صندوق القرار)
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            
            last_sma20 = df['SMA_20'].iloc[-1]
            last_sma50 = df['SMA_50'].iloc[-1]
            last_rsi = df['RSI'].iloc[-1]
            last_vol = df['Volume'].iloc[-1]
            avg_vol = df['Vol_SMA_20'].iloc[-1]

            # تحديد الترند
            if last_close > last_sma20 and last_close > last_sma50: trend, trend_color = "صاعد (إيجابي)", "🟢"
            elif last_close < last_sma20 and last_close < last_sma50: trend, trend_color = "هابط (سلبي)", "🔴"
            else: trend, trend_color = "عرضي (مختلط)", "🟡"

            # تحديد الزخم
            if pd.isna(last_rsi):
                rsi_status, rsi_color = "جاري الحساب...", "⚪"
                last_rsi_display = 0.0
            elif last_rsi > 70: 
                rsi_status, rsi_color = "تشبع شرائي (احذر)", "🔴"
                last_rsi_display = last_rsi
            elif last_rsi < 30: 
                rsi_status, rsi_color = "تشبع بيعي (فرصة)", "🟢"
                last_rsi_display = last_rsi
            else: 
                rsi_status, rsi_color = "زخم طبيعي", "⚪"
                last_rsi_display = last_rsi

            # تحديد السيولة
            if last_vol > (avg_vol * 1.5): vol_status, vol_color = "سيولة عالية (دخول هوامير)", "🔥"
            elif last_vol > avg_vol: vol_status, vol_color = "سيولة جيدة", "📈"
            else: vol_status, vol_color = "سيولة ضعيفة", "❄️"

            # عرض لوحة القيادة الذكية
            st.markdown(f"### 🤖 قراءة الرادار الآلية لسهم ({ticker}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الإغلاق الأخير", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند العام {trend_color}", trend)
            m3.metric(f"مؤشر القوة RSI {rsi_color}", f"{last_rsi_display:.1f} - {rsi_status}")
            m4.metric(f"تدفق السيولة {vol_color}", vol_status)
            st.markdown("---")

            # 3. رسم الشارت الاحترافي (3 أجزاء)
            df_plot = df.tail(150) # عرض آخر 150 يوم ليكون الشارت واضحاً
            
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

            # القسم الأول: الشموع والمتوسطات
            fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], 
                                         low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_20'], line=dict(color='orange', width=1.5), name='متوسط 20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], line=dict(color='dodgerblue', width=1.5), name='متوسط 50'), row=1, col=1)

            # القسم الثاني: السيولة (Volume)
            colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)

            # القسم الثالث: مؤشر RSI
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
            fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
            fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")

            fig.update_layout(title=f'التحليل الفني الشامل لسهم ({ticker})', height=800, 
                              template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. جدول الأداء التراكمي
            st.markdown("### 📋 جدول السيولة والزخم التاريخي")
            table = pd.DataFrame({
                'التاريخ': df.index.strftime('%Y-%m-%d'),
                'الإغلاق': df['Close'].round(2),
                'حجم التداول (الفوليوم)': df['Volume'].apply(lambda x: f"{x:,}"),
                'مؤشر RSI': df['RSI'].round(1)
            })
            display_table = table.tail(15).iloc[::-1].set_index('التاريخ')
            st.dataframe(display_table, use_container_width=True)
