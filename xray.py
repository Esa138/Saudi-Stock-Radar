import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures
import warnings
import time
import re

warnings.filterwarnings('ignore')

# ==========================================
# 🦅 إعدادات قمرة القيادة (الرادار الشبح V1.1)
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
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: 900 !important; font-size: 18px !important; border-radius: 8px !important; transition: all 0.3s ease; border: none; }
    .stButton>button:hover { background-color: #00CC33 !important; transform: scale(1.02); }
    
    /* 🛠️ التصميم العسكري الجديد للجدول - وضوح 4K للأرقام */
    .radar-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-family: 'Tajawal', sans-serif; background-color: #0D1117; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .radar-table thead { background-color: #161B22; border-bottom: 2px solid #00FF41; }
    .radar-table th { color: #8B949E; padding: 15px; font-size: 17px; text-align: center; font-weight: 700; }
    .radar-table td { padding: 15px; border-bottom: 1px solid #21262D; color: #E6EDF3; font-size: 19px; font-weight: bold; text-align: center; }
    .radar-table tbody tr:hover { background-color: rgba(0, 255, 65, 0.05); }
    .target-name { color: #58A6FF !important; font-size: 20px !important; font-weight: 900 !important; }
    
    /* درع حماية الأرقام من القص والتشوه */
    .ltr-text { direction: ltr; display: inline-block; font-family: monospace; font-size: 19px; }
    .dist-green { color: #00FF41 !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    .dist-orange { color: #FFA500 !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    .dist-red { color: #FF4B4B !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">👁️‍🗨️ MASA X-RAY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">طائرة الاستطلاع الشبحية | Zero-Latency Quant Engine | HD Vision Patch</div>', unsafe_allow_html=True)

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

# ذخيرة الرادار النظيفة (أهم 85 سهم في السوق السعودي - مبرمجة وجاهزة)
SAUDI_NAMES = {
    '1120.SR': 'الراجحي', '1180.SR': 'الأهلي', '1010.SR': 'الرياض', '1050.SR': 'السعودي الفرنسي', 
    '1060.SR': 'الأول', '1020.SR': 'الجزيرة', '1030.SR': 'الاستثمار', '1080.SR': 'العربي', 
    '1140.SR': 'البلاد', '1150.SR': 'الإنماء', '1182.SR': 'أملاك', '1183.SR': 'سهل', 
    '1111.SR': 'تداول', '2222.SR': 'أرامكو', '2010.SR': 'سابك', '2020.SR': 'المغذيات', 
    '2060.SR': 'التصنيع', '2350.SR': 'كيان', '2001.SR': 'كيمانول', '2250.SR': 'المجموعة السعودية', 
    '2310.SR': 'سبكيم', '2082.SR': 'أكوا باور', '7010.SR': 'stc', '7020.SR': 'موبايلي', 
    '7030.SR': 'زين السعودية', '2280.SR': 'المراعي', '2281.SR': 'تنمية', '6010.SR': 'نادك', 
    '6040.SR': 'تبوك الزراعية', '6060.SR': 'الشرقية للتنمية', '6070.SR': 'الجوف', '4160.SR': 'ثمار', 
    '4164.SR': 'النهدي', '4013.SR': 'سليمان الحبيب', '4015.SR': 'جمجوم فارما', '4002.SR': 'المواساة', 
    '4003.SR': 'إكسترا', '4190.SR': 'جرير', '4200.SR': 'الدريس', '4142.SR': 'الماجد للعود', 
    '4321.SR': 'المراكز', '4300.SR': 'دار الأركان', '4220.SR': 'إعمار', '4322.SR': 'ريتال', 
    '7202.SR': 'سلوشنز', '7203.SR': 'علم', '7204.SR': 'توبي', '8210.SR': 'بوبا', 
    '8010.SR': 'التعاونية', '8012.SR': 'الجزيرة تكافل', '8030.SR': 'ميدغلف', '8040.SR': 'أليانز', 
    '3030.SR': 'أسمنت السعودية', '3040.SR': 'أسمنت القصيم', '3050.SR': 'أسمنت الجنوبية', 
    '3060.SR': 'أسمنت ينبع', '3080.SR': 'أسمنت الشرقية', '3090.SR': 'أسمنت تبوك', '2120.SR': 'المتطورة', 
    '2140.SR': 'إيان', '2150.SR': 'زجاج', '2170.SR': 'اللجين', '2180.SR': 'فيبكو', 
    '2190.SR': 'سيسكو', '2200.SR': 'أنابيب', '2210.SR': 'نماء', '2230.SR': 'الكيميائية', 
    '2360.SR': 'الفخارية', '4030.SR': 'البحري', '4040.SR': 'جماعي', '4110.SR': 'باتك', 
    '4130.SR': 'الباحة', '4140.SR': 'الصادرات', '4050.SR': 'ساسكو', '4100.SR': 'مكة', '4250.SR': 'جبل عمر',
    '4280.SR': 'المملكة', '4230.SR': 'البحر الأحمر', '4150.SR': 'التعمير', '4240.SR': 'سينومي ريت'
}

# ==========================================
# 🧠 المحرك الكمّي الخارق (X-Ray Core)
# ==========================================
def scan_whale_target(ticker, raw_name):
    try:
        # 🧹 الغسالة التلقائية: إزالة أي أرقام التصقت بالاسم بالخطأ
        clean_name = re.sub(r'^\d+[:\s-]*', '', raw_name).strip()

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
        
        if avg_vol_3 < (avg_vol_20 * 0.6) and avg_spread_3 < (avg_spread_20 * 0.6):
            tags.append("📦 مضغوط")
            score += 1

        if curr_vol > (avg_vol_20 * 1.5) and curr_spread < (avg_spread_20 * 0.8):
            tags.append("🧽 ابتلاع")
            score += 2

        last_10 = df.tail(10)
        sum_vol_10 = float(last_10['Volume'].sum())
        dist_str = "-"
        dist_val = 999.0
        vwap_10 = 0.0
        
        if sum_vol_10 > 0:
            typical_price = (last_10['High'] + last_10['Low'] + last_10['Close']) / 3
            vwap_10 = float((typical_price * last_10['Volume']).sum() / sum_vol_10)
            
            dist_val = ((curr_close - vwap_10) / vwap_10) * 100
            dist_str = f"{dist_val:+.2f}%"
            
            if abs(dist_val) <= 1.5:
                tags.append("🎯 سعر الحوت")
                score += 3

        if not tags:
            return None

        return {
            "name": clean_name,
            "ticker": ticker.replace(".SR", ""),
            "price": f"{curr_close:.2f}",
            "vwap": f"{vwap_10:.2f}" if vwap_10 > 0 else "-",
            "dist_str": dist_str,
            "dist_val": dist_val,
            "tags": " | ".join(tags),
            "score": score,
            "abs_dist": abs(dist_val)
        }

    except Exception:
        return None

# ==========================================
# 🚀 إطلاق طائرات الاستطلاع
# ==========================================
if st.button("📡 بدء المسح الاستخباراتي العميق للدارك بول الآن", use_container_width=True):
    start_time = time.time()
    
    progress_bar = st.progress(0, text="جاري إرسال العناكب البرمجية لاختراق السيرفرات ومسح السيولة المخفية... ⏳")
    
    results = []
    total_stocks = len(SAUDI_NAMES)
    processed = 0
    
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
    # ⚔️ بناء الجدول الكريستالي المخصص (HTML/CSS)
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by=["score", "abs_dist"], ascending=[False, True])
        
        st.success(f"✅ اكتمل المسح في {round(end_time - start_time, 1)} ثانية فقط! تم رصد ({len(df)}) أهداف جاهزة للاقتحام.")
        
        # 💎 الإعجاز البصري: بناء جدول HTML لا يمكن قص أرقامه
        html_table = '<table class="radar-table">'
        html_table += '<thead><tr><th>الهدف 🦅</th><th>الرمز</th><th>السعر اللحظي</th><th>تكلفة الحوت 🐋</th><th>البُعد عن التكلفة 📏</th><th>الإشارات المخفية 🚨</th></tr></thead><tbody>'
        
        for _, row in df.iterrows():
            num = float(row['dist_val'])
            if abs(num) <= 1.5:
                color_class = "dist-green"
            elif num < 0:
                color_class = "dist-red"
            else:
                color_class = "dist-orange"
                
            html_table += "<tr>"
            html_table += f"<td class='target-name'>{row['name']}</td>"
            html_table += f"<td><span class='ltr-text'>{row['ticker']}</span></td>"
            html_table += f"<td><span class='ltr-text'>{row['price']}</span></td>"
            html_table += f"<td><span class='ltr-text'>{row['vwap']}</span></td>"
            html_table += f"<td><span class='{color_class}'>{row['dist_str']}</span></td>"
            html_table += f"<td style='font-size: 22px;'>{row['tags']}</td>"
            html_table += "</tr>"
            
        html_table += '</tbody></table>'
        
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.warning("⚖️ الرادار صامت. لم يتم رصد أي تجميع مؤسساتي مخفي في الوقت الحالي.")

st.markdown("<hr><p style='text-align:center; color:#4B5563; font-size:12px;'>Engineered by Masa Chief Quant | V1.1 HD Vision | Custom HTML Grid</p>", unsafe_allow_html=True)
