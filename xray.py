import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures
import warnings
import time

warnings.filterwarnings('ignore')

# ==========================================
# 🦅 إعدادات قمرة القيادة (الرادار الشبح)
# ==========================================
st.set_page_config(page_title="MASA X-RAY | رادار الحيتان العميق", page_icon="👁️‍🗨️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #0A0E17; }
    .main-title { color: #00FF41; text-align: center; font-size: 50px; font-weight: 900; text-shadow: 0px 0px 20px rgba(0,255,65,0.5); margin-bottom: 5px; }
    .sub-title { color: #8B949E; text-align: center; font-size: 18px; margin-bottom: 30px; letter-spacing: 1px;}
    .legend-box { background: rgba(20, 24, 31, 0.9); border: 1px solid #30363D; border-right: 4px solid #00FF41; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: 900 !important; font-size: 18px !important; border-radius: 8px !important; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #00CC33 !important; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">👁️‍🗨️ MASA X-RAY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">طائرة الاستطلاع الشبحية | Zero-Latency Quant Engine</div>', unsafe_allow_html=True)

st.markdown("""
<div class="legend-box">
    <strong style="color: #00FF41; font-size: 22px;">فك التشفير الاستخباراتي للحيتان (قواعد الاشتباك):</strong><br><br>
    <span style="font-size: 16px;">
    📦 <b>زنبرك مضغوط:</b> جفاف تام للسيولة وانكماش للتذبذب.. السهم تم تجفيفه وانفجاره وشيك جداً.<br><br>
    🧽 <b>ابتلاع مؤسساتي:</b> حجم تداول فلكي داخل شمعة ضيقة.. الحوت يمتص عروض القطيع بصمت تام.<br><br>
    🎯 <b>مغناطيس التكلفة:</b> السعر الحالي يتطابق مع (متوسط تكلفة الملياردير لآخر 10 أيام). دخول آمن ومخاطرة شبه معدومة.
    </span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📚 قاموس الأهداف (نخبة السوق كعينة - انسخ قاموسك الكامل 168 سهم وضعه هنا لاحقاً)
# ==========================================
SAUDI_NAMES = {
    '1010.SR': 'الرياض', '1020.SR': 'الجزيرة', '1030.SR': 'الاستثمار', '1050.SR': 'السعودي الفرنسي', '1060.SR': 'الأول', '1080.SR': 'العربي', '1111.SR': 'تداول', '1120.SR': 'الراجحي', '1140.SR': 'البلاد', '1150.SR': 'الإنماء', '1180.SR': 'الأهلي', '1182.SR': 'أملاك', '1183.SR': 'سهل', '1833.SR': 'الموارد',
    '2010.SR': 'سابك', '2222.SR': 'أرامكو', '7010.SR': 'stc', '4321.SR': 'المراكز', '4300.SR': 'دار الأركان', '4142.SR': 'الماجد للعود', '4015.SR': 'جمجوم فارما', '2082.SR': 'أكوا باور', '7204.SR': 'توبي', '7020.SR': 'موبايلي', '2280.SR': 'المراعي', '4164.SR': 'النهدي', '4013.SR': 'سليمان الحبيب', '4220.SR': 'إعمار', '4322.SR': 'ريتال', '7202.SR': 'سلوشنز', '7203.SR': 'علم', '8210.SR': 'بوبا', '8010.SR': 'التعاونية'
}

# ==========================================
# 🧠 المحرك الكمّي الخارق (X-Ray Core)
# ==========================================
def scan_whale_target(ticker, name):
    try:
        # تحميل بيانات 30 يوماً فقط للسرعة الخارقة
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if df.empty or len(df) < 20:
            return None

        curr_close = float(df['Close'].iloc[-1])
        curr_vol = float(df['Volume'].iloc[-1])
        curr_spread = float(df['High'].iloc[-1] - df['Low'].iloc[-1])

        avg_vol_20 = float(df['Volume'].tail(20).mean())
        avg_spread_20 = float((df['High'] - df['Low']).tail(20).mean())
        
        avg_vol_3 = float(df['Volume'].tail(3).mean())
        avg_spread_3 = float((df['High'] - df['Low']).tail(3).mean())

        tags = []
        score = 0
        
        # 1. 📦 كاشف الزنبرك
        if avg_vol_3 < (avg_vol_20 * 0.6) and avg_spread_3 < (avg_spread_20 * 0.6):
            tags.append("📦 مضغوط")
            score += 1

        # 2. 🧽 كاشف الابتلاع
        if curr_vol > (avg_vol_20 * 1.5) and curr_spread < (avg_spread_20 * 0.8):
            tags.append("🧽 ابتلاع")
            score += 2

        # 3. 🎯 كاشف التكلفة (VWAP-10)
        last_10 = df.tail(10)
        sum_vol_10 = float(last_10['Volume'].sum())
        dist_str = "غير متوفر"
        dist_val = 999.0
        vwap_10 = 0.0
        
        if sum_vol_10 > 0:
            typical_price = (last_10['High'] + last_10['Low'] + last_10['Close']) / 3
            vwap_10 = float((typical_price * last_10['Volume']).sum() / sum_vol_10)
            
            # حساب البعد عن التكلفة بالنسبة المئوية
            dist_val = ((curr_close - vwap_10) / vwap_10) * 100
            dist_str = f"{dist_val:+.2f}%"
            
            # إذا كان السعر يبعد أقل من 1.5% عن التكلفة
            if abs(dist_val) <= 1.5:
                tags.append("🎯 سعر الحوت")
                score += 3

        # 🛑 التطهير البصري: لا تعرض السهم إذا كان فارغاً من أي إشارة استخباراتية!
        if not tags:
            return None

        return {
            "الهدف 🦅": name,
            "الرمز": ticker.replace(".SR", ""),
            "السعر اللحظي": f"{curr_close:.2f}",
            "تكلفة الحوت 🐋": f"{vwap_10:.2f}" if vwap_10 > 0 else "-",
            "البُعد عن التكلفة 📏": dist_str,
            "الإشارات المخفية 🚨": " | ".join(tags),
            "_score": score,
            "_dist": abs(dist_val)
        }

    except Exception:
        return None

# ==========================================
# 🚀 إطلاق طائرات الاستطلاع (Multi-Threading)
# ==========================================
if st.button("📡 بدء المسح الاستخباراتي العميق للدارك بول الآن", use_container_width=True):
    start_time = time.time()
    
    progress_bar = st.progress(0, text="جاري إرسال العناكب البرمجية لاختراق السيرفرات ومسح السيولة المخفية... ⏳")
    
    results = []
    total_stocks = len(SAUDI_NAMES)
    processed = 0
    
    # الإعجاز العلمي: 20 طائرة استطلاع تضرب السوق في نفس اللحظة 
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(scan_whale_target, t, n): t for t, n in SAUDI_NAMES.items()}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            processed += 1
            progress_bar.progress(processed / total_stocks, text=f"تم مسح {processed} من {total_stocks} سهم...")
            res = future.result()
            if res:
                results.append(res)
                
    progress_bar.empty()
    end_time = time.time()
    
    # ==========================================
    # ⚔️ غرفة العمليات (عرض الغنائم)
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        
        # الإعجاز القتالي: ترتيب ذكي يضع السهم صاحب الأيقونات الأكثر والأقرب لتكلفة الحوت في القمة!
        df = df.sort_values(by=["_score", "_dist"], ascending=[False, True]).drop(columns=["_score", "_dist"])
        df.reset_index(drop=True, inplace=True)
        
        st.success(f"✅ اكتمل المسح في {round(end_time - start_time, 1)} ثانية فقط! تم رصد ({len(df)}) أهداف جاهزة للاقتحام.")
        
        # تلوين ذكي لعمود البعد عن التكلفة
        def color_distance(val):
            try:
                num = float(val.replace('%', ''))
                if abs(num) <= 1.5:
                    return 'color: #00FF41; font-weight: bold;'
                elif num < 0:
                    return 'color: #FF4B4B; font-weight: bold;'
                else:
                    return 'color: #FFA500;'
            except:
                return ''

        styled_df = df.style.map(color_distance, subset=['البُعد عن التكلفة 📏'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=450
        )
    else:
        st.warning("⚖️ الرادار صامت. لم يتم رصد أي تجميع مؤسساتي مخفي في الوقت الحالي. (أفضل صفقة الآن هي توفير الكاش).")

st.markdown("<hr><p style='text-align:center; color:#4B5563; font-size:12px;'>Engineered by Masa Chief Quant | V1.0 Stealth X-Ray | Multi-Threading Enabled</p>", unsafe_allow_html=True)
