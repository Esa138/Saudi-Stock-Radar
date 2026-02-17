import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import datetime
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# ==========================================
# 💎 1. إعدادات الهوية الاحترافية
# ==========================================
st.set_page_config(page_title="منصة ماسة 💎 | Masa Quant", layout="wide", page_icon="💎", initial_sidebar_state="collapsed")

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
.scanner-header { background-color: rgba(76, 175, 80, 0.1); color: #4caf50; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border: 1px solid #4caf50; }
.scanner-header-blue { background-color: rgba(33, 150, 243, 0.2); color: #2196f3; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border: 1px solid #2196f3; }
.scanner-header-red { background-color: rgba(244, 67, 54, 0.1); color: #f44336; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border: 1px solid #f44336; }
.scanner-header-gray { background-color: #2d303e; color: #fff; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #00d2ff;}
.qafah-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; text-align: center; background-color: #1e2129; border-radius: 5px; overflow: hidden;}
.qafah-table th { color: white; padding: 10px; font-weight: bold; }
.qafah-table td { color: #e0e0e0; padding: 10px; border-bottom: 1px solid #2d303e; }
[data-testid="collapsedControl"] { display: none; }
.search-container { background: linear-gradient(145deg, #1e2129, #15171e); padding: 20px; border-radius: 15px; border: 1px solid #2d303e; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); text-align: center;}
.filter-btn { border: 1px solid #4caf50; color: #4caf50; background-color: transparent; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin: 3px; }
.filter-btn-active { background-color: #4caf50; color: white; border: 1px solid #4caf50; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin: 3px; }
div.stRadio > div[role="radiogroup"] { justify-content: center; margin-bottom: 15px; }

/* 🧠 تصميم صندوق ذكاء ماسة (AI) */
.ai-box { background: linear-gradient(145deg, #12141a, #1a1c24); border-top: 4px solid #00d2ff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(0,210,255,0.15);}
.ai-header-flex { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d303e; padding-bottom: 15px; margin-bottom: 15px;}
.ai-title { color: #00d2ff; font-weight: bold; font-size: 24px; margin: 0;}
.ai-score-circle { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: bold; color: white; border: 4px solid; background-color: rgba(0,0,0,0.2); box-shadow: 0 0 15px currentColor;}
.ai-decision-text { font-size: 30px; font-weight: bold; margin-bottom: 20px; text-align: center; background-color: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px;}
.ai-reason-item { font-size: 15px; color: #e0e0e0; margin-bottom: 10px; line-height: 1.6; padding-right: 15px; border-right: 3px solid #2d303e;}
.ai-table { width: 100%; text-align: center; border-collapse: collapse; margin-top: 10px; background-color: #1e2129; border-radius: 8px; overflow: hidden;}
.ai-table th { background-color: #2d303e; color: white; padding: 10px; font-size: 13px;}
.ai-table td { padding: 10px; border-bottom: 1px solid #2d303e; font-size: 13px;}
.bo-badge { color: black; font-weight: bold; padding: 4px 8px; border-radius: 12px; font-size: 12px; display: inline-block;}
.target-text { color: #00E676; font-weight: bold; font-size: 14px; }
.sl-text { color: #FF5252; font-weight: bold; font-size: 14px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# ⚡ 2. محركات ذكاء ماسة (AI Engine)
# ==========================================
def get_ai_analysis(last_close, ma50, ma200, rsi, counter, zr_low, zr_high, event_text, bo_score_add):
    if pd.isna(ma50) or pd.isna(ma200): return 0, "جاري الحساب ⏳", "gray", ["بيانات غير كافية."]
    
    score = 50
    reasons = []
    
    if event_text != "استقرار ➖":
        score += bo_score_add
        if "🚀" in event_text or "🟢" in event_text or "💎" in event_text:
            reasons.append(f"⚡ <b>الحدث اللحظي:</b> إشارة إيجابية واضحة الآن ({event_text}).")
        elif "🩸" in event_text or "🔴" in event_text or "🛑" in event_text:
            reasons.append(f"⚠️ <b>الحدث اللحظي:</b> إشارة سلبية خطيرة الآن ({event_text}).")
        elif "⚠️" in event_text:
            reasons.append(f"⚠️ <b>الحدث اللحظي:</b> اختراق وهمي بسيولة ضعيفة، يجب الحذر.")

    if last_close > ma200:
        score += 15
        reasons.append("✅ <b>الاتجاه العام (MA 200):</b> مسار صاعد آمن استثمارياً.")
    else:
        score -= 20
        reasons.append("❌ <b>الاتجاه العام (MA 200):</b> كسر لمتوسط 200 (مسار هابط).")
        
    if last_close > ma50:
        dist = ((last_close - ma50) / ma50) * 100
        if dist < 3:
            score += 20
            reasons.append("💎 <b>دعم المضارب:</b> ارتداد من MA 50 (فرصة صيد ذهبية).")
        elif dist > 8:
            score -= 10
            reasons.append(f"⚠️ <b>التضخم:</b> السعر ابتعد عن الدعم بنسبة {dist:.1f}% (يُفضل جني الأرباح).")
        else:
            score += 10
            reasons.append("✅ <b>زخم المضاربة:</b> ثبات ممتاز فوق MA 50.")
    else:
        score -= 15
        reasons.append("🔴 <b>زخم المضاربة:</b> كسر لمتوسط 50 (مرحلة ضعف أو تصحيح).")

    if counter > 0:
        if counter <= 3:
            score += 15
            reasons.append(f"🚀 <b>العداد ({counter}):</b> موجة صاعدة في بدايتها.")
        elif counter >= 6:
            score -= 10
            reasons.append(f"⚠️ <b>العداد ({counter}):</b> صعود متتالي طويل (احتمال تصحيح).")
        else:
            score += 5
            reasons.append(f"📈 <b>العداد ({counter}):</b> منتصف موجة صاعدة.")
    elif counter < 0:
        if counter >= -3:
            score -= 5
            reasons.append(f"🔻 <b>العداد ({counter}):</b> بداية تصحيح هابط.")
        else:
            score -= 15
            reasons.append(f"🩸 <b>العداد ({counter}):</b> نزيف مستمر، لا تشتري.")

    if 40 <= rsi <= 65:
        score += 10
        reasons.append(f"✅ <b>RSI ({rsi:.1f}):</b> مؤشر صحي ولديه مساحة للصعود.")
    elif rsi > 70:
        score -= 15
        reasons.append(f"🚨 <b>RSI ({rsi:.1f}):</b> تشبع شرائي وتضخم.")
    elif rsi < 30:
        score += 15
        reasons.append(f"🛒 <b>RSI ({rsi:.1f}):</b> تشبع بيعي وفرصة ارتداد.")

    if pd.notna(zr_low) and last_close <= zr_low * 1.05: score += 15; reasons.append("🎯 <b>زيرو انعكاس:</b> السعر يختبر قاع القناة (منطقة ارتداد مؤسساتية).")
    elif pd.notna(zr_high) and last_close >= zr_high * 0.97: score -= 15; reasons.append("🧱 <b>زيرو انعكاس:</b> السعر يصطدم بسقف القناة (مقاومة تاريخية شرسة).")

    score = int(max(0, min(100, score)))
    
    if score >= 85 and ("🚀" in event_text or "🟢" in event_text or "💎" in event_text): return score, "فرصة ماسية 💎🚀", "#FFD700", reasons
    elif score >= 70: return score, "شراء / تجميع 🟢", "#00E676", reasons
    elif 45 <= score < 70: return score, "مراقبة 🟡", "#FFB300", reasons
    else: return score, "سلبية / خروج 🔴", "#FF5252", reasons

# ==========================================
# ⚡ 3. قوائم الأسواق والمسح الآلي
# ==========================================
@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol):
    return yf.Ticker(ticker_symbol).history(period="3y") 

SAUDI_WATCHLIST = ['1120.SR', '2222.SR', '2010.SR', '1180.SR', '7010.SR', '4165.SR', '4210.SR', '2360.SR', '1211.SR', '2020.SR', '4050.SR', '4190.SR', '2280.SR', '4030.SR']
US_WATCHLIST = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'META', 'GOOGL', 'AMD', 'NFLX', 'PLTR', 'COIN', 'SPY', 'QQQ']

def get_cat(val):
    if pd.isna(val): return ""
    v = abs(val)
    if v >= 2.0: return "(MAJOR)"
    elif v >= 0.5: return "(HIGH)"
    elif v >= 0.1: return "(MEDIUM)"
    else: return "(LOW)"

@st.cache_data(ttl=1800)
def scan_market(watchlist_list):
    breakouts, breakdowns, recent_up, recent_down = [], [], [], []
    loads_list, alerts_list, ai_picks = [], [], []
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for tk in watchlist_list:
        try:
            df_s = yf.Ticker(tk).history(period="1y")
            if len(df_s) > 200:
                c, h, l, vol = df_s['Close'], df_s['High'], df_s['Low'], df_s['Volume']
                sym = tk.replace('.SR', '')
                
                ma50 = c.rolling(50).mean()
                ma200 = c.rolling(200).mean()
                v_sma20 = vol.rolling(20).mean()
                
                h3, l3 = h.rolling(3).max().shift(1), l.rolling(3).min().shift(1)
                h4, l4 = h.rolling(4).max().shift(1), l.rolling(4).min().shift(1)
                h10, l10 = h.rolling(10).max().shift(1), l.rolling(10).min().shift(1)
                zr_h = h.rolling(300, min_periods=10).max().shift(1)
                zr_l = l.rolling(300, min_periods=10).min().shift(1)
                
                up_diff, down_diff = c.diff().clip(lower=0), -1 * c.diff().clip(upper=0)
                rsi = 100 - (100 / (1 + (up_diff.ewm(com=13, adjust=False).mean() / down_diff.ewm(com=13, adjust=False).mean())))
                
                last_c, prev_c, prev2_c = c.iloc[-1], c.iloc[-2], c.iloc[-3]
                last_vol, avg_vol = vol.iloc[-1], v_sma20.iloc[-1]

                diff = c.diff()
                direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
                counter = 0; counters = []
                for d in direction:
                    if d == 1: counter = counter + 1 if counter > 0 else 1
                    elif d == -1: counter = counter - 1 if counter < 0 else -1
                    else: counter = 0
                    counters.append(counter)
                cur_count = counters[-1]
                
                if cur_count > 0: recent_up.append({"السهم": sym, "تاريخ": df_s.index[-cur_count].strftime("%Y-%m-%d"), "منذ كم صف": cur_count})
                elif cur_count < 0: recent_down.append({"السهم": sym, "تاريخ": df_s.index[-abs(cur_count)].strftime("%Y-%m-%d"), "منذ كم صف": abs(cur_count)})

                pct_1d = (c.iloc[-1] / c.iloc[-2] - 1) * 100 if len(c)>1 else 0
                pct_3d = (c.iloc[-1] / c.iloc[-4] - 1) * 100 if len(c)>3 else 0
                pct_5d = (c.iloc[-1] / c.iloc[-6] - 1) * 100 if len(c)>5 else 0
                pct_10d = (c.iloc[-1] / c.iloc[-11] - 1) * 100 if len(c)>10 else 0

                loads_list.append({"holding ticker": sym,"date Latest Date": df_s.index[-1].strftime("%Y-%m-%d"),"daily direction counter": int(cur_count),"hitting_days": abs(cur_count),"load diff 1d %": pct_1d,"1d_cat": get_cat(pct_1d),"Top G/L 3Days": "✅" if pct_3d > 0 else "❌","load diff 3d %": pct_3d,"3d_cat": get_cat(pct_3d),"Top G/L 5Days": "✅" if pct_5d > 0 else "❌","load diff 5d %": pct_5d,"5d_cat": get_cat(pct_5d),"Top G/L 10days": "✅" if pct_10d > 0 else "❌","load diff 10d %": pct_10d,"10d_cat": get_cat(pct_10d)})

                # 🚀 حساب الاختراقات الشاملة لتظهر في (رادار الاختراقات اللحظي)
                bo_msgs_sys = []
                if last_c > h3.iloc[-1] and prev_c <= h3.iloc[-2]: 
                    bo_msgs_sys.append("3أيام")
                    alerts_list.append({"ticker": sym, "frame": "يومي", "datetime": now_time, "filter": "اختراق 3 أيام صاعد 🟢"})
                if last_c > h4.iloc[-1] and prev_c <= h4.iloc[-2]: bo_msgs_sys.append("4أيام")
                if last_c > h10.iloc[-1] and prev_c <= h10.iloc[-2]: bo_msgs_sys.append("10أيام")
                
                if bo_msgs_sys: breakouts.append({"السهم": sym, "التاريخ": today_str, "النوع": "+".join(bo_msgs_sys)})

                bd_msgs_sys = []
                if last_c < l3.iloc[-1] and prev_c >= l3.iloc[-2]: 
                    bd_msgs_sys.append("3أيام")
                    alerts_list.append({"ticker": sym, "frame": "يومي", "datetime": now_time, "filter": "كسر 3 أيام هابط 🔴"})
                if last_c < l4.iloc[-1] and prev_c >= l4.iloc[-2]: bd_msgs_sys.append("4أيام")
                if last_c < l10.iloc[-1] and prev_c >= l10.iloc[-2]: bd_msgs_sys.append("10أيام")
                
                if bd_msgs_sys: breakdowns.append({"السهم": sym, "التاريخ": today_str, "النوع": "+".join(bd_msgs_sys)})

                # 🧠 محرك الذكاء الاصطناعي للجدول (الحدث اللحظي المتطور)
                events = []
                vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1
                
                if bo_msgs_sys: 
                    events.append("اختراق 🚀" if vol_ratio >= 1.2 else "اختراق وهمي ⚠️")
                elif prev_c > h3.iloc[-2] and prev2_c <= h3.iloc[-3] and last_c > h3.iloc[-1]:
                    events.append("اختراق(أمس) 🚀")

                if bd_msgs_sys: 
                    events.append("كسر 🩸" if vol_ratio >= 1.2 else "كسر وهمي 🛑")
                elif prev_c < l3.iloc[-2] and prev2_c >= l3.iloc[-3] and last_c < l3.iloc[-1]:
                    events.append("كسر(أمس) 🩸")
                
                if cur_count == 1: events.append("ارتداد 🟢")
                elif cur_count == -1: events.append("تصحيح 🔴")

                if not events and pd.notna(ma50.iloc[-1]):
                    dist_ma50 = ((last_c - ma50.iloc[-1])/ma50.iloc[-1]) * 100
                    if 0 <= dist_ma50 <= 1.5 and prev_c > ma50.iloc[-2]:
                        events.append("دعم MA50 💎")
                    elif -1.5 <= dist_ma50 < 0 and prev_c > ma50.iloc[-2]:
                        events.append("كسر MA50 ⚠️")

                event_text = " + ".join(events) if events else "استقرار ➖"
                
                bo_score_add = 0
                if "اختراق 🚀" in event_text or "اختراق(أمس)" in event_text: bo_score_add = 15
                elif "كسر 🩸" in event_text or "كسر(أمس)" in event_text: bo_score_add = -15
                elif "ارتداد" in event_text: bo_score_add = 10
                elif "تصحيح" in event_text: bo_score_add = -10

                bg_color = "transparent"
                text_color = "gray"
                if "🚀" in event_text or "🟢" in event_text or "💎" in event_text: bg_color, text_color = "#00E676", "black"
                elif "🩸" in event_text or "🔴" in event_text or "🛑" in event_text: bg_color, text_color = "#FF5252", "white"
                elif "⚠️" in event_text: bg_color, text_color = "#FFD700", "black"

                target = zr_h.iloc[-1] if pd.notna(zr_h.iloc[-1]) else last_c * 1.05
                sl = ma50.iloc[-1] if pd.notna(ma50.iloc[-1]) else last_c * 0.95
                if last_c < sl: sl = l3.iloc[-1] if pd.notna(l3.iloc[-1]) else last_c * 0.90

                ai_score, ai_dec, ai_col, _ = get_ai_analysis(last_c, ma50.iloc[-1], ma200.iloc[-1], rsi.iloc[-1], cur_count, zr_l.iloc[-1], zr_h.iloc[-1], event_text, bo_score_add)
                
                event_badge = f"<span class='bo-badge' style='background-color:{bg_color}; color:{text_color}; border: 1px solid {bg_color if bg_color != 'transparent' else '#555'};'>{event_text}</span>"
                
                ai_picks.append({
                    "السهم": sym, 
                    "السعر": round(last_c, 2), 
                    "التقييم": ai_score, 
                    "الحدث اللحظي ⚡": event_badge, 
                    "الهدف 🎯": f"{target:.2f}",
                    "الوقف 🛡️": f"{sl:.2f}",
                    "القرار الخوارزمي": ai_dec, 
                    "اللون": ai_col
                })

        except: continue
    return pd.DataFrame(breakouts), pd.DataFrame(breakdowns), pd.DataFrame(recent_up), pd.DataFrame(recent_down), pd.DataFrame(loads_list), pd.DataFrame(alerts_list), pd.DataFrame(ai_picks)

st.markdown("<h1 style='text-align: center; color: #00d2ff; font-weight: bold;'>💎 منصة مـاسـة للتحليل الكمي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-top: -10px; margin-bottom: 30px;'>مستشارك الآلي الخوارزمي للسوق السعودي والأمريكي 🇸🇦🇺🇸</p>", unsafe_allow_html=True)

st.markdown("<div class='search-container'>", unsafe_allow_html=True)
market_choice = st.radio("اختر نطاق الماسح الآلي 🌐:", ["السوق السعودي 🇸🇦", "السوق الأمريكي 🇺🇸"], horizontal=True)
default_ticker = "NVDA" if "الأمريكي" in market_choice else "4030.SR"

col_empty1, col_search1, col_search2, col_empty2 = st.columns([1, 3, 1, 1])
with col_search1: ticker = st.text_input(f"🎯 رمز السهم:", value=default_ticker, label_visibility="collapsed")
with col_search2: analyze_btn = st.button("استخراج الفرص 💎", use_container_width=True, type="primary")
st.markdown("</div>", unsafe_allow_html=True)

if analyze_btn or ticker:
    ticker = ticker.upper() 
    selected_watchlist = US_WATCHLIST if "الأمريكي" in market_choice else SAUDI_WATCHLIST
    
    with st.spinner(f"جاري مسح السوق وتحليل البيانات بواسطة (ذكاء ماسة 🧠)..."):
        df = get_stock_data(ticker) 
        df_bup, df_bdn, df_recent_up, df_recent_down, df_loads, df_alerts, df_ai_picks = scan_market(selected_watchlist)
        
        if df.empty:
            st.error("❌ السهم غير موجود! تذكر: أضف (.SR) للأسهم السعودية.")
        else:
            close, high, low, vol = df['Close'], df['High'], df['Low'], df['Volume']

            df['SMA_50'] = close.rolling(window=50).mean()
            df['SMA_200'] = close.rolling(window=200).mean() 
            df['Vol_SMA_20'] = vol.rolling(window=20).mean()

            df['High_3D'] = high.rolling(3).max().shift(1)
            df['Low_3D'] = low.rolling(3).min().shift(1)
            df['High_4D'] = high.rolling(4).max().shift(1)
            df['Low_4D'] = low.rolling(4).min().shift(1)
            df['High_10D'] = high.rolling(10).max().shift(1)
            df['Low_10D'] = low.rolling(10).min().shift(1)
            df['High_15D'] = high.rolling(15).max().shift(1)
            df['Low_15D'] = low.rolling(15).min().shift(1)

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
            
            delta_rsi = close.diff()
            up = delta_rsi.clip(lower=0)
            down = -1 * delta_rsi.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))

            df['ZR_High'] = high.rolling(window=300, min_periods=10).max().shift(1)
            df['ZR_Low'] = low.rolling(window=300, min_periods=10).min().shift(1)

            last_close, prev_close, prev2_close = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            last_sma200 = df['SMA_200'].iloc[-1]
            last_sma50 = df['SMA_50'].iloc[-1]
            last_vol = df['Volume'].iloc[-1]
            avg_vol = df['Vol_SMA_20'].iloc[-1]
            last_zr_high = df['ZR_High'].iloc[-1]
            last_zr_low = df['ZR_Low'].iloc[-1]
            last_rsi = df['RSI'].iloc[-1]
            last_counter = df['Counter'].iloc[-1]

            main_bo_msgs_sys = []
            if last_close > df['High_3D'].iloc[-1] and prev_close <= df['High_3D'].iloc[-2]: main_bo_msgs_sys.append("3أيام")
            if last_close > df['High_4D'].iloc[-1] and prev_close <= df['High_4D'].iloc[-2]: main_bo_msgs_sys.append("4أيام")
            if last_close > df['High_10D'].iloc[-1] and prev_close <= df['High_10D'].iloc[-2]: main_bo_msgs_sys.append("10أيام")

            main_bd_msgs_sys = []
            if last_close < df['Low_3D'].iloc[-1] and prev_close >= df['Low_3D'].iloc[-2]: main_bd_msgs_sys.append("3أيام")
            if last_close < df['Low_4D'].iloc[-1] and prev_close >= df['Low_4D'].iloc[-2]: main_bd_msgs_sys.append("4أيام")
            if last_close < df['Low_10D'].iloc[-1] and prev_close >= df['Low_10D'].iloc[-2]: main_bd_msgs_sys.append("10أيام")

            main_events = []
            main_vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1
            
            if main_bo_msgs_sys: 
                main_events.append("اختراق 🚀" if main_vol_ratio >= 1.2 else "اختراق وهمي ⚠️")
            elif prev_close > df['High_3D'].iloc[-2] and prev2_close <= df['High_3D'].iloc[-3] and last_close > df['High_3D'].iloc[-1]:
                main_events.append("اختراق(أمس) 🚀")

            if main_bd_msgs_sys: 
                main_events.append("كسر 🩸" if main_vol_ratio >= 1.2 else "كسر وهمي 🛑")
            elif prev_close < df['Low_3D'].iloc[-2] and prev2_close >= df['Low_3D'].iloc[-3] and last_close < df['Low_3D'].iloc[-1]:
                main_events.append("كسر(أمس) 🩸")

            if last_counter == 1: main_events.append("ارتداد 🟢")
            elif last_counter == -1: main_events.append("تصحيح 🔴")

            if not main_events and pd.notna(last_sma50):
                main_dist_ma50 = ((last_close - last_sma50)/last_sma50) * 100
                if 0 <= main_dist_ma50 <= 1.5 and prev_close > df['SMA_50'].iloc[-2]:
                    main_events.append("دعم MA50 💎")
                elif -1.5 <= main_dist_ma50 < 0 and prev_close > df['SMA_50'].iloc[-2]:
                    main_events.append("كسر MA50 ⚠️")

            main_event_text = " + ".join(main_events) if main_events else "استقرار ➖"
            
            main_bo_score_add = 0
            if "اختراق 🚀" in main_event_text or "اختراق(أمس)" in main_event_text: main_bo_score_add = 15
            elif "كسر 🩸" in main_event_text or "كسر(أمس)" in main_event_text: main_bo_score_add = -15
            elif "ارتداد" in main_event_text: main_bo_score_add = 10
            elif "تصحيح" in main_event_text: main_bo_score_add = -10

            if pd.notna(last_sma200) and pd.notna(last_sma50):
                if last_close > last_sma200 and last_close > last_sma50: trend, trend_color = "مسار صاعد 🚀", "🟢"
                elif last_close < last_sma200 and last_close < last_sma50: trend, trend_color = "مسار هابط 🔴", "🔴"
                else: trend, trend_color = "تذبذب (حيرة) ⚖️", "🟡"
            else:
                trend, trend_color = "جاري الحساب...", "⚪"

            vol_status, vol_color = ("سيولة عالية", "🔥") if last_vol > (avg_vol * 1.5) else ("سيولة جيدة", "📈") if last_vol > avg_vol else ("سيولة ضعيفة", "❄️")
            zr_status, zr_color = ("يختبر سقف زيرو", "⚠️") if last_close >= last_zr_high * 0.98 else ("يختبر قاع زيرو", "💎") if last_close <= last_zr_low * 1.05 else ("في منتصف القناة", "⚖️")
            currency = "$" if "الأمريكي" in market_choice or not ticker.endswith('.SR') else "ريال"

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

            st.markdown(f"### 🤖 قراءة استراتيجية ماسة لسهم ({ticker}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"الإغلاق الأخير ({currency})", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند الاستراتيجي {trend_color}", trend)
            m3.metric(f"تدفق السيولة {vol_color}", vol_status)
            m4.metric(f"قراءة زيرو {zr_color}", zr_status)
            st.markdown("<br>", unsafe_allow_html=True)

            # ==========================================
            # 🧠 التبويب الأول: لوحة القيادة المركزية (AI + Live Reports)
            # ==========================================
            tab_ai, tab1, tab5, tab6, tab2, tab3, tab4 = st.tabs([
                "🧠 لوحة القيادة (ذكاء ماسة + التقارير) 👑",
                "🎯 شارت الاختراقات", 
                "🗂️ ماسح السوق (Loads)",
                "🚨 رادار التنبيهات",
                "🌐 TradingView", 
                "📊 شارت الخوارزمية", 
                "📋 بيانات السهم"
            ])

            with tab_ai:
                col_ai_main, col_ai_reports = st.columns([2.5, 1.2])
                
                with col_ai_main:
                    ai_score, ai_decision, ai_color, ai_reasons = get_ai_analysis(last_close, last_sma50, last_sma200, last_rsi, last_counter, last_zr_low, last_zr_high, main_event_text, main_bo_score_add)
                    
                    st.markdown(f"""
                    <div class="ai-box">
                        <div class="ai-header-flex">
                            <div class="ai-title">🤖 التقرير الآلي لسهم ({ticker})</div>
                            <div class="ai-score-circle" style="border-color: {ai_color}; color: {ai_color};">
                                {ai_score}
                            </div>
                        </div>
                        <div class="ai-decision-text" style="color: {ai_color};">
                            القرار: {ai_decision}
                        </div>
                        <div style="margin-top: 15px;">
                            {''.join([f'<div class="ai-reason-item" dir="rtl">{r}</div>' for r in ai_reasons])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("#### 🎯 خطة التداول الآلي (لجميع أسهم القائمة):")
                    if not df_ai_picks.empty:
                        df_ai_disp = pd.DataFrame(df_ai_picks).sort_values(by="التقييم", ascending=False)
                        html_ai = "<table class='ai-table' dir='rtl'><tr><th>السهم</th><th>السعر</th><th>التقييم</th><th>الحدث اللحظي ⚡</th><th>الهدف 🎯</th><th>الوقف 🛡️</th><th>القرار الخوارزمي</th></tr>"
                        for _, row in df_ai_disp.iterrows():
                            html_ai += f"<tr><td><b>{row['السهم']}</b></td><td>{row['السعر']:.2f}</td><td style='color:{row['اللون']}; font-size:16px; font-weight:bold;'>{row['التقييم']}</td><td>{row['الحدث اللحظي ⚡']}</td><td><span class='target-text'>{row['الهدف 🎯']}</span></td><td><span class='sl-text'>{row['الوقف 🛡️']}</span></td><td style='color:{row['اللون']}; font-weight:bold;'>{row['القرار الخوارزمي']}</td></tr>"
                        html_ai += "</table>"
                        st.markdown(html_ai, unsafe_allow_html=True)

                # ⚡ التقارير الحية نُقلت هنا للشاشة الرئيسية!
                with col_ai_reports:
                    st.markdown("<div class='scanner-header-gray'>التغييرات الأخيرة في الاتجاه</div>", unsafe_allow_html=True)
                    c_txt1, c_inp, c_txt2 = st.columns([2.5, 1, 0.5])
                    with c_txt1: st.markdown("<p style='font-size:13px; margin-top:8px; text-align:right; color:#ccc;'>عرض التغييرات خلال آخر:</p>", unsafe_allow_html=True)
                    with c_inp: n_days = st.number_input("صف", min_value=1, max_value=30, value=3, label_visibility="collapsed")
                    with c_txt2: st.markdown("<p style='font-size:13px; margin-top:8px; text-align:right; color:#ccc;'>صف</p>", unsafe_allow_html=True)
                    
                    df_up_recent = df_recent_up[df_recent_up['منذ كم صف'] <= n_days].sort_values(by='منذ كم صف') if not df_recent_up.empty else pd.DataFrame()
                    df_dn_recent = df_recent_down[df_recent_down['منذ كم صف'] <= n_days].sort_values(by='منذ كم صف') if not df_recent_down.empty else pd.DataFrame()
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if not df_up_recent.empty:
                        html_up = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#4CAF50; color:white;'>منذ كم صف</th><th style='background-color:#4CAF50; color:white;'>تغير إلى صاعد</th><th style='background-color:#4CAF50; color:white;'>السهم</th></tr>"
                        for _, row in df_up_recent.iterrows():
                            html_up += f"<tr><td>{row['منذ كم صف']}</td><td>{row['تاريخ']}</td><td><span style='background-color: #1565c0; color: white; padding: 2px 6px; border-radius: 3px;'>{row['السهم']}</span></td></tr>"
                        html_up += "</table>"
                        st.markdown(html_up, unsafe_allow_html=True)
                    else: st.markdown(f"<table class='qafah-table' dir='rtl'><tr><th style='background-color:#4CAF50; color:white;'>تغير إلى صاعد</th></tr><tr><td style='color:gray;'>لا توجد تغيرات صاعدة آخر {n_days} صفوف</td></tr></table>", unsafe_allow_html=True)
                    
                    if not df_dn_recent.empty:
                        html_dn = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#e53935; color:white;'>منذ كم صف</th><th style='background-color:#e53935; color:white;'>تغير إلى هابط</th><th style='background-color:#e53935; color:white;'>السهم</th></tr>"
                        for _, row in df_dn_recent.iterrows(): 
                            html_dn += f"<tr><td style='background-color:rgba(229, 57, 53, 0.1);'>{row['منذ كم صف']}</td><td style='background-color:rgba(229, 57, 53, 0.1);'>{row['تاريخ']}</td><td style='color:#ef9a9a; font-weight:bold; background-color:rgba(229, 57, 53, 0.1);'>{row['السهم']}</td></tr>"
                        html_dn += "</table>"
                        st.markdown(html_dn, unsafe_allow_html=True)
                    else: st.markdown(f"<table class='qafah-table' dir='rtl'><tr><th style='background-color:#e53935; color:white;'>تغير إلى هابط</th></tr><tr><td style='color:gray;'>لا توجد تغيرات هابطة آخر {n_days} صفوف</td></tr></table>", unsafe_allow_html=True)

                    st.markdown("<hr style='border-color: #2d303e;'>", unsafe_allow_html=True)
                    
                    # 🚀 جداول الاختراقات والكسور (عادت للشاشة الرئيسية بميزة النوع)
                    st.markdown("<div class='scanner-header'>اختراق المقاومة (اليوم) 🚀</div>", unsafe_allow_html=True)
                    if not df_bup.empty:
                        html_bup = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#2e7d32; color:white;'>النوع</th><th style='background-color:#2e7d32; color:white;'>السهم</th></tr>"
                        for _, row in df_bup.iterrows(): html_bup += f"<tr><td style='font-size:11px;'>{row['النوع']}</td><td style='color:#00d2ff; font-weight:bold;'>{row['السهم']}</td></tr>"
                        html_bup += "</table>"
                        st.markdown(html_bup, unsafe_allow_html=True)
                    else: st.markdown("<table class='qafah-table'><tr><th style='background-color:#2e7d32; color:white;'>الاختراق (اليوم)</th></tr><tr><td style='color:gray;'>لا توجد اختراقات اليوم</td></tr></table>", unsafe_allow_html=True)
                        
                    st.markdown("<div class='scanner-header-red'>كسر الدعم (اليوم) 🩸</div>", unsafe_allow_html=True)
                    if not df_bdn.empty:
                        html_bdn = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#c62828; color:white;'>النوع</th><th style='background-color:#c62828; color:white;'>السهم</th></tr>"
                        for _, row in df_bdn.iterrows(): html_bdn += f"<tr><td style='font-size:11px;'>{row['النوع']}</td><td style='color:#ef9a9a; font-weight:bold;'>{row['السهم']}</td></tr>"
                        html_bdn += "</table>"
                        st.markdown(html_bdn, unsafe_allow_html=True)
                    else: st.markdown("<table class='qafah-table'><tr><th style='background-color:#c62828; color:white;'>الكسر (اليوم)</th></tr><tr><td style='color:gray;'>لا توجد كسور اليوم</td></tr></table>", unsafe_allow_html=True)

            with tab1:
                c1, c2, c3, c4 = st.columns(4)
                show_3d = c1.checkbox("عرض 3 أيام 🟠", value=True)
                show_4d = c2.checkbox("عرض 4 أيام 🟢", value=False)
                show_10d = c3.checkbox("عرض 10 أيام 🟣", value=True)
                show_15d = c4.checkbox("عرض 15 يوم 🔴", value=False)
                df_plot2 = df.tail(150)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Close'], mode='lines+markers', name='السعر', line=dict(color='dodgerblue', width=2), marker=dict(size=5)))
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

            with tab5:
                if not df_loads.empty:
                    top_3d = len(df_loads[df_loads['load diff 3d %'] > 0])
                    worst_3d = len(df_loads[df_loads['load diff 3d %'] < 0])
                    top_5d = len(df_loads[df_loads['load diff 5d %'] > 0])
                    worst_5d = len(df_loads[df_loads['load diff 5d %'] < 0])
                    top_10d = len(df_loads[df_loads['load diff 10d %'] > 0])
                    worst_10d = len(df_loads[df_loads['load diff 10d %'] < 0])
                    st.markdown(f"""<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:8px; margin-bottom: 20px;"><span class="filter-btn-active">All ({len(df_loads)})</span><span class="filter-btn">Top 3d Gainers ({top_3d})</span><span class="filter-btn" style="color:#f44336; border-color:#f44336;">Top 3d Losers ({worst_3d})</span><span class="filter-btn">Top 5d Gainers ({top_5d})</span><span class="filter-btn" style="color:#f44336; border-color:#f44336;">Top 5d Losers ({worst_5d})</span><span class="filter-btn">Top 10d Gainers ({top_10d})</span><span class="filter-btn" style="color:#f44336; border-color:#f44336;">Top 10d Losers ({worst_10d})</span></div>""", unsafe_allow_html=True)
                    df_loads_styled = df_loads.copy()
                    def color_loads_values(val):
                        if isinstance(val, str) and "%" in val:
                            if "-" in val: return 'color: #f44336; font-weight: bold;'
                            elif val.startswith("0.0000"): return 'color: gray;'
                            else: return 'color: #4caf50; font-weight: bold;'
                        elif isinstance(val, int) and (val > 0): return 'color: #4caf50; font-weight: bold;'
                        elif isinstance(val, int) and (val < 0): return 'color: #f44336; font-weight: bold;'
                        return ''
                    df_loads_styled['load diff 1d %'] = df_loads_styled.apply(lambda x: f"{x['load diff 1d %']:.4f}% {x['1d_cat']}", axis=1)
                    df_loads_styled['load diff 3d %'] = df_loads_styled.apply(lambda x: f"{x['load diff 3d %']:.4f}% {x['3d_cat']}", axis=1)
                    df_loads_styled['load diff 5d %'] = df_loads_styled.apply(lambda x: f"{x['load diff 5d %']:.4f}% {x['5d_cat']}", axis=1)
                    df_loads_styled['load diff 10d %'] = df_loads_styled.apply(lambda x: f"{x['load diff 10d %']:.4f}% {x['10d_cat']}", axis=1)
                    df_loads_styled = df_loads_styled.drop(columns=['1d_cat', '3d_cat', '5d_cat', '10d_cat'])
                    st.dataframe(df_loads_styled.style.applymap(color_loads_values), use_container_width=True, height=550, hide_index=True)

            with tab6:
                if not df_alerts.empty:
                    def color_alerts(val):
                        if isinstance(val, str):
                            if "صاعدة" in val or "شراء" in val or "🟢" in val or "🚀" in val: return 'color: #4caf50; font-weight: bold;'
                            if "كسر" in val or "سلبية" in val or "🔴" in val or "⚠️" in val: return 'color: #f44336; font-weight: bold;'
                        return ''
                    st.dataframe(df_alerts.style.applymap(color_alerts), use_container_width=True, height=550, hide_index=True)

            with tab2:
                if ticker.endswith('.SR'): tv_symbol = f"TADAWUL:{ticker.replace('.SR', '')}"
                else: tv_symbol = ticker
                tradingview_html = f"""<div class="tradingview-widget-container" style="height:700px;width:100%"><div id="tradingview_masa" style="height:100%;width:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true,"symbol": "{tv_symbol}","interval": "D","timezone": "Asia/Riyadh","theme": "dark","style": "1","locale": "ar_AE","enable_publishing": false,"backgroundColor": "#1a1c24","gridColor": "#2d303e","hide_top_toolbar": false,"hide_legend": false,"save_image": false,"container_id": "tradingview_masa","toolbar_bg": "#1e2129","studies": ["Volume@tv-basicstudies","RSI@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"]}});</script></div>"""
                components.html(tradingview_html, height=700)

            with tab3:
                df_plot = df.tail(300) 
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
                fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_200'], line=dict(color='orange', width=2.5), name='MA 200 (V9)'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], line=dict(color='cyan', width=2), name='MA 50 (V9)'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_High'], line=dict(color='white', width=2, dash='dot'), name='سقف زيرو'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ZR_Low'], line=dict(color='orange', width=2, dash='dot'), name='قاع زيرو'), row=1, col=1)
                colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
                fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI 14'), row=3, col=1)
                fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
                fig.add_hline(y=50, line_dash="solid", row=3, col=1, line_color="gray", opacity=0.5) 
                fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")
                fig.update_layout(height=800, template='plotly_dark', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            with tab4:
                table = pd.DataFrame({'التاريخ': df.index.strftime('%Y-%m-%d'),'الإغلاق': df['Close'].round(2),'عداد الاتجاه': df['Counter'].astype(int),'MA 50': df['SMA_50'].round(2),'MA 200': df['SMA_200'].round(2),'تغير 1 يوم': df['Load_Diff_1D'],'تراكمي 3 أيام': df['Load_Diff_3D'],'تراكمي 5 أيام': df['Load_Diff_5D'],'تراكمي 10 أيام': df['Load_Diff_10D'],'حجم السيولة': df['Volume']})
                display_table = table.tail(15).iloc[::-1].copy()
                display_table['حجم السيولة'] = display_table['حجم السيولة'].apply(lambda x: f"{x:,}")
                display_table.set_index('التاريخ', inplace=True)
                st.dataframe(display_table, use_container_width=True, height=550)
                csv = table.tail(30).iloc[::-1].to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 تصدير البيانات للإكسل", data=csv, file_name=f'Masa_{ticker}.csv', mime='text/csv', use_container_width=True)
