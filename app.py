import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="الرادار الخوارزمي", layout="wide")
st.title("🚀 نظام التداول الخوارزمي (Quant Dashboard)")

col1, col2 = st.columns([1, 3])
with col1:
    ticker = st.text_input("أدخل رمز السهم (مثال: 2222.SR, 1120.SR, AAPL)", value="2222.SR")
    analyze_btn = st.button("تحليل السهم 🔍")

if analyze_btn or ticker:
    with st.spinner(f"جاري تحليل السيولة والزخم لسهم {ticker}..."):
        df = yf.Ticker(ticker).history(period="1y")
        
        if df.empty:
            st.error("❌ تأكد من رمز السهم، لا توجد بيانات.")
        else:
            close = df['Close'].squeeze()
            high = df['High'].squeeze()
            low = df['Low'].squeeze()
            
            df['1d_%'] = close.pct_change(1) * 100
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
            df['Load_Diff_5D'] = df['5d_%'].apply(categorize)
            df['Load_Diff_10D'] = df['10d_%'].apply(categorize)
            
            df['High_3D'] = high.rolling(3).max().shift(1)
            df['Low_3D'] = low.rolling(3).min().shift(1)
            df['High_10D'] = high.rolling(10).max().shift(1)
            df['Low_10D'] = low.rolling(10).min().shift(1)
            
            table = pd.DataFrame({
                'التاريخ': df.index.strftime('%Y-%m-%d'),
                'عداد الاتجاه': df['Counter'].astype(int),
                'تغير 1 يوم': df['Load_Diff_1D'],
                'تراكمي 5 أيام': df['Load_Diff_5D'],
                'تراكمي 10 أيام': df['Load_Diff_10D']
            })
            display_table = table.tail(15).iloc[::-1].set_index('التاريخ')
            
            df_plot = df.tail(120) 
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines+markers', name='السعر', line=dict(color='dodgerblue', width=2)))
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['High_3D'], line=dict(color='orange', width=1.5, dash='dot', shape='hv'), name='مقاومة 3 أيام'))
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Low_3D'], line=dict(color='orange', width=1.5, dash='dot', shape='hv'), name='دعم 3 أيام'))
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['High_10D'], line=dict(color='purple', width=1.5, shape='hv'), name='مقاومة 10 أيام'))
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Low_10D'], line=dict(color='purple', width=1.5, shape='hv'), name='دعم 10 أيام'))
            
            bo_up_3d = df_plot[df_plot['Close'] > df_plot['High_3D']]
            fig.add_trace(go.Scatter(x=bo_up_3d.index, y=bo_up_3d['Close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='green', line=dict(width=1, color='black')), name='اختراق 🔼'))
            bo_down_3d = df_plot[df_plot['Close'] < df_plot['Low_3D']]
            fig.add_trace(go.Scatter(x=bo_down_3d.index, y=bo_down_3d['Close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='red', line=dict(width=1, color='black')), name='كسر 🔽'))
            
            fig.update_layout(title=f'مخطط الاختراقات وتتبع الزخم لسهم ({ticker})', hovermode='x unified', template='plotly_dark', height=550)
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("### 📋 جدول الزخم والأداء التراكمي")
            st.dataframe(display_table, use_container_width=True, height=400)
