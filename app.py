import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="منصة ماسة 💎 | للتحليل الكمي", layout="wide", page_icon="💎")
st.title("💎 منصة ماسة (Masa) للتحليل الكمي واصطياد الفرص")

col1, col2 = st.columns([1, 3])
with col1:
    ticker = st.text_input("أدخل رمز السهم (مثال: 2222.SR, 1120.SR, AAPL)", value="1120.SR")
    analyze_btn = st.button("تحليل شامل 🔍")

if analyze_btn or ticker:
    with st.spinner(f"جاري دمج الزخم مع زيرو انعكاس لسهم {ticker}..."):
        df = yf.Ticker(ticker).history(period="2y") 
        
        if df.empty:
            st.error("❌ تأكد من رمز السهم، لا توجد بيانات.")
        else:
            close = df['Close']
            high = df['High']
            low = df['Low']

            # ==========================================
            # 1. حسابات الزخم والأداء التراكمي
            # ==========================================
            df['1d_%'] = close.pct_change(1) * 100
            df['3d_%'] = close.pct_change(3) * 100  # الإضافة الجديدة للـ 3 أيام
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
            df['Load_Diff_3D'] = df['3d_%'].apply(categorize) # الإضافة الجديدة
            df['Load_Diff_5D'] = df['5d_%'].apply(categorize)
            df['Load_Diff_10D'] = df['10d_%'].apply(categorize)
            
            # خطوط الاختراقات
            df['High_3D'] = high.rolling(3).max().shift(1)
            df['Low_3D'] = low.rolling(3).min().shift(1)

            # ==========================================
            # 2. حسابات المؤشرات الاحترافية وزيرو انعكاس
            # ==========================================
            df['SMA_20'] = close.rolling(window=20).mean()
            df['SMA_50'] = close.rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            # RSI
            delta_rsi = close.diff()
            up = delta_rsi.clip(lower=0)
            down = -1 * delta_rsi.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))

            # زيرو انعكاس (300 شمعة)
            zr_period = 300 
            df['ZR_High'] = high.rolling(window=zr_period, min_periods=10).max().shift(1)
            df['ZR_Low'] = low.rolling(window=zr_period, min_periods=10).min().shift(1)

            # الدعوم والمقاومات
            pivot_len = 10
            df['Pivot_High'] = high[high == high.rolling(window=2*pivot_len+1, center=True).max()]
            df['Pivot_Low'] = low[low == low.rolling(window=2*pivot_len+1, center=True).min()]
            recent_res = df['Pivot_High'].dropna().tail(3)
            recent_sup = df['Pivot_Low'].dropna().tail(3)

            # ==========================================
            # 3. الخلاصة الآلية أعلى الموقع
            # ==========================================
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

            st.markdown(f"### 🤖 قراءة الرادار الشاملة لسهم ({ticker}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الإغلاق الأخير", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند العام {trend_color}", trend)
            m3.metric(f"تدفق السيولة {vol_color}", vol_status)
            m4.metric(f"قراءة زيرو انعكاس {zr_color}", zr_status)
            st.markdown("---")

            # ==========================================
            # 4. رسم الشارت الشامل 
            # ==========================================
            df_plot = df.tail(180) 
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

            # الشموع
            fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], 
                                         low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
            
            # زيرو انعكاس
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_High'], line=dict(color='white', width=2, dash='dot'), name='سقف زيرو'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_Low'], line=dict(color='orange', width=2, dash='dot'), name='قاع زيرو'), row=1, col=1)

            # علامات الاختراق
            bo_up_3d = df_plot[df_plot['Close'] > df_plot['High_3D']]
            fig.add_trace(go.Scatter(x=bo_up_3d.index, y=bo_up_3d['Close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='green', line=dict(width=1, color='black')), name='اختراق 🔼'), row=1, col=1)
            
            bo_down_3d = df_plot[df_plot['Close'] < df_plot['Low_3D']]
            fig.add_trace(go.Scatter(x=bo_down_3d.index, y=bo_down_3d['Close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='red', line=dict(width=1, color='black')), name='كسر 🔽'), row=1, col=1)

            # الدعوم والمقاومات
            for p_idx, p_val in recent_res.items():
                if p_idx in df_plot.index or p_idx < df_plot.index[0]:
                    fig.add_hline(y=p_val, line_dash="solid", row=1, col=1, line_color="#2196f3", line_width=1.5, opacity=0.8)
            for t_idx, t_val in recent_sup.items():
                if t_idx in df_plot.index or t_idx < df_plot.index[0]:
                    fig.add_hline(y=t_val, line_dash="solid", row=1, col=1, line_color="#ca8a04", line_width=1.5, opacity=0.8)

            # السيولة
            colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)

            # RSI
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
            fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
            fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")

            fig.update_layout(title=f'الشارت الشامل (زخم + زيرو + سيولة) | ({ticker})', height=850, 
                              template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # ==========================================
            # 5. جدول الزخم والأداء التراكمي الشامل
            # ==========================================
            st.markdown("### 📋 جدول الزخم والأداء التراكمي (مع السيولة)")
            table = pd.DataFrame({
                'التاريخ': df.index.strftime('%Y-%m-%d'),
                'الإغلاق': df['Close'].round(2),
                'عداد الاتجاه': df['Counter'].astype(int),
                'تغير 1 يوم': df['Load_Diff_1D'],
                'تراكمي 3 أيام': df['Load_Diff_3D'], # تم إضافته هنا
                'تراكمي 5 أيام': df['Load_Diff_5D'],
                'تراكمي 10 أيام': df['Load_Diff_10D'],
                'حجم السيولة': df['Volume'].apply(lambda x: f"{x:,}")
            })
            display_table = table.tail(15).iloc[::-1].set_index('التاريخ')
            st.dataframe(display_table, use_container_width=True, height=550)
