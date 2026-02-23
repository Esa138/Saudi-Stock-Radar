import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import datetime
import os
import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# ==========================================
# 💎 1. إعدادات الهوية وقاعدة البيانات
# ==========================================
st.set_page_config(page_title="منصة ماسة 💎 | V83 Force Sync", layout="wide", page_icon="⚡")

DB_FILE = "masa_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracker 
                 (date_time TEXT, market TEXT, ticker TEXT, company TEXT, 
                  entry REAL, target REAL, stop_loss REAL, score TEXT, mom TEXT, date_only TEXT)''')
    conn.commit()
    conn.close()

init_db()

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
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
.empty-box { text-align:center; padding:15px; background-color:#1e2129; border-radius:8px; color:#888; margin-bottom:15px; font-size:15px; border: 1px dashed #2d303e;}

/* 🧠 تصميم الذكاء الاصطناعي (X-Ray) */
.ai-box { background: linear-gradient(145deg, #12141a, #1a1c24); border-top: 4px solid #00d2ff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(0,210,255,0.15);}
.ai-table { width: 100%; text-align: center; border-collapse: collapse; margin-top: 10px; background-color: #1e2129; border-radius: 8px; overflow: hidden;}
.ai-table th { background-color: #2d303e; color: white; padding: 12px; font-size: 14px;}
.ai-table td { padding: 12px; border-bottom: 1px solid #2d303e; font-size: 14px; vertical-align: middle; font-weight:bold;}
.bo-badge { font-weight: bold; padding: 4px 10px; border-radius: 6px; font-size: 12px; display: inline-block; white-space: nowrap; margin: 2px;}
.target-text { color: #00E676; font-weight: bold; font-size: 14px; }
.sl-text { color: #FF5252; font-weight: bold; font-size: 14px; }
.rec-badge { font-weight:900; font-size:14px; padding:6px 12px; border-radius:8px;}

/* 🧲 تصميم جداول الحيتان */
.whale-table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3);}
.whale-table th { color: white; padding: 12px; font-weight: 900; }
.whale-table td { padding: 12px; border-bottom: 1px solid #2d303e; color: white; font-weight: bold;}
.whale-acc th { background-color: rgba(0, 230, 118, 0.2); border-bottom: 2px solid #00E676; color: #00E676;}
.whale-dist th { background-color: rgba(255, 82, 82, 0.2); border-bottom: 2px solid #FF5252; color: #FF5252;}

/* 👑 تصميم VIP ماسة المطور */
.vip-container { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-top: 20px; margin-bottom: 30px; }
.vip-card { background: linear-gradient(135deg, #2b2302 0%, #1a1c24 100%); border: 1px solid #ffd700; border-top: 4px solid #ffd700; padding: 25px 20px; border-radius: 15px; width: 31%; min-width: 280px; box-shadow: 0 10px 20px rgba(255, 215, 0, 0.1); transition: transform 0.3s ease; text-align: center; position: relative; overflow: hidden;}
.vip-card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(255, 215, 0, 0.25); }
.vip-crown { position: absolute; top: -15px; right: -15px; font-size: 60px; transform: rotate(15deg); opacity: 0.1; }
.vip-title { color: #ffd700; font-size: 26px; font-weight: 900; margin-bottom: 5px; }
.vip-time { font-size: 13px; color: #aaa; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; display: inline-block; border: 1px solid rgba(255,255,255,0.1);}
.vip-rr { font-size: 13px; color: #00d2ff; background-color: rgba(0, 210, 255, 0.1); border: 1px dashed #00d2ff; padding: 4px 10px; border-radius: 4px; display: inline-block; margin-bottom: 15px; font-weight: bold;}
.vip-price { font-size: 32px; color: white; font-weight: bold; margin-bottom: 15px; }
.vip-details { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 15px; background: rgba(0,0,0,0.4); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 215, 0, 0.2);}
.vip-target { color: #00e676; font-weight: 900; font-size: 18px;}
.vip-stop { color: #ff5252; font-weight: 900; font-size: 18px;}
.vip-score { background: #ffd700; color: black; padding: 8px 20px; border-radius: 20px; font-weight: 900; font-size: 18px; display: inline-block; margin-top: 15px; box-shadow: 0 4px 10px rgba(255, 215, 0, 0.4);}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

masa_logo_html = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 5px; margin-top: -10px;">
    <svg width="90" height="90" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="neonBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00d2ff" />
                <stop offset="100%" stop-color="#3a7bd5" />
            </linearGradient>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffd700" />
                <stop offset="100%" stop-color="#ffaa00" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>
        <path d="M 50,5 L 90,35 L 50,95 L 10,35 Z" fill="rgba(0, 210, 255, 0.05)" stroke="url(#neonBlue)" stroke-width="2.5" filter="url(#glow)" stroke-linejoin="round"/>
        <path d="M 20,35 L 50,60 L 80,35" fill="none" stroke="url(#neonBlue)" stroke-width="2" opacity="0.6" stroke-linejoin="round"/>
        <path d="M 50,5 L 50,60" fill="none" stroke="url(#neonBlue)" stroke-width="2" opacity="0.6"/>
        <path d="M 30,75 L 75,25 M 55,25 L 75,25 L 75,45" fill="none" stroke="url(#goldGrad)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
    </svg>
    <div style="font-family: 'Arial', sans-serif; text-align: center; margin-top: 15px; line-height: 1;">
        <span style="font-size: 42px; font-weight: 900; letter-spacing: 5px; color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.1);">MASA</span>
        <span style="font-size: 42px; font-weight: 300; letter-spacing: 5px; color: #00d2ff; text-shadow: 0 0 15px rgba(0,210,255,0.4);"> QUANT</span>
    </div>
    <div style="color: #888; font-size: 13px; letter-spacing: 3px; font-weight: bold; margin-top: 8px;">
        INSTITUTIONAL ALGORITHMIC TRADING <span style="color:#ffd700">V83 (FORCE SYNC ⚡)</span>
    </div>
</div>
"""
st.markdown(masa_logo_html, unsafe_allow_html=True)

clock_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
body { margin: 0; padding: 0; background-color: transparent; display: flex; justify-content: center; align-items: center; height: 100%; font-family: 'Tajawal', sans-serif;}
.clock-wrapper { background: linear-gradient(145deg, #15171e, #1a1c24); border: 1px solid #2d303e; padding: 8px 25px; border-radius: 50px; box-shadow: 0 4px 15px rgba(0, 210, 255, 0.1); color: #aaa; font-size: 15px; font-weight: bold; display: flex; align-items: center; gap: 10px; border-bottom: 2px solid #00d2ff;}
.time-pulse { color: #00d2ff; font-size: 18px; letter-spacing: 2px; font-family: 'Courier New', monospace; text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);}
.date-text { color: #e0e0e0;}
</style>
<div class="clock-wrapper" dir="rtl">
    <span>🕋 توقيت مكة (24H):</span>
    <span class="time-pulse" id="live-time">--:--:--</span>
    <span class="date-text" id="live-date"></span>
</div>
<script>
    function updateClock() {
        let now = new Date();
        let timeOpts = { timeZone: 'Asia/Riyadh', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
        let dateOpts = { timeZone: 'Asia/Riyadh', year: 'numeric', month: 'short', day: 'numeric' };
        document.getElementById('live-time').innerText = now.toLocaleTimeString('en-GB', timeOpts);
        document.getElementById('live-date').innerText = ' | ' + now.toLocaleDateString('ar-SA', dateOpts);
    }
    setInterval(updateClock, 1000);
    updateClock();
</script>
"""
components.html(clock_html, height=55)
st.markdown("<br>", unsafe_allow_html=True)

saudi_tz = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(saudi_tz)
today_str = now.strftime("%Y-%m-%d")

if 'tg_sent' not in st.session_state:
    st.session_state.tg_sent = set()

with st.expander("⚙️ لوحة التحكم والإعدادات (المحفظة وتليجرام)", expanded=False):
    c_set1, c_set2 = st.columns(2)
    with c_set1:
        st.markdown("<h4 style='color:#00d2ff; text-align:right;'>⚙️ إدارة المخاطر</h4>", unsafe_allow_html=True)
        capital = st.number_input("💵 حجم المحفظة الكلي:", min_value=1000.0, value=100000.0, step=1000.0)
        risk_pct = st.number_input("⚖️ نسبة المخاطرة للصفقة (%):", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    with c_set2:
        st.markdown("<h4 style='color:#00E676; text-align:right;'>🤖 إشعارات التليجرام</h4>", unsafe_allow_html=True)
        tg_token = st.text_input("Bot Token (الصق توكن الروبوت هنا)", type="password")
        tg_chat = st.text_input("Chat ID (الصق رقم غرفتك هنا)")

# ==========================================
# 🌍 2. قوائم الأسواق الشاملة
# ==========================================
SAUDI_NAMES = {
    '1010.SR': 'الرياض', '1020.SR': 'الجزيرة', '1030.SR': 'الاستثمار', '1050.SR': 'السعودي الفرنسي', '1060.SR': 'الأول', '1080.SR': 'العربي', '1111.SR': 'تداول', '1120.SR': 'الراجحي', '1140.SR': 'البلاد', '1150.SR': 'الإنماء', '1180.SR': 'الأهلي', '1182.SR': 'أملاك', '1183.SR': 'الموارد',
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
    'AAPL': 'Apple', 'MSFT': 'Microsoft', 'NVDA': 'NVIDIA', 'GOOGL': 'Alphabet', 'AMZN': 'Amazon', 'META': 'Meta', 'TSLA': 'Tesla', 'AMD': 'AMD', 'AVGO': 'Broadcom', 'TSM': 'TSMC', 'CRM': 'Salesforce', 'NFLX': 'Netflix', 'INTC': 'Intel', 'CSCO': 'Cisco', 'QCOM': 'Qualcomm',
    'PLTR': 'Palantir', 'SNOW': 'Snowflake', 'CRWD': 'CrowdStrike', 'DDOG': 'Datadog', 'NET': 'Cloudflare', 'NOW': 'ServiceNow', 'PANW': 'Palo Alto', 'SHOP': 'Shopify', 'SQ': 'Block', 'UBER': 'Uber', 'TEAM': 'Atlassian', 'MDB': 'MongoDB', 'ZS': 'Zscaler',
    'COIN': 'Coinbase', 'MSTR': 'MicroStrategy', 'MARA': 'Marathon', 'RIOT': 'Riot Platforms', 'HOOD': 'Robinhood',
    'V': 'Visa', 'MA': 'Mastercard', 'JPM': 'JPMorgan', 'BAC': 'Bank of America', 'GS': 'Goldman Sachs', 'MS': 'Morgan Stanley', 'PYPL': 'PayPal', 'C': 'Citigroup', 'WFC': 'Wells Fargo',
    'WMT': 'Walmart', 'HD': 'Home Depot', 'COST': 'Costco', 'SBUX': 'Starbucks', 'NKE': 'Nike', 'MCD': 'McDonalds', 'PG': 'Procter & Gamble', 'KO': 'Coca-Cola', 'PEP': 'PepsiCo',
    'LLY': 'Eli Lilly', 'UNH': 'UnitedHealth', 'JNJ': 'Johnson & Johnson', 'ABBV': 'AbbVie', 'MRK': 'Merck', 'PFE': 'Pfizer', 'ISRG': 'Intuitive Surg',
    'XOM': 'Exxon Mobil', 'CVX': 'Chevron', 'BA': 'Boeing', 'CAT': 'Caterpillar', 'GE': 'General Electric', 'DIS': 'Disney', 'VZ': 'Verizon', 'T': 'AT&T',
    'SPY': 'S&P 500 ETF', 'QQQ': 'Nasdaq ETF', 'DIA': 'Dow Jones ETF', 'IWM': 'Russell 2000 ETF', 'ARKK': 'ARK Innovation', 'SMH': 'Semiconductor ETF', 'SOXX': 'iShares Semi ETF', 'XLF': 'Financial ETF', 'XLV': 'Health Care ETF', 'XLE': 'Energy ETF', 'TQQQ': 'ProShares Ultra QQQ'
}
FX_NAMES = {
    'EURUSD=X': 'EUR/USD', 'JPY=X': 'USD/JPY', 'GBPUSD=X': 'GBP/USD', 'CHF=X': 'USD/CHF', 'AUDUSD=X': 'AUD/USD',
    'CAD=X': 'USD/CAD', 'NZDUSD=X': 'NZD/USD', 'EURGBP=X': 'EUR/GBP', 'EURJPY=X': 'EUR/JPY', 'GBPJPY=X': 'GBP/JPY'
}
CRYPTO_NAMES = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana', 'BNB-USD': 'BNB', 'XRP-USD': 'XRP',
    'ADA-USD': 'Cardano', 'AVAX-USD': 'Avalanche', 'LINK-USD': 'Chainlink', 'DOGE-USD': 'Dogecoin', 'DOT-USD': 'Polkadot'
}

def get_stock_name(ticker):
    if ticker in SAUDI_NAMES: return SAUDI_NAMES[ticker]
    if ticker in US_NAMES: return US_NAMES[ticker]
    if ticker in FX_NAMES: return FX_NAMES[ticker]
    if ticker in CRYPTO_NAMES: return CRYPTO_NAMES[ticker]
    return ticker.replace('.SR', '').replace('=X', '').replace('-USD', '')

def format_price(val, ticker):
    if pd.isna(val): return "0.00"
    try:
        v = float(val)
        if "=X" in str(ticker): return f"{v:.3f}" if "JPY" in str(ticker) else f"{v:.5f}"
        elif "-USD" in str(ticker): return f"{v:.5f}" if v < 2 else f"{v:.3f}" if v < 50 else f"{v:.2f}"
        else: return f"{v:.2f}"
    except: return str(val)

def localize_timezone(df):
    if df is None or df.empty: return df
    try:
        if isinstance(df.index, pd.DatetimeIndex):
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC').tz_convert('Asia/Riyadh').tz_localize(None)
            else:
                df.index = df.index.tz_convert('Asia/Riyadh').tz_localize(None)
    except Exception: pass
    return df

@st.cache_data(ttl=1800, show_spinner=False)
def get_macro_status(market_choice):
    if "السعودي" in market_choice: ticker, name = "^TASI.SR", "تاسي (TASI)"
    elif "الأمريكي" in market_choice: ticker, name = "^GSPC", "إس آند بي (S&P 500)"
    elif "الفوركس" in market_choice: ticker, name = "DX-Y.NYB", "مؤشر الدولار (DXY)"
    else: ticker, name = "BTC-USD", "البيتكوين (BTC)"
    try:
        df = yf.Ticker(ticker).history(period="6mo", interval="1d")
        if df is None or df.empty: return "تذبذب ⛅", name, 0.0, 0.0
        c = df['Close']
        ma50 = c.rolling(50).mean().iloc[-1]
        if pd.isna(ma50): ma50 = c.mean()
        last_c = c.iloc[-1]
        prev_c = c.iloc[-2] if len(c) > 1 else last_c
        pct_change = ((last_c - prev_c) / prev_c) * 100 if prev_c != 0 else 0
        if "الفوركس" in market_choice: status = "سوق لامركزي 💱"
        else:
            if last_c > ma50: status = "إيجابي ☀️"
            elif last_c < ma50: status = "سلبي ⛈️"
            else: status = "تذبذب ⛅"
        return status, name, pct_change, last_c
    except Exception: return "تذبذب ⛅", name, 0.0, 0.0

def save_to_tracker_sql(df_vip, market):
    if df_vip.empty: return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for _, row in df_vip.iterrows():
        date_time = str(row['raw_time']).replace('⏱️ ', '')
        date_only = date_time.split(' | ')[1] if ' | ' in date_time else date_time
        ticker = str(row['الرمز'])
        c.execute("SELECT 1 FROM tracker WHERE date_only=? AND ticker=?", (date_only, ticker))
        if not c.fetchone():
            c.execute('''INSERT INTO tracker (date_time, market, ticker, company, entry, target, stop_loss, score, mom, date_only)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (date_time, market, ticker, str(row['الشركة']), float(row['raw_price']), float(row['raw_target']), float(row['raw_sl']), str(row['raw_score']), str(row['raw_mom']), date_only))
    conn.commit()
    conn.close()
    return True

def calc_momentum_score(pct_1d, pct_5d, pct_10d, vol_ratio):
    def get_points(val, weights):
        if pd.isna(val) or val == 0: return weights[3]
        abs_val = abs(val)
        if val > 0:
            if abs_val >= 1.0: return weights[0]
            elif abs_val >= 0.1: return weights[1]
            else: return weights[2]
        else:
            if abs_val >= 1.0: return weights[6]
            elif abs_val >= 0.1: return weights[5]
            else: return weights[4]
    s5 = get_points(pct_5d, [40, 35, 28, 20, 12, 6, 0])
    s10 = get_points(pct_10d, [25, 22, 18, 12, 8, 4, 0])
    s1 = get_points(pct_1d, [15, 13, 10, 7, 4, 2, 0])
    if pd.isna(pct_1d) or pct_1d == 0: svol = 10
    elif pct_1d > 0: svol = 20 if vol_ratio > 1.0 else 16
    else: svol = 6 if vol_ratio <= 1.0 else 0
    return min(100, max(0, s5 + s10 + s1 + svol))

def get_mom_badge(score):
    if score >= 75: return f"<span style='background-color:rgba(0,230,118,0.2); color:#00E676; padding: 4px 8px; border-radius:6px; border:1px solid #00E676; font-weight:bold;'>{score} 🔥</span>"
    elif score >= 50: return f"<span style='background-color:rgba(255,215,0,0.2); color:#FFD700; padding: 4px 8px; border-radius:6px; border:1px solid #FFD700; font-weight:bold;'>{score} ⚡</span>"
    else: return f"<span style='background-color:rgba(255,82,82,0.2); color:#FF5252; padding: 4px 8px; border-radius:6px; border:1px solid #FF5252; font-weight:bold;'>{score} ❄️</span>"

def get_ai_analysis(last_close, ma50, ma200, rsi, counter, zr_low, zr_high, event_text, bo_score_add, mom_score, vol_accel_ratio, pct_1d, macro_status, is_forex, is_crypto, last_vwap, rr_ratio, daily_trend, interval):
    if pd.isna(ma50) or pd.isna(ma200): return 0, "انتظار ⏳", "gray", ["بيانات غير كافية للتحليل."]
    tech_score = 50
    reasons = []
    
    is_macro_bull_stock = last_close > ma200
    is_micro_bull = last_close > ma50
    is_bleeding = counter < 0 or "كسر" in event_text or "سلبي" in event_text or "تصحيح" in event_text or "هابط" in event_text or "🕳️" in event_text
    dist_ma50 = ((last_close - ma50) / ma50) * 100 if is_micro_bull else ((ma50 - last_close) / ma50) * 100
    
    veto_max_59 = False; veto_max_79 = False; golden_watch = False
    
    is_zero_breakout = "زيرو 👑" in event_text or "سماء 🌌" in event_text
    is_zero_breakdown = "كسر زيرو 🩸" in event_text or "انهيار سحيق 🕳️" in event_text or "سقوط 🩸" in event_text
    is_blue_sky = pd.notna(zr_high) and last_close > zr_high
    is_zero_bottom = pd.notna(zr_low) and last_close <= zr_low * 1.05

    macro_reason = ""
    is_absolute_lockdown = False

    mtf_reason = ""
    is_mtf_veto = False
    if interval != "1d":
        if daily_trend == "هابط ⛈️":
            tech_score -= 25
            is_mtf_veto = True
            veto_max_59 = True
            mtf_reason = "👁️‍🗨️ <b>[مصفوفة التوافق MTF]:</b> الفريم اليومي الأكبر يعاني من مسار هابط شرس. تم حظر الاختراق اللحظي لمنع السباحة ضد التيار الأكبر."
        else:
            tech_score += 15
            mtf_reason = "👁️‍🗨️ <b>[مصفوفة التوافق MTF]:</b> اصطفاف نجمي إيجابي! الفريم اللحظي مدعوم بمسار صاعد مستقر ومؤكد على الفريم اليومي الأكبر."

    if rr_ratio < 1.5:
        tech_score -= 20
        veto_max_59 = True
        reasons.append(f"⚖️ <b>[إدارة المخاطر R:R]:</b> نسبة الربح للمخاطرة سيئة ({rr_ratio:.1f}:1). نحن نقبل الصفقات الآمنة فقط. تم حظر الدخول.")
    else:
        tech_score += 10
        reasons.append(f"⚖️ <b>[إدارة المخاطر R:R]:</b> العائد ممتاز ({rr_ratio:.1f}:1) ومحمي بوقف ATR المطاطي.")

    if pd.notna(last_vwap) and not is_forex:
        if last_close < last_vwap:
            tech_score -= 20
            veto_max_59 = True
            reasons.append("🐋 <b>[مؤشر الحقيقة VWAP]:</b> السعر يتداول تحت متوسط تكلفة الحيتان (تصريف خفي). تم حظر الدخول.")
        else:
            tech_score += 10
            reasons.append("🐋 <b>[مؤشر الحقيقة VWAP]:</b> السعر يتداول فوق متوسط تكلفة الحيتان (تجميع إيجابي مستمر).")

    if macro_status == "سلبي ⛈️" and not is_forex:
        if is_zero_bottom and not is_zero_breakdown:
            tech_score += 15
            macro_reason = "🛡️ <b>[تكتيك دفاعي]:</b> السوق ينزف، وهذا الأصل في قاع زيرو السحيق (استثناء آمن للاصطياد)."
        elif is_blue_sky and (vol_accel_ratio >= 1.2 or is_crypto):
            tech_score += 20
            macro_reason = "🌌 <b>[استثناء المتمرد]:</b> الأصل يحلق في سماء زرقاء متمرداً على سلبية المؤشر العام!"
        else:
            tech_score -= 30
            is_absolute_lockdown = True
            macro_reason = "🛑 <b>[الإغلاق المطلق 🔒]:</b> المؤشر ينزف والأصل ليس في قاع زيرو. تم حظر الدخول لحمايتك من (مصيدة الثيران)."
    elif macro_status == "إيجابي ☀️" and not is_forex:
        if "اختراق" in event_text or is_blue_sky:
            tech_score += 10
            macro_reason = "☀️ <b>[دعم الماكرو]:</b> طقس السوق صاعد ويدعم نجاح هذه الاختراقات بقوة."

    if is_macro_bull_stock: tech_score += 15; reasons.append("✅ <b>الاتجاه العام:</b> يتداول في أمان استثماري (أعلى من 200).")
    else: 
        if is_micro_bull and mom_score >= 70 and not is_bleeding:
            golden_watch = True; tech_score += 5; reasons.append(f"👀 <b>مرحلة تعافي:</b> يحاول الارتداد رغم كونه تحت MA200.")
        else:
            tech_score -= 25; veto_max_59 = True; reasons.append("❌ <b>الاتجاه العام:</b> ينهار تحت متوسط 200 (مسار هابط).")

    if is_forex or is_crypto:
        tech_score += 10
        if veto_max_59 and mom_score >= 60 and (macro_status != "سلبي ⛈️" or is_forex) and not is_mtf_veto: 
            veto_max_59 = False; veto_max_79 = True
    else:
        if vol_accel_ratio >= 1.2 and pct_1d > 0 and not is_bleeding:
            tech_score += 15; reasons.append(f"🌊 <b>السيولة:</b> تدفق سيولة مؤسساتية عالية.")
            if veto_max_59 and mom_score >= 60 and macro_status != "سلبي ⛈️" and not is_mtf_veto: veto_max_59 = False; veto_max_79 = True
        elif vol_accel_ratio < 0.7: tech_score -= 5; reasons.append("❄️ <b>السيولة:</b> التداولات ضعيفة وجافة.")

    if is_micro_bull:
        if dist_ma50 <= 3.5 and not is_bleeding: tech_score += 15; reasons.append("💎 <b>الدعم:</b> ارتداد إيجابي آمن بالقرب من متوسط 50.")
        elif dist_ma50 <= 3.5 and is_bleeding: tech_score += 0; veto_max_79 = True; reasons.append("⏳ <b>الدعم:</b> السعر يختبر الدعم اللحظي، ننتظر توقف النزيف.")
        elif dist_ma50 > 8.0 and not is_blue_sky: tech_score -= 10; veto_max_79 = True; reasons.append(f"⚠️ <b>التضخم:</b> السعر ابتعد عن الدعم بنسبة {dist_ma50:.1f}%.")
    else:
        if not golden_watch: tech_score -= 20; veto_max_59 = True; reasons.append("🔴 <b>المضاربة:</b> السعر سلبي ويكسر متوسط 50 اللحظي.")

    if is_zero_breakdown:
        tech_score -= 40; veto_max_59 = True; reasons.append("🕳️ <b>[انهيار تاريخي]:</b> السعر يكسر قاع 300 شمعة ويسقط في الهاوية. حظر دخول نهائي!")
    elif "🚀" in event_text or "🟢" in event_text or "💎" in event_text or "📈" in event_text or "🔥" in event_text or "👑" in event_text or "🌌" in event_text: 
        tech_score += 10; reasons.append(f"⚡ <b>الحدث:</b> إشارة إيجابية داعمة في الشموع الأخيرة.")
    elif "🩸" in event_text or "🔴" in event_text or "🛑" in event_text or "⚠️" in event_text or "📉" in event_text: 
        tech_score -= 15; reasons.append(f"⚠️ <b>الحدث:</b> ضغط بيعي واضح.")
        if "كسر" in event_text: veto_max_59 = True

    if is_zero_bottom and macro_status != "سلبي ⛈️" and not is_zero_breakdown: 
        tech_score += 10; reasons.append("🎯 <b>زيرو انعكاس:</b> السعر رخيص جداً ويختبر قاع القناة التاريخي.")
    
    if is_blue_sky:
        tech_score += 25
        if not is_zero_breakout: reasons.append("🌌 <b>سماء زرقاء:</b> يواصل التحليق فوق قمة زيرو التاريخية بلا مقاومات.")
        else: reasons.append("👑 <b>انفجار تاريخي:</b> يخترق سقف زيرو الآن وينطلق في سماء مفتوحة.")
    elif pd.notna(zr_high) and last_close >= zr_high * 0.97 and last_close <= zr_high:
        tech_score -= 15; veto_max_79 = True; reasons.append("🧱 <b>تحذير زيرو:</b> السعر متضخم ويصطدم بسقف القناة كمقاومة.")

    tech_score = int(max(0, min(100, tech_score)))
    final_score = int((tech_score * 0.4) + (mom_score * 0.6))
    
    reasons = [r for r in reasons if r]
    reasons.insert(0, f"📊 <b>الزخم التراكمي:</b> تقييم قوة الحركة هو <b>{mom_score}/100</b>.")
    
    if mtf_reason: reasons.insert(0, mtf_reason)
    
    if is_absolute_lockdown:
        final_score = min(final_score, 59)
        if macro_reason: reasons.insert(0, macro_reason)
    else:
        if macro_reason: reasons.insert(0, macro_reason)
        if golden_watch and not is_bleeding: final_score = min(max(final_score, 60), 79); reasons.insert(0, "🛡️ <b>[فيتو التعافي]:</b> تم تخفيض التقييم للمراقبة لأن الأصل ما زال تحت MA200.")
        elif not is_macro_bull_stock and not is_micro_bull and is_bleeding: final_score = min(final_score, 59); reasons.insert(0, "🛑 <b>[فيتو الانهيار]:</b> الأصل ضعيف جداً ومنهار، تم فرض حظر الدخول.")
        elif veto_max_59 and not golden_watch: final_score = min(final_score, 59); reasons.insert(0, "🛡️ <b>[فيتو المخاطر]:</b> تم فرض حظر الدخول بسبب العيوب القاتلة (الفيتو).")
        elif (veto_max_79 or rsi > 72) and not is_blue_sky: final_score = min(final_score, 79); reasons.insert(0, "🛡️ <b>[فيتو الأمان]:</b> السعر متضخم (مؤشرات عالية)، تم منعه من الـ VIP لتجنب التعليقة.")

    if final_score >= 80: 
        if is_blue_sky: dec, col = "سماء زرقاء 🌌", "#FFD700"
        else: dec, col = "دخول قوي 🟢", "#00E676"
    elif final_score >= 60: 
        if is_blue_sky: dec, col = "مراقبة الانفجار 🌌", "#FFD700"
        else: dec, col = "مراقبة 🟡", "#FFD700"
    else: dec, col = "تجنب 🔴", "#FF5252"

    return final_score, dec, col, reasons

def get_cat(val):
    try:
        if pd.isna(val) or val == "" or np.isinf(float(val)): return ""
        v = abs(float(val))
        if v >= 1.0: return "MAJOR"
        elif v >= 0.1: return "HIGH"
        else: return "MEDIUM"
    except: return ""

def format_cat(val, cat):
    try:
        if pd.isna(val) or val == "" or np.isinf(float(val)): return "⚪ 0.00%"
        f_val = float(val)
        cat_str = f" {cat}" if cat else ""
        if f_val > 0: return f"🟢 +{f_val:.2f}%{cat_str}"
        elif f_val < 0: return f"🔴 {f_val:.2f}%{cat_str}"
        return f"⚪ 0.00%{cat_str}"
    except: return "⚪ 0.00%"

def safe_color_table(val):
    val_str = str(val)
    if "👑" in val_str or "🌌" in val_str: return 'color: #ffd700; font-weight: bold; background-color: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700;'
    if "🟢" in val_str or "✅" in val_str or "🚀" in val_str or "💎" in val_str: return 'color: #00E676; font-weight: bold;'
    if "🔴" in val_str or "❌" in val_str or "🩸" in val_str or "⚠️" in val_str: return 'color: #FF5252; font-weight: bold;'
    if "🕳️" in val_str: return 'color: #fff; font-weight: bold; background-color: #f44336; border: 1px solid #f44336;'
    if "MAJOR" in val_str: return 'color: #00d2ff; font-weight: bold;' 
    if "HIGH" in val_str: return 'color: #FFD700; font-weight: bold;' 
    if "⏱️" in val_str: return 'color: #00d2ff; font-weight: bold;'
    try:
        clean_str = val_str.replace('MAJOR', '').replace('HIGH', '').replace('MEDIUM', '').replace('LOW', '').replace('%', '').replace(',', '').replace('+', '').replace('🟢', '').replace('🔴', '').replace('⚪', '').strip()
        if clean_str.replace('.', '', 1).replace('-', '', 1).isdigit():
            num = float(clean_str)
            if num > 0: return 'color: #00E676; font-weight: bold;'
            if num < 0: return 'color: #FF5252; font-weight: bold;'
    except: pass
    return ''

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_data(ticker_symbol, period="2y", interval="1d"): 
    try:
        tk = yf.Ticker(str(ticker_symbol))
        df = tk.history(period=period, interval=interval)
        if df is None or df.empty: return pd.DataFrame()
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df = localize_timezone(df)
        return df
    except Exception: return pd.DataFrame() 

@st.cache_data(ttl=900, show_spinner=False)
def scan_market_v83(watchlist_list, period="1y", interval="1d", lbl="أيام", tf_label="يومي", macro_status="تذبذب ⛅"):
    breakouts, breakdowns, recent_up, recent_down = [], [], [], []
    loads_list, alerts_list, ai_picks = [], [], []
    
    saudi_tz_internal = datetime.timezone(datetime.timedelta(hours=3))
    now_internal = datetime.datetime.now(saudi_tz_internal)
    
    col_change = "تغير 1 يوم" if interval == "1d" else "تغير 1 شمعة"
    col_count = "عدد الأيام" if interval == "1d" else "عدد الشموع"

    histories = {}
    
    def fetch_data(tk):
        try:
            t_obj = yf.Ticker(tk)
            df = t_obj.history(period=period, interval=interval)
            if df.empty: return tk, None, None
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = localize_timezone(df)
            
            df_1d = None
            if interval != "1d":
                try:
                    df_1d_raw = t_obj.history(period="1y", interval="1d")
                    if not df_1d_raw.empty:
                        if isinstance(df_1d_raw.columns, pd.MultiIndex): df_1d_raw.columns = df_1d_raw.columns.get_level_values(0)
                        df_1d = localize_timezone(df_1d_raw)
                except: pass
            if len(df) > 30: return tk, df, df_1d
        except Exception: pass
        return tk, None, None

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_data, tk) for tk in watchlist_list]
        for future in as_completed(futures):
            tk, df_s, df_1d = future.result()
            if df_s is not None: histories[tk] = (df_s, df_1d)

    for tk in watchlist_list:
        try: 
            data = histories.get(tk)
            if data is not None:
                df_s, df_1d = data
                is_forex = "=X" in tk
                is_crypto = "-USD" in tk
                
                c, h, l = df_s['Close'], df_s['High'], df_s['Low']
                vol = df_s['Volume'] if 'Volume' in df_s.columns else pd.Series([0]*len(c), index=c.index)
                stock_name = get_stock_name(tk)
                
                ma50 = c.rolling(50).mean()
                ma200 = c.rolling(200).mean() if len(c) >= 200 else c.rolling(50).mean()
                v_sma20, v_sma10 = vol.rolling(20).mean(), vol.rolling(10).mean()
                
                tr1 = h - l
                tr2 = (h - c.shift(1)).abs()
                tr3 = (l - c.shift(1)).abs()
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = tr.rolling(14).mean()
                last_atr = atr.iloc[-1] if pd.notna(atr.iloc[-1]) and atr.iloc[-1] > 0 else (c.iloc[-1] * 0.02)
                
                if vol.sum() == 0 or is_forex: vwap = c.rolling(20).mean()
                else:
                    typical_price = (h + l + c) / 3
                    vwap = (typical_price * vol).rolling(20).sum() / vol.rolling(20).sum()
                last_vwap = vwap.iloc[-1] if pd.notna(vwap.iloc[-1]) else c.iloc[-1]

                h3, l3 = h.rolling(3).max().shift(1), l.rolling(3).min().shift(1)
                h4, l4 = h.rolling(4).max().shift(1), l.rolling(4).min().shift(1)
                h10, l10 = h.rolling(10).max().shift(1), l.rolling(10).min().shift(1)
                
                zr_window = 300 if len(c) >= 300 else max(len(c) - 2, 10)
                df_s['ZR_High'] = h.rolling(zr_window, min_periods=10).max().shift(1)
                df_s['ZR_Low'] = l.rolling(zr_window, min_periods=10).min().shift(1)
                
                last_zr_h = df_s['ZR_High'].iloc[-1] if not df_s['ZR_High'].empty else np.nan
                prev_zr_h = df_s['ZR_High'].iloc[-2] if len(df_s) > 1 else last_zr_h
                last_zr_l = df_s['ZR_Low'].iloc[-1] if not df_s['ZR_Low'].empty else np.nan
                prev_zr_l = df_s['ZR_Low'].iloc[-2] if len(df_s) > 1 else last_zr_l
                
                up_diff, down_diff = c.diff().clip(lower=0), -1 * c.diff().clip(upper=0)
                rsi = 100 - (100 / (1 + (up_diff.ewm(com=13, adjust=False).mean() / down_diff.ewm(com=13, adjust=False).mean())))
                
                last_c, prev_c, prev2_c = c.iloc[-1], c.iloc[-2], c.iloc[-3]
                
                daily_trend = "صاعد ☀️"
                if interval == "1d":
                    if pd.notna(ma50.iloc[-1]) and last_c < ma50.iloc[-1]: daily_trend = "هابط ⛈️"
                else:
                    if df_1d is not None and not df_1d.empty and len(df_1d) > 50:
                        d_c = df_1d['Close'].dropna()
                        if not d_c.empty:
                            d_ma50 = d_c.rolling(50).mean().iloc[-1]
                            if d_c.iloc[-1] < d_ma50: daily_trend = "هابط ⛈️"
                
                if is_forex or is_crypto: vol_ratio, vol_accel_ratio = 1.0, 1.0
                else:
                    last_vol = vol.iloc[-1] if pd.notna(vol.iloc[-1]) and vol.iloc[-1] > 0 else 1000000
                    avg_vol = v_sma20.iloc[-1] if pd.notna(v_sma20.iloc[-1]) and v_sma20.iloc[-1] > 0 else 1000000
                    avg_vol_10 = v_sma10.iloc[-1] if pd.notna(v_sma10.iloc[-1]) and v_sma10.iloc[-1] > 0 else 1000000
                    vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1.0
                    vol_accel_ratio = last_vol / avg_vol_10 if avg_vol_10 > 0 else 1.0

                diff = c.diff()
                direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
                counter = 0; counters = []
                for d in direction:
                    if d == 1: counter = counter + 1 if counter > 0 else 1
                    elif d == -1: counter = counter - 1 if counter < 0 else -1
                    else: counter = 0
                    counters.append(counter)
                cur_count = counters[-1]
                
                try: candle_time = now_internal.strftime("⏱️ %H:%M | %Y-%m-%d") if interval == "1d" else df_s.index[-1].strftime("⏱️ %H:%M | %Y-%m-%d")
                except: candle_time = now_internal.strftime("⏱️ %H:%M | %Y-%m-%d")
                full_time_str = candle_time

                pct_1d = (last_c / prev_c - 1) * 100 if len(c)>1 and prev_c != 0 else 0
                pct_3d = (last_c / c.iloc[-4] - 1) * 100 if len(c)>3 else 0
                pct_5d = (last_c / c.iloc[-6] - 1) * 100 if len(c)>5 else 0
                pct_10d = (last_c / c.iloc[-11] - 1) * 100 if len(c)>10 else 0

                cat_1d, cat_3d, cat_5d, cat_10d = get_cat(pct_1d), get_cat(pct_3d), get_cat(pct_5d), get_cat(pct_10d)
                
                loads_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الاتجاه": int(cur_count), col_count: abs(cur_count), col_change: pct_1d, "1d_cat": cat_1d, f"تراكمي 3 {lbl}": pct_3d, "3d_cat": cat_3d, f"تراكمي 5 {lbl}": pct_5d, "5d_cat": cat_5d, f"تراكمي 10 {lbl}": pct_10d, "10d_cat": cat_10d, f"حالة 3 {lbl}": "✅" if pct_3d > 0 else "❌", f"حالة 5 {lbl}": "✅" if pct_5d > 0 else "❌", f"حالة 10 {lbl}": "✅" if pct_10d > 0 else "❌", "raw_3d": pct_3d, "raw_5d": pct_5d, "raw_10d": pct_10d})

                bo_today, bd_today = [], []
                
                if pd.notna(last_zr_h) and last_c > last_zr_h:
                    if prev_c <= prev_zr_h:  
                        alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"اختراق سقف زيرو 👑🚀"})
                        bo_today.append("اختراق زيرو 👑")
                    else: 
                        alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"سماء زرقاء 🌌"})
                        bo_today.append("سماء زرقاء 🌌")

                if pd.notna(last_zr_l) and last_c < last_zr_l:
                    if prev_c >= prev_zr_l:
                        alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"كسر قاع زيرو 🩸📉"})
                        bd_today.append("كسر زيرو 🩸")
                    else:
                        alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"انهيار سحيق 🕳️"})
                        bd_today.append("سقوط 🩸")

                if last_c > h3.iloc[-1] and prev_c <= h3.iloc[-2]: bo_today.append(f"3{lbl}"); alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"اختراق 3 {lbl} 🟢"})
                if last_c > h4.iloc[-1] and prev_c <= h4.iloc[-2]: bo_today.append(f"4{lbl}")
                if last_c > h10.iloc[-1] and prev_c <= h10.iloc[-2]: bo_today.append(f"10{lbl}")
                if last_c < l3.iloc[-1] and prev_c >= l3.iloc[-2]: bd_today.append(f"3{lbl}"); alerts_list.append({"الشركة": stock_name, "التاريخ": candle_time, "الفريم": tf_label, "التنبيه": f"كسر 3 {lbl} 🔴"})

                bo_yest, bd_yest = [], []
                if prev_c > h3.iloc[-2] and prev2_c <= h3.iloc[-3]: bo_yest.append(f"3{lbl}")
                if prev_c < l3.iloc[-2] and prev2_c >= l3.iloc[-3]: bd_yest.append(f"3{lbl}")

                events = []
                bo_score_add = 0
                if pct_1d > 0 and vol_accel_ratio > 1.2 and not is_forex and not is_crypto: events.append("تسارع سيولة 🌊🔥"); bo_score_add += 10
                elif pct_1d > 0 and cur_count > 0 and (is_forex or is_crypto): events.append("زخم سعري 🌊🔥"); bo_score_add += 10
                
                if bo_today: events.append(f"انطلاق 🚀 ({'+'.join(bo_today)})"); bo_score_add += 15
                elif bd_today: events.append(f"سقوط 🩸 ({'+'.join(bd_today)})"); bo_score_add -= 20
                elif bo_yest and last_c > h3.iloc[-1]: events.append("اختراق سابق 🟢"); bo_score_add += 10
                elif bd_yest and last_c < l3.iloc[-1]: events.append("كسر سابق 🔴"); bo_score_add -= 15
                else:
                    dist_m50 = ((last_c - ma50.iloc[-1])/ma50.iloc[-1]) * 100 if pd.notna(ma50.iloc[-1]) else 100
                    if 0 <= dist_m50 <= 2.5 and cur_count > 0: events.append("ارتداد MA50 💎"); bo_score_add += 10
                    elif -2.5 <= dist_m50 < 0 and cur_count < 0: events.append("كسر MA50 ⚠️"); bo_score_add -= 15

                if not events:
                    if cur_count > 1: events.append(f"مسار صاعد ({cur_count} {lbl}) 📈"); bo_score_add += 5
                    elif cur_count < -1: events.append(f"مسار هابط ({abs(cur_count)} {lbl}) 📉"); bo_score_add -= 5
                    else: events.append("استقرار ➖")

                event_text = " | ".join(events)
                bg_color, text_color, border_color = "transparent", "gray", "gray"
                if "👑" in event_text or "🌌" in event_text: bg_color, text_color, border_color = "rgba(255, 215, 0, 0.15)", "#FFD700", "rgba(255, 215, 0, 0.8)"
                elif any(x in event_text for x in ["🚀", "🟢", "💎", "📈", "🔥"]): bg_color, text_color, border_color = "rgba(0, 230, 118, 0.12)", "#00E676", "rgba(0, 230, 118, 0.5)"
                elif "🕳️" in event_text: bg_color, text_color, border_color = "#f44336", "#fff", "#fff"
                elif any(x in event_text for x in ["🩸", "🔴", "🛑", "📉"]): bg_color, text_color, border_color = "rgba(255, 82, 82, 0.12)", "#FF5252", "rgba(255, 82, 82, 0.5)"
                elif "⚠️" in event_text: bg_color, text_color, border_color = "rgba(255, 215, 0, 0.12)", "#FFD700", "rgba(255, 215, 0, 0.5)"
                ch_badge = f"<span class='bo-badge' style='background-color:{bg_color}; color:{text_color}; border: 1px solid {border_color};'>{event_text}</span>"

                sl_atr = last_c - (last_atr * 1.5)
                sl_fallback = ma50.iloc[-1] if pd.notna(ma50.iloc[-1]) else last_c * 0.95
                sl = sl_atr if sl_atr < last_c else sl_fallback
                if sl >= last_c: sl = last_c * 0.98

                risk = last_c - sl
                if risk <= 0: risk = last_c * 0.01

                min_target = last_c + (risk * 2.0) 

                if pd.notna(last_zr_h) and last_c > last_zr_h:
                    target_val = last_c + (risk * 3.0)
                    target_disp = "سماء مفتوحة 🚀"
                else:
                    natural_target = last_zr_h if pd.notna(last_zr_h) else last_c * 1.05
                    target_val = max(natural_target, min_target)
                    target_disp = format_price(target_val, tk)

                rr_ratio = (target_val - last_c) / risk if risk > 0 else 0
                mom_score = calc_momentum_score(pct_1d, pct_5d, pct_10d, vol_ratio)
                ai_score, ai_dec, ai_col, reasons_list = get_ai_analysis(last_c, ma50.iloc[-1], ma200.iloc[-1], rsi.iloc[-1], cur_count, last_zr_l, last_zr_h, event_text, bo_score_add, mom_score, vol_accel_ratio, pct_1d, macro_status, is_forex, is_crypto, last_vwap, rr_ratio, daily_trend, interval)
                
                price_disp = format_price(last_c, tk)
                sl_disp = format_price(sl, tk)

                ai_picks.append({"الشركة": stock_name, "الرمز": tk, "السعر": price_disp, "Score 💯": ai_score, "الحالة اللحظية ⚡": ch_badge, "الهدف 🎯": target_disp, "الوقف 🛡️": sl_disp, "التوصية 🚦": ai_dec, "اللون": ai_col, "raw_score": ai_score, "raw_mom": mom_score, "raw_events": event_text, "raw_time": full_time_str, "raw_target": target_val, "raw_sl": sl, "raw_price": last_c, "raw_reasons": reasons_list, "raw_rr": rr_ratio})

        except Exception as e: 
            continue

    return pd.DataFrame(breakouts), pd.DataFrame(breakdowns), pd.DataFrame(recent_up), pd.DataFrame(recent_down), pd.DataFrame(loads_list), pd.DataFrame(alerts_list), pd.DataFrame(ai_picks)

# ==========================================
# 🌟 الواجهة الرئيسية
# ==========================================
st.markdown("<div class='search-container'>", unsafe_allow_html=True)

col_m1, col_m2 = st.columns([1, 1])
with col_m1:
    market_choice = st.radio("🌐 الأسواق:", ["السعودي 🇸🇦", "الأمريكي 🇺🇸", "الفوركس 💱", "الكريبتو ₿"], horizontal=True)
with col_m2:
    tf_choice = st.radio("⏳ الفاصل الزمني:", ["يومي (1D)", "ساعة (60m)", "15 دقيقة (15m)"], horizontal=True)

interval_map = {"يومي (1D)": "1d", "ساعة (60m)": "60m", "15 دقيقة (15m)": "15m"}
period_map_scan = {"1d": "2y", "60m": "3mo", "15m": "1mo"} 
period_map_ui = {"1d": "2y", "60m": "6mo", "15m": "60d"}   

selected_interval = interval_map[tf_choice]
selected_period_scan = period_map_scan[selected_interval]
selected_period_ui = period_map_ui[selected_interval]

tf_label_name = tf_choice.replace(" (1D)", "").replace(" (60m)", "").replace(" (15m)", "")
lbl = "أيام" if selected_interval == "1d" else "شموع"
col_change_name = 'تغير 1 يوم' if selected_interval == '1d' else 'تغير 1 شمعة'

col_empty1, col_search1, col_search2, col_empty2 = st.columns([1, 3, 1, 1])

with col_search1: 
    if "السعودي" in market_choice:
        saudi_display_to_ticker = {f"{name} ({tk.replace('.SR', '')})": tk for tk, name in SAUDI_NAMES.items()}
        options = sorted(list(saudi_display_to_ticker.keys()))
        default_index = options.index('الراجحي (1120)') if 'الراجحي (1120)' in options else 0
        selected_option = st.selectbox("🎯 اختر السهم:", options, index=default_index, label_visibility="collapsed")
        ticker = saudi_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(SAUDI_NAMES.keys())
        currency = "ريال"
    elif "الأمريكي" in market_choice:
        us_display_to_ticker = {f"{name} ({tk})": tk for tk, name in US_NAMES.items()}
        options = sorted(list(us_display_to_ticker.keys()))
        default_index = options.index('NVIDIA (NVDA)') if 'NVIDIA (NVDA)' in options else 0
        selected_option = st.selectbox("🎯 اختر السهم:", options, index=default_index, label_visibility="collapsed")
        ticker = us_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(US_NAMES.keys())
        currency = "$"
    elif "الفوركس" in market_choice:
        fx_display_to_ticker = {f"{name}": tk for tk, name in FX_NAMES.items()}
        options = list(fx_display_to_ticker.keys())
        default_index = 0
        selected_option = st.selectbox("🎯 اختر الزوج:", options, index=default_index, label_visibility="collapsed")
        ticker = fx_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(FX_NAMES.keys())
        currency = "سعر"
    elif "الكريبتو" in market_choice:
        crypto_display_to_ticker = {f"{name}": tk for tk, name in CRYPTO_NAMES.items()}
        options = list(crypto_display_to_ticker.keys())
        default_index = 0
        selected_option = st.selectbox("🎯 اختر العملة:", options, index=default_index, label_visibility="collapsed")
        ticker = crypto_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(CRYPTO_NAMES.keys())
        currency = "$"

with col_search2: analyze_btn = st.button("استخراج الفرص 💎", use_container_width=True, type="primary")

macro_status, macro_name, macro_pct, macro_price = get_macro_status_v82(market_choice)

if "الفوركس" in market_choice:
    bg_m, txt_m, bord_m, msg_m = "rgba(33, 150, 243, 0.1)", "#00d2ff", "#00d2ff", "سوق العملات لامركزي (درع الماكرو مخصص لمراقبة قوة الدولار فقط 💱)"
elif macro_status == "إيجابي ☀️":
    bg_m, txt_m, bord_m, msg_m = "rgba(0, 230, 118, 0.1)", "#00E676", "#00E676", "الرادار الهجومي مفتوح 🚀 (الاختراقات مدعومة من سيولة السوق الكلي)"
elif macro_status == "سلبي ⛈️":
    bg_m, txt_m, bord_m, msg_m = "rgba(255, 82, 82, 0.1)", "#FF5252", "#FF5252", "الإغلاق المطلق مُفعل 🔒 (حظر التوصيات باستثناء [قيعان زيرو] السحيقة)"
else:
    bg_m, txt_m, bord_m, msg_m = "rgba(255, 215, 0, 0.1)", "#FFD700", "#FFD700", "تذبذب وحيرة ⚖️ (التركيز على المضاربة السريعة واختطاف الأرباح)"

st.markdown(f"""
<div style='background-color: {bg_m}; border: 1px solid {bord_m}; padding: 15px; border-radius: 10px; margin-top: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);'>
    <h4 style='color: {txt_m}; margin: 0; font-weight:900;'>🛡️ درع السوق الكلي (The Macro Shield)</h4>
    <div style='font-size: 18px; color: white; margin-top: 5px;'>
        المؤشر القيادي: <b style='color:#00d2ff;'>{macro_name}</b> | الإغلاق: <b>{format_price(macro_price, "^GSPC")} ({macro_pct:+.2f}%)</b> | الطقس: <b>{macro_status}</b>
    </div>
    <div style='font-size: 15px; color: {txt_m}; margin-top: 5px; font-weight:bold;'>{msg_m}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if analyze_btn or ticker:
    with st.spinner(f"⚡ جاري مسح السوق بهدوء... وجلب بيانات ({display_name})..."):
        
        df_bup, df_bdn, df_recent_up, df_recent_down, df_loads, df_alerts, df_ai_picks = scan_market_v83(
            watchlist_list=selected_watchlist, period=selected_period_scan, interval=selected_interval, lbl=lbl, tf_label=tf_label_name, macro_status=macro_status
        )
        
        df = get_stock_data(ticker, selected_period_ui, selected_interval)

        if df is None or df.empty: 
            st.warning(f"⚠️ جدار الحماية: تعذر جلب بيانات ({display_name}) من المصدر. يرجى الانتظار بضع ثوانٍ والمحاولة مرة أخرى.")
        else:
            is_fx_main = "=X" in ticker
            is_crypto_main = "-USD" in ticker
            
            if df_loads.empty: st.cache_data.clear()

            close, high, low = df['Close'], df['High'], df['Low']
            vol = df['Volume'] if 'Volume' in df.columns else pd.Series([0]*len(close), index=close.index)
            
            df['SMA_50'] = close.rolling(window=50).mean()
            df['SMA_200'] = close.rolling(window=200).mean() if len(close) >= 200 else close.rolling(window=50).mean()
            
            if vol.sum() == 0 or is_fx_main: df['VWAP'] = close.rolling(20).mean()
            else:
                typical_price = (high + low + close) / 3
                df['VWAP'] = (typical_price * vol).rolling(20).sum() / vol.rolling(20).sum()
            
            df['High_3D'], df['Low_3D'] = high.rolling(3).max().shift(1), low.rolling(3).min().shift(1)
            df['High_4D'], df['Low_4D'] = high.rolling(4).max().shift(1), low.rolling(4).min().shift(1)
            df['High_10D'], df['Low_10D'] = high.rolling(10).max().shift(1), low.rolling(10).min().shift(1)
            df['High_15D'], df['Low_15D'] = high.rolling(15).max().shift(1), low.rolling(15).min().shift(1)

            df['1d_%'] = close.pct_change(1) * 100
            df['3d_%'] = close.pct_change(3) * 100 
            df['5d_%'] = close.pct_change(5) * 100
            df['10d_%'] = close.pct_change(10) * 100
            
            diff = close.diff()
            direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
            counter = []; curr = 0
            for d in direction:
                if d == 1: curr = curr + 1 if curr > 0 else 1
                elif d == -1: curr = curr - 1 if curr < 0 else -1
                else: curr = 0
                counter.append(curr)
            df['Counter'] = counter

            up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
            ema_up, ema_down = up.ewm(com=13, adjust=False).mean(), down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))

            if 'ZR_High' not in df.columns:
                zr_window = 300 if len(close) >= 300 else max(len(close) - 2, 10)
                df['ZR_High'] = high.rolling(zr_window, min_periods=10).max().shift(1)
                df['ZR_Low'] = low.rolling(zr_window, min_periods=10).min().shift(1)

            last_close, prev_close = close.iloc[-1], close.iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            
            last_sma200, last_sma50 = df['SMA_200'].iloc[-1], df['SMA_50'].iloc[-1]
            last_zr_high, last_zr_low = df['ZR_High'].iloc[-1], df['ZR_Low'].iloc[-1]
            
            if is_fx_main or is_crypto_main: vol_status, vol_color = "سوق سيولة عالمية", "💱"
            else:
                last_vol = df['Volume'].iloc[-1] if pd.notna(df['Volume'].iloc[-1]) and df['Volume'].iloc[-1] > 0 else 1000000
                avg_vol = vol.rolling(window=20).mean().iloc[-1] if pd.notna(vol.rolling(window=20).mean().iloc[-1]) and vol.rolling(window=20).mean().iloc[-1] > 0 else 1000000
                avg_vol10 = vol.rolling(window=10).mean().iloc[-1] if pd.notna(vol.rolling(window=10).mean().iloc[-1]) and vol.rolling(window=10).mean().iloc[-1] > 0 else 1000000
                main_vol_accel_ratio = last_vol / avg_vol10 if avg_vol10 > 0 else 1
                vol_status, vol_color = ("تسارع سيولة", "🔥") if main_vol_accel_ratio >= 1.2 else ("سيولة جيدة", "📈") if last_vol > avg_vol else ("سيولة ضعيفة", "❄️")

            if pd.notna(last_sma200) and pd.notna(last_sma50):
                if last_close > last_sma200 and last_close > last_sma50: trend, trend_color = "مسار صاعد 🚀", "🟢"
                elif last_close < last_sma200 and last_close < last_sma50: trend, trend_color = "مسار هابط 🔴", "🔴"
                else: trend, trend_color = "تذبذب (حيرة) ⚖️", "🟡"
            else: trend, trend_color = "جاري الحساب...", "⚪"

            zr_status, zr_color = ("سماء زرقاء", "🌌") if pd.notna(last_zr_high) and last_close > last_zr_high else ("يختبر سقف زيرو", "⚠️") if pd.notna(last_zr_high) and last_close >= last_zr_high * 0.98 else ("يختبر قاع زيرو", "💎") if pd.notna(last_zr_low) and last_close <= last_zr_low * 1.05 else ("في منتصف القناة", "⚖️")

            st.markdown(f"### 🤖 قراءة استراتيجية ماسة لـ ({display_name}) - فاصل [{tf_label_name}]:")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"الإغلاق ({currency})", format_price(last_close, ticker), f"{pct_change:.2f}%")
            m2.metric(f"الترند {trend_color}", trend)
            m3.metric(f"السيولة {vol_color}", vol_status)
            m4.metric(f"القناة {zr_color}", zr_status)
            st.markdown("<br>", unsafe_allow_html=True)

            tab_vip, tab_whales, tab_ai, tab1, tab5, tab6, tab_backtest, tab_track, tab2, tab3, tab4 = st.tabs([
                "👑 VIP ماسة", "🐋 رادار الحيتان", "🧠 التوصيات", "🎯 الاختراقات", "🗂️ ماسح السوق", "🚨 التنبيهات", "⏳ الباك تيست", "📂 المراقبة", "🌐 TradingView", "📊 الشارت", "📋 البيانات"
            ])

            with tab_vip:
                if not df_ai_picks.empty:
                    df_vip_full = pd.DataFrame(df_ai_picks)
                    df_vip = df_vip_full[(df_vip_full['raw_score'] >= 80) & (df_vip_full['raw_mom'] >= 75) & (~df_vip_full['raw_events'].str.contains('كسر|هابط|تصحيح|🕳️'))].sort_values(by=['raw_score', 'raw_mom'], ascending=[False, False]).head(3)
                    if not df_vip.empty:
                        st.markdown("<h3 style='text-align: center; color: #ffd700; font-weight: 900; margin-bottom: 5px;'>👑 الصندوق الأسود: أقوى الفرص الاستثمارية الآن</h3>", unsafe_allow_html=True)
                        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
                        with col_btn2:
                            if st.button("💾 حفظ هذه الفرص في محفظة المراقبة", use_container_width=True):
                                save_to_tracker_sql(df_vip, market_choice)
                                st.success("✅ تم الحفظ بنجاح! راجع تبويب (المراقبة 📂)")
                        cards_html = "<div class='vip-container'>"
                        for _, row in df_vip.iterrows():
                            risk_amount = capital * (risk_pct / 100)
                            risk_per_share = float(row['raw_price']) - float(row['raw_sl'])
                            
                            if risk_per_share > 0: 
                                if "=X" in row['الرمز']:
                                    shares_str = "رافعة (Lot)"
                                    pos_value_str = "تداول هامشي 💱"
                                elif "-USD" in row['الرمز']:
                                    shares = risk_amount / risk_per_share
                                    pos_value = shares * float(row['raw_price'])
                                    pos_value_str = f"{pos_value:,.2f} $"
                                    shares_str = f"{shares:.4f} حبة"
                                else:
                                    shares = int(risk_amount / risk_per_share)
                                    pos_value = shares * float(row['raw_price'])
                                    pos_value_str = f"{pos_value:,.2f} {currency}"
                                    shares_str = f"{shares:,} سهم"
                            else: shares_str, pos_value_str = "0", "0"
                            
                            alert_id = f"{today_str}_{row['الرمز']}_{selected_interval}"
                            if tg_token and tg_chat and alert_id not in st.session_state.tg_sent:
                                msg = f"🚨 *Masa VIP Alert!* 💎\n\n📌 *Asset:* {row['الشركة']} ({row['الرمز']})\n⏱️ *Timeframe:* {tf_choice}\n💰 *Price:* {row['السعر']}\n🎯 *Target:* {row['الهدف 🎯']}\n🛡️ *SL (ATR):* {row['الوقف 🛡️']}\n⚖️ *R:R:* 1:{row['raw_rr']:.1f}\n\n🤖 _Masa Quant System V83_"
                                try: requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_chat, "text": msg, "parse_mode": "Markdown"}); st.session_state.tg_sent.add(alert_id)
                                except: pass

                            rr_disp = f"⚖️ العائد للمخاطرة R:R = 1 : {row['raw_rr']:.1f}"
                            card = f"<div class='vip-card'><div class='vip-crown'>👑</div><div class='vip-title'>{row['الشركة']}</div><div class='vip-time'>{str(row['raw_time'])}</div><br><div class='vip-rr'>{rr_disp}</div><div class='vip-price'>{row['السعر']} <span style='font-size:16px; color:#aaa; font-weight:normal;'>{currency}</span></div><div class='vip-details'><div>الهدف 🎯<br><span class='vip-target'>{row['الهدف 🎯']}</span></div><div>الوقف (ATR) 🛡️<br><span class='vip-stop'>{row['الوقف 🛡️']}</span></div></div><div style='margin-bottom: 15px;'>{row['الحالة اللحظية ⚡']}</div><div style='background:rgba(33,150,243,0.1); padding:10px; border-radius:8px; border:1px solid rgba(33,150,243,0.3); font-size:14px; margin-bottom:15px; color:#00d2ff;'>📦 الكمية/العقد: <b>{shares_str}</b><br>💵 التكلفة: <b>{pos_value_str}</b></div><div class='vip-score'>التقييم: {row['raw_score']}/100</div></div>"
                            cards_html += card
                        cards_html += "</div>"
                        st.markdown(cards_html, unsafe_allow_html=True)
                    else: st.markdown(f"<div class='empty-box'>👑 الصندوق مغلق حالياً!<br><br>محرك الصناديق يمنع الصفقات التي تعاكس الفريم الأكبر، أو لا تحقق (عائد ضعفين للمخاطرة). 🔒</div>", unsafe_allow_html=True)
                else: st.markdown("<div class='empty-box'>السوق لا يحتوي على فرص. الصندوق الأسود يبحث فقط عن الصفقات الآمنة المتوافقة زمنياً.</div>", unsafe_allow_html=True)

            with tab_whales:
                st.markdown("<h3 style='text-align: center; color: #00d2ff; font-weight: bold;'>🧲 رادار تدفق السيولة (أثر الحيتان)</h3>", unsafe_allow_html=True)
                
                if not df_loads.empty:
                    df_w = pd.DataFrame(df_loads).copy()
                    df_w['acc_score'] = df_w['raw_3d'] + df_w['raw_5d'] + df_w['raw_10d']
                    df_acc = df_w[(df_w['raw_3d'] > 0) & (df_w['raw_5d'] > 0) & (df_w['raw_10d'] > 0)]
                    df_acc = df_acc.sort_values(by=['acc_score'], ascending=False).head(10)
                    df_dist = df_w[(df_w['raw_3d'] < 0) & (df_w['raw_5d'] < 0) & (df_w['raw_10d'] < 0)]
                    df_dist = df_dist.sort_values(by=['acc_score'], ascending=True).head(10)
                    
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        st.markdown("<div style='background:rgba(0, 230, 118, 0.15); border:1px solid #00E676; padding:10px; text-align:center; border-radius:8px; margin-bottom:10px;'><h4 style='color:#00E676; margin:0;'>🟩 أقوى 10 أصول (تجميع مؤسساتي)</h4><span style='font-size:12px; color:white;'>المال الذكي يشتري بهدوء</span></div>", unsafe_allow_html=True)
                        if not df_acc.empty:
                            acc_html = "<table class='whale-table whale-acc' dir='rtl'><tr><th>الأصل</th><th>3 فترات</th><th>5 فترات</th><th>10 فترات</th><th>حالة الحوت</th></tr>"
                            for _, r in df_acc.iterrows():
                                acc_html += f"<tr><td style='color:#00d2ff;'>{r['الشركة']}</td><td><span style='color:#00E676;'>+{r['raw_3d']:.2f}%</span></td><td><span style='color:#00E676;'>+{r['raw_5d']:.2f}%</span></td><td><span style='color:#00E676;'>+{r['raw_10d']:.2f}%</span></td><td>🔥 تجميع</td></tr>"
                            acc_html += "</table>"
                            st.markdown(acc_html, unsafe_allow_html=True)
                        else: st.markdown("<div class='empty-box' style='border-color:#00E676;'>لا توجد عمليات تجميع واضحة حالياً.</div>", unsafe_allow_html=True)

                    with col_w2:
                        st.markdown("<div style='background:rgba(255, 82, 82, 0.15); border:1px solid #FF5252; padding:10px; text-align:center; border-radius:8px; margin-bottom:10px;'><h4 style='color:#FF5252; margin:0;'>🟥 أضعف 10 أصول (تصريف دموي)</h4><span style='font-size:12px; color:white;'>المال الذكي يهرب تدريجياً</span></div>", unsafe_allow_html=True)
                        if not df_dist.empty:
                            dist_html = "<table class='whale-table whale-dist' dir='rtl'><tr><th>الأصل</th><th>3 فترات</th><th>5 فترات</th><th>10 فترات</th><th>حالة الحوت</th></tr>"
                            for _, r in df_dist.iterrows():
                                dist_html += f"<tr><td style='color:#00d2ff;'>{r['الشركة']}</td><td><span style='color:#FF5252;'>{r['raw_3d']:.2f}%</span></td><td><span style='color:#FF5252;'>{r['raw_5d']:.2f}%</span></td><td><span style='color:#FF5252;'>{r['raw_10d']:.2f}%</span></td><td>🩸 تصريف</td></tr>"
                            dist_html += "</table>"
                            st.markdown(dist_html, unsafe_allow_html=True)
                        else: st.markdown("<div class='empty-box' style='border-color:#FF5252;'>لا توجد عمليات تصريف واضحة حالياً.</div>", unsafe_allow_html=True)
                else: st.info("لا توجد بيانات كافية.")

            with tab_ai:
                if not df_ai_picks.empty:
                    df_ai_disp = pd.DataFrame(df_ai_picks).sort_values(by="Score 💯", ascending=False)
                    html_ai = "<table class='ai-table' dir='rtl'><tr><th>الأصل</th><th>السعر</th><th>Score 💯</th><th>الحالة اللحظية ⚡</th><th>القرار 🚦</th><th style='width:35%; text-align:right;'>تحليل الخوارزمية (أشعة إكس 🧠)</th></tr>"
                    for _, row in df_ai_disp.iterrows():
                        reasons_html = "".join([f"<div style='font-size:12px; margin-bottom:5px; line-height:1.5; color:#bbb;'>{r}</div>" for r in row['raw_reasons']])
                        html_ai += f"<tr><td style='color:#00d2ff; font-weight:bold; font-size:15px;'>{row['الشركة']}</td><td>{row['السعر']}</td><td style='color:{row['اللون']}; font-size:18px; font-weight:bold;'>{row['Score 💯']}/100</td><td>{row['الحالة اللحظية ⚡']}</td><td style='color:{row['اللون']};'><span class='rec-badge' style='background-color:{row['اللون']}20; border:1px solid {row['اللون']}50;'>{row['التوصية 🚦']}</span></td><td style='text-align:right; padding:10px 15px; border-right: 2px solid {row['اللون']}50;'>{reasons_html}</td></tr>"
                    html_ai += "</table>"
                    st.markdown(html_ai, unsafe_allow_html=True)
                else: st.markdown(f"<div class='empty-box'>📉 لا توجد أصول.</div>", unsafe_allow_html=True)

            with tab1:
                c1, c2, c3, c4 = st.columns(4)
                show_3d = c1.checkbox(f"عرض 3 {lbl} 🟠", value=True)
                show_4d = c2.checkbox(f"عرض 4 {lbl} 🟢", value=False)
                show_10d = c3.checkbox(f"عرض 10 {lbl} 🟣", value=True)
                show_15d = c4.checkbox(f"عرض 15 {lbl} 🔴", value=False)
                
                df_plot2 = df.tail(150).copy()
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2['Close'], mode='lines+markers', name='السعر', line=dict(color='dodgerblue', width=2), marker=dict(size=5)))
                
                def add_channel(fig, h_col, l_col, color, dash, name, marker_color, marker_size, symbol_up, symbol_dn):
                    if h_col in df_plot2.columns and l_col in df_plot2.columns:
                        fig.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2[h_col], line=dict(color=color, width=1.5, dash=dash, shape='hv'), name=f'مقاومة {name}'))
                        fig.add_trace(go.Scatter(x=df_plot2.index, y=df_plot2[l_col], line=dict(color=color, width=1.5, dash=dash, shape='hv'), name=f'دعم {name}'))
                        bo_up = df_plot2[(df_plot2['Close'] > df_plot2[h_col]) & (df_plot2['Close'].shift(1) <= df_plot2[h_col].shift(1))]
                        bo_dn = df_plot2[(df_plot2['Close'] < df_plot2[l_col]) & (df_plot2['Close'].shift(1) >= df_plot2[l_col].shift(1))]
                        fig.add_trace(go.Scatter(x=bo_up.index, y=bo_up['Close'], mode='markers', marker=dict(symbol=symbol_up, size=marker_size, color=marker_color, line=dict(width=1, color='black')), name=f'اختراق {name}'))
                        fig.add_trace(go.Scatter(x=bo_dn.index, y=bo_dn['Close'], mode='markers', marker=dict(symbol=symbol_dn, size=marker_size, color='red', line=dict(width=1, color='black')), name=f'كسر {name}'))
                
                if show_3d: add_channel(fig2, 'High_3D', 'Low_3D', 'orange', 'dot', f'3 {lbl}', 'orange', 12, 'triangle-up', 'triangle-down')
                if show_4d: add_channel(fig2, 'High_4D', 'Low_4D', '#4caf50', 'dash', f'4 {lbl}', '#4caf50', 12, 'triangle-up', 'triangle-down')
                if show_10d: add_channel(fig2, 'High_10D', 'Low_10D', '#9c27b0', 'solid', f'10 {lbl}', '#9c27b0', 14, 'diamond', 'diamond-tall')
                if show_15d: add_channel(fig2, 'High_15D', 'Low_15D', '#f44336', 'dashdot', f'15 {lbl}', '#f44336', 16, 'star', 'star-triangle-down')
                
                fig2.update_layout(height=650, hovermode='x unified', template='plotly_dark', margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                if selected_interval != "1d": 
                    if is_crypto_main: pass
                    elif is_fx_main: fig2.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
                    else: fig2.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[16, 9], pattern="hour")])
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

            with tab5:
                if not df_loads.empty:
                    df_loads_styled = pd.DataFrame(df_loads).copy()
                    try:
                        if col_change_name in df_loads_styled.columns and '1d_cat' in df_loads_styled.columns:
                            df_loads_styled[col_change_name] = df_loads_styled.apply(lambda x: format_cat(x[col_change_name], x['1d_cat']), axis=1)
                        if f'تراكمي 3 {lbl}' in df_loads_styled.columns and '3d_cat' in df_loads_styled.columns:
                            df_loads_styled[f'تراكمي 3 {lbl}'] = df_loads_styled.apply(lambda x: format_cat(x[f'تراكمي 3 {lbl}'], x['3d_cat']), axis=1)
                        if f'تراكمي 5 {lbl}' in df_loads_styled.columns and '5d_cat' in df_loads_styled.columns:
                            df_loads_styled[f'تراكمي 5 {lbl}'] = df_loads_styled.apply(lambda x: format_cat(x[f'تراكمي 5 {lbl}'], x['5d_cat']), axis=1)
                        if f'تراكمي 10 {lbl}' in df_loads_styled.columns and '10d_cat' in df_loads_styled.columns:
                            df_loads_styled[f'تراكمي 10 {lbl}'] = df_loads_styled.apply(lambda x: format_cat(x[f'تراكمي 10 {lbl}'], x['10d_cat']), axis=1)
                        
                        df_loads_styled = df_loads_styled.drop(columns=['1d_cat', '3d_cat', '5d_cat', '10d_cat', 'raw_3d', 'raw_5d', 'raw_10d'], errors='ignore')
                        df_loads_styled = df_loads_styled.fillna('')
                        subset_cols = [c for c in [col_change_name, f'حالة 3 {lbl}', f'تراكمي 3 {lbl}', f'حالة 5 {lbl}', f'تراكمي 5 {lbl}', f'حالة 10 {lbl}', f'تراكمي 10 {lbl}'] if c in df_loads_styled.columns]
                        
                        if subset_cols:
                            styler_loads = df_loads_styled.style.applymap(safe_color_table, subset=subset_cols) if hasattr(df_loads_styled.style, 'applymap') else df_loads_styled.style.map(safe_color_table, subset=subset_cols)
                            st.dataframe(styler_loads, use_container_width=True, height=550)
                        else: 
                            st.dataframe(df_loads_styled.astype(str), use_container_width=True, height=550)
                    except Exception as e:
                        df_safe = df_loads_styled.drop(columns=['1d_cat', '3d_cat', '5d_cat', '10d_cat', 'raw_3d', 'raw_5d', 'raw_10d'], errors='ignore')
                        st.dataframe(df_safe.astype(str), use_container_width=True, height=550)
                else: 
                    st.markdown("<div class='empty-box'>📭 لا توجد بيانات للتحليل.</div>", unsafe_allow_html=True)

            with tab6:
                if not df_alerts.empty:
                    df_alerts_disp = pd.DataFrame(df_alerts).fillna('')
                    try:
                        if 'التنبيه' in df_alerts_disp.columns:
                            styler_alerts = df_alerts_disp.style.applymap(safe_color_table, subset=['التنبيه']) if hasattr(df_alerts_disp.style, 'applymap') else df_alerts_disp.style.map(safe_color_table, subset=['التنبيه'])
                            st.dataframe(styler_alerts, use_container_width=True, height=550)
                        else: 
                            st.dataframe(df_alerts_disp.astype(str), use_container_width=True, height=550)
                    except:
                        st.dataframe(df_alerts_disp.astype(str), use_container_width=True, height=550)
                else: 
                    st.markdown(f"<div class='empty-box'>لم يتم رصد أي اختراقات أو كسور في السوق.</div>", unsafe_allow_html=True)

            # ⏳ V83: تفعيل مختبر الباك تيست للتاريخ المفصلي
            with tab_backtest:
                st.markdown(f"<h3 style='text-align: center; color: #FFD700;'>⏳ السجل التاريخي لـ ({display_name})</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: gray;'>يقوم هذا المحرك بفحص آخر 150 شمعة واستخراج الأحداث المفصلية التي مرت على السهم لاختبار قوته التاريخية.</p>", unsafe_allow_html=True)
                
                try:
                    df_bt = df.tail(150).copy()
                    bt_logs = []
                    for i in range(1, len(df_bt)):
                        prev = df_bt.iloc[i-1]
                        curr = df_bt.iloc[i]
                        
                        try: t_str = df_bt.index[i].strftime('%Y-%m-%d | %H:%M') if selected_interval != '1d' else df_bt.index[i].strftime('%Y-%m-%d')
                        except: t_str = str(df_bt.index[i])[:16]
                        
                        if pd.notna(curr.get('ZR_High')) and pd.notna(prev.get('ZR_High')):
                            if curr['Close'] > curr['ZR_High'] and prev['Close'] <= prev['ZR_High']:
                                bt_logs.append({"التاريخ والوقت": t_str, "السعر": format_price(curr['Close'], ticker), "الحدث التاريخي": "🚀 اختراق سقف زيرو 👑"})
                        
                        if pd.notna(curr.get('ZR_Low')) and pd.notna(prev.get('ZR_Low')):
                            if curr['Close'] < curr['ZR_Low'] and prev['Close'] >= prev['ZR_Low']:
                                bt_logs.append({"التاريخ والوقت": t_str, "السعر": format_price(curr['Close'], ticker), "الحدث التاريخي": "🩸 كسر قاع زيرو (انهيار) 🕳️"})
                        
                        if pd.notna(curr.get('SMA_50')) and pd.notna(prev.get('SMA_50')):
                            if curr['Close'] > curr['SMA_50'] and prev['Close'] <= prev['SMA_50']:
                                bt_logs.append({"التاريخ والوقت": t_str, "السعر": format_price(curr['Close'], ticker), "الحدث التاريخي": "🟢 اختراق متوسط 50"})
                            elif curr['Close'] < curr['SMA_50'] and prev['Close'] >= prev['SMA_50']:
                                bt_logs.append({"التاريخ والوقت": t_str, "السعر": format_price(curr['Close'], ticker), "الحدث التاريخي": "🔴 كسر متوسط 50"})
                    
                    if bt_logs:
                        df_bt_res = pd.DataFrame(bt_logs).iloc[::-1]
                        df_bt_res.set_index("التاريخ والوقت", inplace=True)
                        styler_bt = df_bt_res.style.applymap(safe_color_table, subset=['الحدث التاريخي']) if hasattr(df_bt_res.style, 'applymap') else df_bt_res.style.map(safe_color_table, subset=['الحدث التاريخي'])
                        st.dataframe(styler_bt, use_container_width=True, height=500)
                    else:
                        st.info("لم يمر السهم بأي أحداث مفصلية (اختراق/كسر) خلال الـ 150 شمعة الماضية، مساره كان عرضياً أو مستقراً.")
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ في بناء الباك تيست: {str(e)}")

            # 📂 V83: تفعيل محفظة المراقبة (Watchlist)
            with tab_track:
                st.markdown("<h3 style='text-align: center; color: #00d2ff;'>📂 محفظة المراقبة (سجل صفقات الـ VIP)</h3>", unsafe_allow_html=True)
                try:
                    conn = sqlite3.connect(DB_FILE)
                    df_saved = pd.read_sql_query("SELECT date_time AS 'وقت الرصد', market AS 'السوق', ticker AS 'الرمز', company AS 'الشركة', entry AS 'سعر الدخول', target AS 'الهدف', stop_loss AS 'الوقف', score AS 'التقييم', mom AS 'الزخم' FROM tracker ORDER BY date_time DESC", conn)
                    if not df_saved.empty:
                        st.dataframe(df_saved, use_container_width=True)
                        col_del1, col_del2, col_del3 = st.columns([1,1,1])
                        with col_del2:
                            if st.button("🗑️ مسح السجل بالكامل", type="secondary", use_container_width=True):
                                cur = conn.cursor()
                                cur.execute("DELETE FROM tracker")
                                conn.commit()
                                st.rerun() if hasattr(st, 'rerun') else st.experimental_rerun()
                    else:
                        st.info("📂 المحفظة فارغة حالياً. اذهب إلى (👑 VIP ماسة) واضغط على زر [حفظ هذه الفرص] لإضافتها هنا.")
                except Exception as e:
                    st.error("حدث خطأ في قراءة قاعدة البيانات.")
                finally:
                    if 'conn' in locals(): conn.close()

            with tab2:
                if is_fx_main:
                    tv_ticker = ticker.replace('=X', '')
                    if len(tv_ticker) == 3: tv_ticker = "USD" + tv_ticker
                    tv_symbol = f"FX:{tv_ticker}"
                elif is_crypto_main:
                    tv_ticker = ticker.replace('-USD', '')
                    tv_symbol = f"BINANCE:{tv_ticker}USDT"
                elif "السعودي" in market_choice:
                    tv_ticker = ticker.replace('.SR', '')
                    tv_symbol = f"TADAWUL:{tv_ticker}"
                else:
                    tv_symbol = ticker
                
                tz = "Asia/Riyadh"
                tv_interval_tv = "D" if selected_interval == "1d" else selected_interval.replace("m", "")
                tradingview_html = f"""<div class="tradingview-widget-container" style="height:700px;width:100%"><div id="tradingview_masa" style="height:100%;width:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true,"symbol": "{tv_symbol}","interval": "{tv_interval_tv}","timezone": "{tz}","theme": "dark","style": "1","locale": "ar_AE","enable_publishing": false,"backgroundColor": "#1a1c24","gridColor": "#2d303e","hide_top_toolbar": false,"hide_legend": false,"save_image": false,"container_id": "tradingview_masa","toolbar_bg": "#1e2129","studies": ["Volume@tv-basicstudies","RSI@tv-basicstudies","MASimple@tv-basicstudies","VWAP@tv-basicstudies"]}});</script></div>"""
                components.html(tradingview_html, height=700)

            with tab3:
                df_plot = df.tail(150) if selected_interval != '1d' else df.tail(300)
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
                
                fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='السعر'), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_200'], line=dict(color='#9c27b0', width=2), name='MA 200'), row=1, col=1) 
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], line=dict(color='#00bcd4', width=2), name='MA 50'), row=1, col=1)  
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['VWAP'], line=dict(color='#ffeb3b', width=2, dash='dot'), name='VWAP (خط الحيتان)'), row=1, col=1)
                
                current_zr_high = df['ZR_High'].iloc[-1] if pd.notna(df['ZR_High'].iloc[-1]) else df_plot['High'].max()
                current_zr_low = df['ZR_Low'].iloc[-1] if pd.notna(df['ZR_Low'].iloc[-1]) else df_plot['Low'].min()
                
                fig.add_trace(go.Scatter(
                    x=df_plot.index, 
                    y=[current_zr_high] * len(df_plot), 
                    mode='lines', line=dict(color='white', width=4, dash='30px,15px'), 
                    name=f'سقف زيرو', hoverinfo='skip'
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=df_plot.index, 
                    y=[current_zr_low] * len(df_plot), 
                    mode='lines', line=dict(color='orange', width=4, dash='30px,15px'), 
                    name=f'قاع زيرو', hoverinfo='skip'
                ), row=1, col=1)
                
                tv_tf = selected_interval.replace('m', '').replace('1d', 'D')
                fig.add_annotation(
                    x=df_plot.index[-min(10, len(df_plot)-1)], y=current_zr_high,
                    text=f"<b>ZR | Used: 300 | TF: {tv_tf}</b><br>High: {current_zr_high:.4f}<br>Low: {current_zr_low:.4f}",
                    showarrow=False, yshift=30, font=dict(color="white", size=10, family="Courier New"),
                    bgcolor="rgba(26, 28, 36, 0.85)", bordercolor="rgba(255, 255, 255, 0.4)", borderwidth=1, borderpad=5
                )
                
                colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df_plot.iterrows()]
                fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='السيولة'), row=2, col=1)
                
                fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='purple', width=2), name='RSI 14'), row=3, col=1)
                
                fig.add_hline(y=70, line_dash="dot", row=3, col=1, line_color="red")
                fig.add_hline(y=50, line_dash="solid", row=3, col=1, line_color="gray", opacity=0.5) 
                fig.add_hline(y=30, line_dash="dot", row=3, col=1, line_color="green")
                
                fig.update_layout(height=800, template='plotly_dark', showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
                
                if selected_interval != "1d": 
                    if is_crypto_main: pass
                    elif is_fx_main: fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
                    else: fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[16, 9], pattern="hour")])
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # 🛡️📋 V83: بناء الجدول المدرع ضد الأخطاء 
            with tab4:
                st.markdown("<h3 style='text-align: center; color: #00d2ff;'>📋 البيانات التاريخية المفصلة</h3>", unsafe_allow_html=True)
                df_display = df.tail(20).iloc[::-1].copy()
                
                # بناء أعمدة الجدول حبة حبة في قوالب آمنة لضمان عدم الانهيار مهما كان شكل التاريخ
                time_list = []
                for d in df_display.index:
                    try:
                        if selected_interval == '1d': time_list.append(d.strftime('%Y-%m-%d | 00:00'))
                        else: time_list.append(d.strftime('%Y-%m-%d | %H:%M'))
                    except: 
                        time_list.append(str(d)[:16])
                
                table_data = {'الوقت': time_list}
                
                def safe_fmt(val, tk):
                    try: return format_price(val, tk)
                    except: return "0.00"
                    
                def safe_int(val):
                    try: return str(int(val)) if pd.notna(val) else "0"
                    except: return "0"
                    
                def safe_cat(val):
                    try: return format_cat(val, get_cat(val))
                    except: return ""

                table_data['الإغلاق'] = [safe_fmt(x, ticker) for x in df_display['Close']]
                
                if 'VWAP' in df_display.columns:
                    table_data['VWAP 🐋'] = [safe_fmt(x, ticker) for x in df_display['VWAP']]
                else:
                    table_data['VWAP 🐋'] = [safe_fmt(x, ticker) for x in df_display['Close']]
                    
                table_data['الاتجاه'] = [safe_int(x) for x in df_display.get('Counter', pd.Series([0]*len(df_display)))]
                table_data['MA 50'] = [safe_fmt(x, ticker) for x in df_display.get('SMA_50', pd_display['Close'])]
                table_data['MA 200'] = [safe_fmt(x, ticker) for x in df_display.get('SMA_200', df_display['Close'])]
                
                table_data[col_change_name] = [safe_cat(x) for x in df_display.get('1d_%', pd.Series([0]*len(df_display)))]
                table_data[f'تراكمي 3 {lbl}'] = [safe_cat(x) for x in df_display.get('3d_%', pd.Series([0]*len(df_display)))]
                table_data[f'تراكمي 5 {lbl}'] = [safe_cat(x) for x in df_display.get('5d_%', pd.Series([0]*len(df_display)))]
                table_data[f'تراكمي 10 {lbl}'] = [safe_cat(x) for x in df_display.get('10d_%', pd.Series([0]*len(df_display)))]
                
                if not is_fx_main and not is_crypto_main:
                    def safe_vol(val):
                        try: return f"{int(val):,}" if pd.notna(val) else "0"
                        except: return "0"
                    table_data['حجم السيولة'] = [safe_vol(x) for x in df_display.get('Volume', pd.Series([0]*len(df_display)))]

                try:
                    final_df = pd.DataFrame(table_data)
                    final_df.set_index('الوقت', inplace=True)
                    
                    subset_data = [col_change_name, f'تراكمي 3 {lbl}', f'تراكمي 5 {lbl}', f'تراكمي 10 {lbl}']
                    existing_cols = [c for c in subset_data if c in final_df.columns]
                    
                    if existing_cols:
                        styler = final_df.style.applymap(safe_color_table, subset=existing_cols) if hasattr(final_df.style, 'applymap') else final_df.style.map(safe_color_table, subset=existing_cols)
                        st.dataframe(styler, use_container_width=True, height=600)
                    else:
                        st.dataframe(final_df.astype(str), use_container_width=True, height=600)
                except Exception as e:
                    # جدار حماية المستحيل
                    st.error("حدث خطأ في تنسيق الجدول، يتم عرض البيانات الأساسية.")
                    st.dataframe(df_display, use_container_width=True, height=600)
