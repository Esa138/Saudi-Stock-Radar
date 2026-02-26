import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures
import warnings
import time
import re

warnings.filterwarnings('ignore')

# ==========================================
# 🦅 إعدادات قمرة القيادة (الرادار الشبح V3.0 - التوسع العالمي)
# ==========================================
st.set_page_config(page_title="MASA X-RAY | رادار الحيتان العالمي", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #0A0E17; }
    .main-title { color: #00FF41; text-align: center; font-size: 50px; font-weight: 900; text-shadow: 0px 0px 20px rgba(0,255,65,0.5); margin-bottom: 5px; }
    .sub-title { color: #8B949E; text-align: center; font-size: 18px; margin-bottom: 20px; letter-spacing: 1px;}
    .legend-box { background: rgba(20, 24, 31, 0.9); border: 1px solid #30363D; border-right: 4px solid #00FF41; border-left: 4px solid #00FF41; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: 900 !important; font-size: 18px !important; border-radius: 8px !important; transition: all 0.3s ease; border: none; margin-top: 10px;}
    .stButton>button:hover { background-color: #00CC33 !important; transform: scale(1.02); box-shadow: 0 0 15px rgba(0,255,65,0.5); }
    
    /* 📻 أزرار اختيار السوق */
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background: #161B22; padding: 10px; border-radius: 10px; border: 1px solid #30363D; margin-bottom: 20px; }
    div.row-widget.stRadio > div > label { background-color: transparent !important; color: #FFF !important; font-size: 20px !important; font-weight: bold !important; padding: 0 20px !important; cursor: pointer; transition: 0.3s; }
    
    /* 🌊 إنذار الهجرة القطاعية */
    .neon-alert { background: linear-gradient(45deg, #4A0000, #8B0000); border: 2px solid #FF4B4B; box-shadow: 0 0 15px rgba(255, 75, 75, 0.4), inset 0 0 10px rgba(255, 75, 75, 0.2); color: #FFF; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: 900; margin-bottom: 25px; animation: pulse 2s infinite; }
    .neon-alert span { color: #FFD700; font-size: 28px; text-shadow: 0 0 10px rgba(255, 215, 0, 0.8); }
    @keyframes pulse { 0% { box-shadow: 0 0 10px rgba(255, 75, 75, 0.3); } 50% { box-shadow: 0 0 25px rgba(255, 75, 75, 0.7); } 100% { box-shadow: 0 0 10px rgba(255, 75, 75, 0.3); } }
    
    /* 🛠️ الجدول العسكري الكريستالي */
    .radar-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-family: 'Tajawal', sans-serif; background-color: #0D1117; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .radar-table thead { background-color: #161B22; border-bottom: 2px solid #00FF41; }
    .radar-table th { color: #8B949E; padding: 15px; font-size: 17px; text-align: center; font-weight: 700; }
    .radar-table td { padding: 15px; border-bottom: 1px solid #21262D; color: #E6EDF3; font-size: 19px; font-weight: bold; text-align: center; vertical-align: middle; }
    .radar-table tbody tr:hover { background-color: rgba(0, 255, 65, 0.05); }
    .target-name { color: #58A6FF !important; font-size: 20px !important; font-weight: 900 !important; }
    .target-name-us { color: #FF9900 !important; font-size: 20px !important; font-weight: 900 !important; font-family: monospace; }
    .sector-badge { font-size: 13px; color: #8B949E; display: block; margin-top: 5px; font-weight: normal; background: #21262D; border-radius: 4px; padding: 2px 5px; width: fit-content; margin-left: auto; margin-right: auto; }
    
    /* حماية الأرقام */
    .ltr-text { direction: ltr; display: inline-block; font-family: monospace; font-size: 19px; }
    .dist-green { color: #00FF41 !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    .dist-orange { color: #FFA500 !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    .dist-red { color: #FF4B4B !important; direction: ltr; display: inline-block; font-weight: 900; font-family: monospace; font-size: 19px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌍 MASA X-RAY V3.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Global Quant Engine | Wall Street & Tadawul Active</div>', unsafe_allow_html=True)

# ==========================================
# 🎛️ وحدة التحكم (تحديد مسرح العمليات)
# ==========================================
market_choice = st.radio("📡 تحديد النطاق الجغرافي للرادار:", ["السوق السعودي 🇸🇦 (TASI)", "السوق الأمريكي 🇺🇸 (Wall Street)"], horizontal=True)

is_us = "الأمريكي" in market_choice

st.markdown("""
<div class="legend-box">
    <strong style="color: #00FF41; font-size: 20px;">الأسلحة الخماسية (قواعد الاشتباك):</strong><br><br>
    <span style="font-size: 15px;">
    📦 <b>زنبرك مضغوط:</b> جفاف للسيولة.. انفجار وشيك. | 🧽 <b>ابتلاع مؤسساتي:</b> تداول فلكي بشمعة ضيقة. | 🎯 <b>مغناطيس التكلفة:</b> سعر الحوت (VWAP 10).<br>
    🪤 <b style="color:#FF4B4B;">مصيدة دِبَبَة:</b> ارتداد نيزكي ومصيدة وقف خسارة. | 🌊 <b style="color:#58A6FF;">الهجرة العظمى:</b> إنذار بتدفق السيولة لقطاع محدد.
    </span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📚 قواميس الأهداف (الذخيرة العالمية)
# ==========================================

SAUDI_NAMES = {
'1010.SR': 'الرياض', '1020.SR': 'الجزيرة', '1030.SR': 'الاستثمار', '1050.SR': 'السعودي الفرنسي', '1060.SR': 'الأول', '1080.SR': 'العربي', '1111.SR': 'تداول', '1120.SR': 'الراجحي', '1140.SR': 'البلاد', '1150.SR': 'الإنماء', '1180.SR': 'الأهلي', '1182.SR': 'أملاك', '1183.SR': 'سهل', '1833.SR': 'الموارد',
    '1201.SR': 'تكوين', '1202.SR': 'مبكو', '1211.SR': 'معادن', '1212.SR': 'أسترا الصناعية', '1213.SR': 'نسيج', '1214.SR': 'شاكر', '1301.SR': 'أسلاك', '1302.SR': 'بوان', '1303.SR': 'الصناعات الكهربائية', '1304.SR': 'اليمامة للحديد', '1320.SR': 'أنابيب السعودية', '1321.SR': 'أنابيب الشرق', '1322.SR': 'أنابيب',
    '2001.SR': 'كيمانول', '2010.SR': 'سابك', '2020.SR': 'المغذيات', '2030.SR': 'المصافي', '2040.SR': 'الخزف السعودي', '2050.SR': 'مجموعة صافولا', '2060.SR': 'التصنيع', '2070.SR': 'الدوائية', '2080.SR': 'الغاز', '2081.SR': 'الخريف', '2082.SR': 'أكوا باور', '2083.SR': 'مرافق',
    '2100.SR': 'وفرة', '2110.SR': 'الكابلات', '2120.SR': 'المتطورة', '2130.SR': 'صدق', '2140.SR': 'أميانتيت', '2150.SR': 'زجاج', '2170.SR': 'اللجين', '2180.SR': 'فيبكو', '2190.SR': 'سيسكو', '2200.SR': 'أنابيب', '2210.SR': 'نماء', '2220.SR': 'معدنية', '2222.SR': 'أرامكو', '2223.SR': 'لوبريف', '2230.SR': 'الكيميائية', '2240.SR': 'الزامل', '2250.SR': 'المجموعة السعودية', '2270.SR': 'سدافكو', '2280.SR': 'المراعي', '2281.SR': 'تنمية', '2282.SR': 'المطاحن الأولى', '2283.SR': 'المطاحن الحديثة', '2290.SR': 'ينساب', '2300.SR': 'صناعة الورق', '2310.SR': 'سبكيم', '2330.SR': 'المتقدمة', '2350.SR': 'كيان السعودية', '2360.SR': 'الفخارية', '2380.SR': 'بترورابغ',
    '3010.SR': 'أسمنت العربية', '3020.SR': 'أسمنت اليمامة', '3030.SR': 'أسمنت السعودية', '3040.SR': 'أسمنت القصيم', '3050.SR': 'أسمنت الجنوبية', '3060.SR': 'أسمنت ينبع', '3080.SR': 'أسمنت الشرقية', '3090.SR': 'أسمنت تبوك', '3091.SR': 'أسمنت الجوف', '3092.SR': 'أسمنت المدينة', '3021.SR': 'أسمنت أم القرى', '3022.SR': 'أسمنت الرياض',
    '4001.SR': 'أسواق العثيم', '4002.SR': 'المواساة', '4003.SR': 'إكسترا', '4004.SR': 'دله الصحية', '4005.SR': 'رعاية', '4007.SR': 'الحمادي', '4013.SR': 'سليمان الحبيب', '4014.SR': 'النهدي', '4015.SR': 'جمجوم فارما', '4020.SR': 'العقارية', '4030.SR': 'البحري', '4031.SR': 'مهارة', '4040.SR': 'سابتكو', '4050.SR': 'ساسكو', '4061.SR': 'أنعام القابضة', '4071.SR': 'العربية', '4081.SR': 'النايفات', '4090.SR': 'طيبة', '4100.SR': 'مكة', '4110.SR': 'باتك', '4130.SR': 'الباحة', '4140.SR': 'الصادرات', '4150.SR': 'التعمير', '4160.SR': 'ثمار', '4161.SR': 'بن داود', '4162.SR': 'المنجم', '4163.SR': 'الدواء', '4164.SR': 'أماك', '4165.SR': 'الماجد للعود', '4170.SR': 'شمس', '4180.SR': 'مجموعة فتيحي', '4190.SR': 'جرير', '4191.SR': 'أبو معطي', '4192.SR': 'عذيب', '4200.SR': 'الدريس', '4210.SR': 'الأبحاث والإعلام', '4220.SR': 'إعمار', '4230.SR': 'البحر الأحمر', '4240.SR': 'سينومي ريتيل', '4250.SR': 'جبل عمر', '4260.SR': 'بدجت', '4261.SR': 'ذيب', '4262.SR': 'لومي', '4280.SR': 'المملكة', '4290.SR': 'الخليج للتدريب', '4300.SR': 'دار الأركان', '4320.SR': 'الأندلس', '4321.SR': 'سينومي سنترز', '4322.SR': 'ريتال',
    '6004.SR': 'التموين', '6010.SR': 'نادك', '6012.SR': 'ريدان', '6013.SR': 'التطويرية الغذائية', '6014.SR': 'الآمار', '6015.SR': 'أمريكانا', '6020.SR': 'القصيم', '6040.SR': 'تبوك الزراعية', '6050.SR': 'الأسماك', '6060.SR': 'الشرقية للتنمية', '6070.SR': 'الجوف', '6090.SR': 'جازادكو',
    '7010.SR': 'STC', '7020.SR': 'موبايلي', '7030.SR': 'زين السعودية', '7040.SR': 'عذيب للاتصالات', '7200.SR': 'المعمر', '7202.SR': 'سلوشنز', '7203.SR': 'علم', '7204.SR': 'توبي',
    '8010.SR': 'التعاونية', '8012.SR': 'الجزيرة تكافل', '8020.SR': 'ملاذ للتأمين', '8030.SR': 'ميدغلف', '8040.SR': 'أليانز', '8050.SR': 'سلامة', '8060.SR': 'ولاء', '8070.SR': 'الدرع العربي', '8100.SR': 'سايكو', '8120.SR': 'اتحاد الخليج', '8150.SR': 'أسيج', '8160.SR': 'التأمين العربية', '8200.SR': 'إعادة', '8210.SR': 'بوبا', '8230.SR': 'تكافل الراجحي', '8240.SR': 'تشب', '8250.SR': 'عناية', '8260.SR': 'أمانة للتأمين', '8270.SR': 'بروج', '8280.SR': 'العالمية'
}

US_NAMES = {
    'AAPL': 'Apple', 'MSFT': 'Microsoft', 'NVDA': 'NVIDIA', 'GOOGL': 'Alphabet', 'AMZN': 'Amazon', 'META': 'Meta', 'TSLA': 'Tesla', 'SMCI': 'Super Micro', 'DELL': 'Dell Technologies',
    'AMD': 'AMD', 'AVGO': 'Broadcom', 'TSM': 'TSMC', 'MU': 'Micron', 'ASML': 'ASML Holding', 'ARM': 'ARM Holdings', 'LRCX': 'Lam Research', 'AMAT': 'Applied Materials', 'INTC': 'Intel', 'QCOM': 'Qualcomm', 'TXN': 'Texas Instruments', 'KLAC': 'KLA Corp', 'MRVL': 'Marvell', 'NXPI': 'NXP Semi',
    'CRM': 'Salesforce', 'ADBE': 'Adobe', 'ORCL': 'Oracle', 'NOW': 'ServiceNow', 'SNOW': 'Snowflake', 'PLTR': 'Palantir', 'DDOG': 'Datadog', 'MDB': 'MongoDB', 'TEAM': 'Atlassian', 'CDNS': 'Cadence Design', 'SNPS': 'Synopsys', 'SHOP': 'Shopify', 'UBER': 'Uber', 'NET': 'Cloudflare', 'CRWD': 'CrowdStrike', 'PANW': 'Palo Alto', 'FTNT': 'Fortinet', 'ZS': 'Zscaler', 'HUBS': 'HubSpot',
    'WMT': 'Walmart', 'HD': 'Home Depot', 'COST': 'Costco', 'MCD': 'McDonalds', 'SBUX': 'Starbucks', 'NKE': 'Nike', 'LULU': 'Lululemon', 'LOW': 'Lowe\'s', 'PG': 'Procter and Gamble', 'KO': 'Coca-Cola', 'PEP': 'PepsiCo', 'TGT': 'Target', 'CMG': 'Chipotle', 'TJX': 'TJX Companies',
    'LLY': 'Eli Lilly', 'JNJ': 'Johnson and Johnson', 'ABBV': 'AbbVie', 'MRK': 'Merck', 'PFE': 'Pfizer', 'ISRG': 'Intuitive Surg', 'VRTX': 'Vertex Pharma', 'REGN': 'Regeneron', 'AMGN': 'Amgen', 'GILD': 'Gilead Sciences', 'TMO': 'Thermo Fisher', 'DHR': 'Danaher', 'ABT': 'Abbott', 'SYK': 'Stryker', 'ZTS': 'Zoetis',
    'CAT': 'Caterpillar', 'BA': 'Boeing', 'GE': 'General Electric', 'XOM': 'Exxon Mobil', 'CVX': 'Chevron', 'SLB': 'Schlumberger', 'COP': 'ConocoPhillips', 'RIVN': 'Rivian', 'LCID': 'Lucid Motors', 'F': 'Ford', 'GM': 'General Motors', 'UNP': 'Union Pacific', 'UPS': 'UPS', 'FDX': 'FedEx', 'DE': 'Deere and Co', 'LMT': 'Lockheed Martin', 'RTX': 'RTX Corp', 'FSLR': 'First Solar', 'ENPH': 'Enphase Energy', 'NEE': 'NextEra Energy',
    'NFLX': 'Netflix', 'VZ': 'Verizon', 'T': 'AT and T', 'TMUS': 'T-Mobile', 'SPOT': 'Spotify', 'BKNG': 'Booking', 'ABNB': 'Airbnb',
    'COIN': 'Coinbase', 'MSTR': 'MicroStrategy', 'MARA': 'Marathon Digital', 'RIOT': 'Riot Platforms', 'CLSK': 'CleanSpark', 'HUT': 'Hut 8',
    'SPUS': 'S and P Sharia ETF', 'HLAL': 'Wahed FTSE Sharia ETF', 'UMMA': 'Wahed Dow Jones Islamic ETF', 'SPSK': 'SP Funds Sukuk ETF', 'SMH': 'Semiconductor ETF', 'SOXX': 'iShares Semi ETF', 'XLK': 'Technology ETF', 'XLV': 'Health Care ETF', 'XLE': 'Energy ETF', 'XLI': 'Industrial ETF'
}

# 🏢 محلل الشفرات الذكي للقطاعات (للسوقين)
def get_sector(ticker, is_us_market):
    if is_us_market:
        tech = ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NFLX', 'CRM', 'PLTR']
        semis = ['NVDA', 'AMD', 'TSM', 'AVGO', 'INTC', 'QCOM', 'SMCI', 'ARM', 'MU']
        crypto = ['COIN', 'MSTR', 'MARA', 'RIOT', 'HOOD', 'CLSK']
        finance = ['JPM', 'BAC', 'V', 'MA', 'GS', 'PYPL', 'SQ']
        health = ['LLY', 'NVO', 'UNH', 'JNJ', 'MRK', 'PFE']
        auto = ['TSLA', 'RIVN', 'LCID']
        retail = ['WMT', 'COST', 'DIS', 'NKE', 'UBER', 'ABNB', 'SBUX']
        industry = ['XOM', 'CVX', 'BA', 'CAT', 'GE', 'LMT']
        
        if ticker in tech: return 'التكنولوجيا والبرمجيات 💻'
        elif ticker in semis: return 'الذكاء الاصطناعي والرقائق 🧠'
        elif ticker in crypto: return 'الكريبتو والبلوكتشين ₿'
        elif ticker in finance: return 'البنوك والتمويل 🏦'
        elif ticker in health: return 'الرعاية الصحية 🏥'
        elif ticker in auto: return 'السيارات الكهربائية 🚗'
        elif ticker in retail: return 'التجزئة والترفيه 🛒'
        elif ticker in industry: return 'الطاقة والصناعة 🛢️'
        else: return 'قطاعات أمريكية 🇺🇸'
    else:
        code = str(ticker).replace('.SR', '')
        if code.startswith('1'): return 'البنوك والتمويل 🏦'
        elif code in ['2222', '2082', '4030', '4200']: return 'الطاقة والمرافق ⚡'
        elif code.startswith('2'): return 'المواد الأساسية 🛢️'
        elif code.startswith('3'): return 'الأسمنت 🏗️'
        elif code.startswith('43') or code in ['4100', '4150', '4220', '4250']: return 'العقارات 🏢'
        elif code.startswith('400') or code.startswith('41') or code.startswith('42'): return 'التجزئة والخدمات 🛒'
        elif code.startswith('401') or code == '8210': return 'الرعاية الصحية 🏥'
        elif code.startswith('6'): return 'الأغذية والزراعة 🌾'
        elif code.startswith('7'): return 'الاتصالات والتقنية 📡'
        elif code.startswith('8'): return 'التأمين 🛡️'
        else: return 'قطاعات أخرى 📊'

# ==========================================
# 🧠 المحرك الكمّي الخارق (X-Ray Core V3)
# ==========================================
def scan_whale_target(ticker, raw_name, is_us_market):
    try:
        clean_name = re.sub(r'^\d+[:\s-]*', '', raw_name).strip()
        sector_name = get_sector(ticker, is_us_market)
        
        display_ticker = ticker if is_us_market else ticker.replace(".SR", "")
        currency = "$" if is_us_market else ""

        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if df.empty or len(df) < 20:
            return None

        curr_open = float(df['Open'].iloc[-1])
        curr_close = float(df['Close'].iloc[-1])
        curr_high = float(df['High'].iloc[-1])
        curr_low = float(df['Low'].iloc[-1])
        curr_vol = float(df['Volume'].iloc[-1])
        
        curr_spread = curr_high - curr_low

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
            
        if curr_spread > 0:
            lower_wick = min(curr_open, curr_close) - curr_low
            wick_ratio = lower_wick / curr_spread
            if wick_ratio >= 0.55 and curr_close > (curr_low + (curr_spread * 0.4)) and curr_vol > (avg_vol_20 * 1.2):
                tags.append("🪤 مصيدة دِبَبَة")
                score += 4 

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
            "ticker": display_ticker,
            "sector": sector_name,
            "price": f"{currency}{curr_close:.2f}",
            "vwap": f"{currency}{vwap_10:.2f}" if vwap_10 > 0 else "-",
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
active_dict = US_NAMES if is_us else SAUDI_NAMES
market_title = "وول ستريت 🇺🇸" if is_us else "تاسي 🇸🇦"

if st.button(f"📡 بدء المسح الاستخباراتي المزدوج لـ ({market_title}) الآن", use_container_width=True):
    start_time = time.time()
    
    progress_bar = st.progress(0, text=f"جاري توجيه الرادار نحو {market_title} ومسح السيولة المخفية... ⏳")
    
    results = []
    total_stocks = len(active_dict)
    processed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(scan_whale_target, t, n, is_us): t for t, n in active_dict.items()}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            processed += 1
            progress_bar.progress(processed / total_stocks, text=f"تم مسح {processed} من {total_stocks} سهم...")
            res = future.result()
            if res:
                results.append(res)
                
    progress_bar.empty()
    end_time = time.time()
    
    # ==========================================
    # ⚔️ عرض الغنائم
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        
        # 🌊 الهجرة العظمى
        if not df.empty:
            sector_scores = df.groupby('sector')['score'].sum()
            total_market_score = sector_scores.sum()
            
            if total_market_score > 0:
                top_sector = sector_scores.idxmax()
                top_score = sector_scores.max()
                concentration = (top_score / total_market_score) * 100
                sector_counts = df[df['sector'] == top_sector].shape[0]
                
                if concentration >= 30 and sector_counts >= 2 and top_sector not in ['قطاعات أخرى 📊', 'قطاعات أمريكية 🇺🇸']:
                    st.markdown(f'<div class="neon-alert">🚨 إنذار استخباراتي: تيار الحيتان يهاجر بقوة ويتركز الآن في <span>[ {top_sector} ]</span> بنسبة {concentration:.0f}% من الزخم! 🚨</div>', unsafe_allow_html=True)
        
        df = df.sort_values(by=["score", "abs_dist"], ascending=[False, True])
        
        st.success(f"✅ اكتمل مسح {market_title} في {round(end_time - start_time, 1)} ثانية! تم رصد ({len(df)}) أهداف استراتيجية.")
        
        # 💎 الجدول الكريستالي
        html_table = '<table class="radar-table">'
        html_table += '<thead><tr><th>الهدف 🦅</th><th>الرمز</th><th>السعر اللحظي</th><th>تكلفة الحوت 🐋</th><th>البُعد عن التكلفة 📏</th><th>الإشارات المخفية 🚨</th></tr></thead><tbody>'
        
        name_class = 'target-name-us' if is_us else 'target-name'

        for _, row in df.iterrows():
            num = float(row['dist_val'])
            if abs(num) <= 1.5: color_class = "dist-green"
            elif num < 0: color_class = "dist-red"
            else: color_class = "dist-orange"
                
            html_table += "<tr>"
            html_table += f"<td><span class='{name_class}'>{row['name']}</span><span class='sector-badge'>{row['sector']}</span></td>"
            html_table += f"<td><span class='ltr-text'>{row['ticker']}</span></td>"
            html_table += f"<td><span class='ltr-text'>{row['price']}</span></td>"
            html_table += f"<td><span class='ltr-text'>{row['vwap']}</span></td>"
            html_table += f"<td><span class='{color_class}'>{row['dist_str']}</span></td>"
            html_table += f"<td style='font-size: 20px; letter-spacing: 1px;'>{row['tags']}</td>"
            html_table += "</tr>"
            
        html_table += '</tbody></table>'
        
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.warning(f"⚖️ الرادار صامت في {market_title} حالياً. لم يتم رصد أي تجميع مؤسساتي مخفي أو مصائد دببة.")

st.markdown("<hr><p style='text-align:center; color:#4B5563; font-size:12px;'>Engineered by Masa Chief Quant | V3.0 Global Edition | Wall Street & TASI</p>", unsafe_allow_html=True)
