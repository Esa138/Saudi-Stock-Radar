import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import datetime
import os
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# ==========================================
# 💎 1. إعدادات الهوية وملف التتبع
# ==========================================
st.set_page_config(page_title="منصة ماسة 💎 | Masa Quant", layout="wide", page_icon="💎", initial_sidebar_state="collapsed")

TRACKER_FILE = "masa_tracker.csv"

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

/* 🧠 تصميم الذكاء الاصطناعي */
.ai-box { background: linear-gradient(145deg, #12141a, #1a1c24); border-top: 4px solid #00d2ff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(0,210,255,0.15);}
.ai-header-flex { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d303e; padding-bottom: 15px; margin-bottom: 15px;}
.ai-title { color: #00d2ff; font-weight: bold; font-size: 22px; margin: 0;}
.ai-score-circle { width: 90px; height: 90px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; border: 4px solid; background-color: rgba(0,0,0,0.3); box-shadow: 0 0 15px currentColor;}
.ai-score-num { font-size: 32px; font-weight: 900; line-height: 1; margin-top: 5px;}
.ai-score-max { font-size: 14px; font-weight: 400; opacity: 0.7; margin-bottom: 5px;}
.ai-decision-text { font-size: 32px; font-weight: 900; margin-bottom: 20px; text-align: center; background-color: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; border: 2px solid; letter-spacing: 1px;}
.ai-reason-item { font-size: 15px; color: #e0e0e0; margin-bottom: 10px; line-height: 1.6; padding-right: 15px; border-right: 3px solid #2d303e;}
.ai-table { width: 100%; text-align: center; border-collapse: collapse; margin-top: 10px; background-color: #1e2129; border-radius: 8px; overflow: hidden;}
.ai-table th { background-color: #2d303e; color: white; padding: 12px; font-size: 14px;}
.ai-table td { padding: 12px; border-bottom: 1px solid #2d303e; font-size: 14px; vertical-align: middle; font-weight:bold;}
.bo-badge { font-weight: bold; padding: 4px 10px; border-radius: 6px; font-size: 12px; display: inline-block; white-space: nowrap; margin: 2px;}
.target-text { color: #00E676; font-weight: bold; font-size: 14px; }
.sl-text { color: #FF5252; font-weight: bold; font-size: 14px; }
.rec-badge { font-weight:900; font-size:14px; padding:6px 12px; border-radius:8px;}

/* 👑 تصميم VIP ماسة */
.vip-container { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-top: 20px; margin-bottom: 30px; }
.vip-card { background: linear-gradient(135deg, #2b2302 0%, #1a1c24 100%); border: 1px solid #ffd700; border-top: 4px solid #ffd700; padding: 25px 20px; border-radius: 15px; width: 31%; min-width: 280px; box-shadow: 0 10px 20px rgba(255, 215, 0, 0.1); transition: transform 0.3s ease; text-align: center; position: relative; overflow: hidden;}
.vip-card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(255, 215, 0, 0.25); }
.vip-crown { position: absolute; top: -15px; right: -15px; font-size: 60px; transform: rotate(15deg); opacity: 0.1; }
.vip-title { color: #ffd700; font-size: 26px; font-weight: 900; margin-bottom: 5px; }
.vip-time { font-size: 13px; color: #aaa; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; display: inline-block; border: 1px solid rgba(255,255,255,0.1);}
.vip-price { font-size: 32px; color: white; font-weight: bold; margin-bottom: 15px; }
.vip-details { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 15px; background: rgba(0,0,0,0.4); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 215, 0, 0.2);}
.vip-target { color: #00e676; font-weight: 900; font-size: 18px;}
.vip-stop { color: #ff5252; font-weight: 900; font-size: 18px;}
.vip-score { background: #ffd700; color: black; padding: 8px 20px; border-radius: 20px; font-weight: 900; font-size: 18px; display: inline-block; margin-top: 15px; box-shadow: 0 4px 10px rgba(255, 215, 0, 0.4);}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 🇸🇦 القاموس السعودي
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

# 🇺🇸 القاموس الأمريكي
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

def get_stock_name(ticker):
    if ticker in SAUDI_NAMES: return SAUDI_NAMES[ticker]
    if ticker in US_NAMES: return US_NAMES[ticker]
    return ticker.replace('.SR', '')

# ==========================================
# 🗄️ دالة حفظ الأداء (Paper Trading)
# ==========================================
def save_to_tracker(df_vip, market):
    if df_vip.empty: return False
    
    records = []
    for _, row in df_vip.iterrows():
        records.append({
            "تاريخ الرصد": row['raw_time'],
            "السوق": market,
            "الرمز": row['الرمز'],
            "الشركة": row['الشركة'],
            "سعر الدخول": row['السعر'],
            "الهدف": row['raw_target'],
            "الوقف": row['raw_sl'],
            "التقييم": row['raw_score'],
            "الزخم": row['raw_mom']
        })
    df_new = pd.DataFrame(records)
    df_new['Date_Only'] = df_new['تاريخ الرصد'].apply(lambda x: str(x).split(' | ')[0])
    
    if os.path.exists(TRACKER_FILE):
        df_old = pd.read_csv(TRACKER_FILE)
        if 'Date_Only' not in df_old.columns:
            df_old['Date_Only'] = df_old['تاريخ الرصد'].apply(lambda x: str(x).split(' | ')[0] if pd.notna(x) else "")
            
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        # منع تكرار نفس السهم في نفس اليوم
        df_combined = df_combined.drop_duplicates(subset=['Date_Only', 'الرمز'], keep='last')
        df_combined.to_csv(TRACKER_FILE, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(TRACKER_FILE, index=False, encoding='utf-8-sig')
    return True

# ==========================================
# 📊 2. محركات التقييم 
# ==========================================
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

def get_ai_analysis(last_close, ma50, ma200, rsi, counter, zr_low, zr_high, event_text, bo_score_add, mom_score, vol_accel_ratio, pct_1d):
    if pd.isna(ma50) or pd.isna(ma200): return 0, "انتظار ⏳", "gray", ["بيانات غير كافية للتحليل."]
    tech_score = 50
    reasons = []
    
    is_macro_bull = last_close > ma200
    is_micro_bull = last_close > ma50
    is_bleeding = counter < 0 or "كسر" in event_text or "سلبي" in event_text or "تصحيح" in event_text or "هابط" in event_text
    dist_ma50 = ((last_close - ma50) / ma50) * 100 if is_micro_bull else ((ma50 - last_close) / ma50) * 100
    dist_ma200 = ((ma200 - last_close) / ma200) * 100 if not is_macro_bull else 0
    
    veto_max_59 = False; veto_max_79 = False; golden_watch = False

    if is_macro_bull: tech_score += 15; reasons.append("✅ <b>الاتجاه العام:</b> السهم يتداول في أمان استثماري (فوق MA 200).")
    else: 
        if is_micro_bull and mom_score >= 70 and not is_bleeding:
            golden_watch = True; tech_score += 5; reasons.append(f"👀 <b>مرحلة تعافي:</b> السهم تحت MA200 لكنه يظهر زخماً للارتداد.")
        else:
            tech_score -= 25; veto_max_59 = True; reasons.append("❌ <b>الاتجاه العام:</b> السهم ينهار تحت متوسط 200 (مسار هابط).")

    if vol_accel_ratio >= 1.2 and pct_1d > 0 and not is_bleeding:
        tech_score += 15; reasons.append(f"🌊 <b>تسارع السيولة:</b> دخول سيولة مؤسساتية.")
        if veto_max_59 and mom_score >= 60: veto_max_59 = False; veto_max_79 = True
    elif vol_accel_ratio < 0.7: tech_score -= 5; reasons.append("❄️ <b>جفاف السيولة:</b> التداولات ضعيفة جداً.")

    if is_micro_bull:
        if dist_ma50 <= 3.5 and not is_bleeding: tech_score += 15; reasons.append("💎 <b>نقطة الدخول:</b> ارتداد إيجابي آمن من دعم MA50.")
        elif dist_ma50 <= 3.5 and is_bleeding: tech_score += 0; veto_max_79 = True; reasons.append("⏳ <b>اختبار الدعم:</b> ننتظر الارتداد لتجنب السكين الساقطة.")
        elif dist_ma50 > 8.0: tech_score -= 10; veto_max_79 = True; reasons.append(f"⚠️ <b>التضخم:</b> السعر ابتعد عن الدعم بنسبة {dist_ma50:.1f}%.")
        else: tech_score += 10; reasons.append("✅ <b>زخم المضاربة:</b> ثبات صحي فوق MA50.")
    else:
        if not golden_watch: tech_score -= 20; veto_max_59 = True; reasons.append("🔴 <b>زخم المضاربة:</b> كسر لمتوسط 50.")

    if "🚀" in event_text or "🟢" in event_text or "💎" in event_text or "📈" in event_text or "🔥" in event_text: 
        tech_score += 10; reasons.append(f"⚡ <b>الحدث اللحظي:</b> إشارة إيجابية داعمة ({event_text}).")
    elif "🩸" in event_text or "🔴" in event_text or "🛑" in event_text or "⚠️" in event_text or "📉" in event_text: 
        tech_score -= 15; reasons.append(f"⚠️ <b>الحدث اللحظي:</b> ضغط بيعي ({event_text}).")
        if "كسر" in event_text: veto_max_59 = True

    if pd.notna(zr_low) and last_close <= zr_low * 1.05: tech_score += 10; reasons.append("🎯 <b>زيرو انعكاس:</b> السعر يختبر قاع القناة (فرصة ارتداد).")
    elif pd.notna(zr_high) and last_close >= zr_high * 0.97: tech_score -= 15; veto_max_79 = True; reasons.append("🧱 <b>تحذير زيرو:</b> السعر يصطدم بسقف القناة (مقاومة).")

    tech_score = int(max(0, min(100, tech_score)))
    final_score = int((tech_score * 0.4) + (mom_score * 0.6))
    reasons.insert(0, f"📊 <b>زخم السيولة التراكمي:</b> يمتلك السهم قوة اندفاع تقدر بـ <b>{mom_score}/100</b>.")

    if golden_watch and not is_bleeding: final_score = min(max(final_score, 60), 79); reasons.insert(0, "🛡️ <b>[فيتو التعافي]:</b> السهم يتعافى بزخم عالٍ، تم وضعه في قسم (مراقبة).")
    elif not is_macro_bull and not is_micro_bull and is_bleeding: final_score = min(final_score, 59); reasons.insert(0, "🛑 <b>[فيتو الانهيار]:</b> السهم ضعيف جداً، تم إعطاء أمر (تجنب).")
    elif veto_max_59 and not golden_watch: final_score = min(final_score, 59); reasons.insert(0, "🛡️ <b>[فيتو المخاطر]:</b> بسبب كسر الدعوم تم إعطاء أمر (تجنب).")
    elif veto_max_79 or is_bleeding or rsi > 72: final_score = min(final_score, 79); reasons.insert(0, "🛡️ <b>[فيتو الأمان]:</b> لتجنب التعليقة أثناء التصحيح أو المقاومة، تم إعطاء أمر (مراقبة).")

    if final_score >= 80: dec, col = "شراء قوي 🟢", "#00E676"
    elif final_score >= 60: dec, col = "مراقبة 🟡", "#FFD700"
    else: dec, col = "تجنب 🔴", "#FF5252"

    return final_score, dec, col, reasons

# ==========================================
# ⚡ 4. قوائم الأسواق والمسح الآلي
# ==========================================
def get_cat(val):
    if pd.isna(val): return ""
    v = abs(val)
    if v >= 1.0: return "MAJOR"
    elif v >= 0.1: return "HIGH"
    else: return "MEDIUM"

def format_cat(val, cat):
    if pd.isna(val): return ""
    if val > 0: return f"🟢 {val:.2f}% ({cat})"
    elif val < 0: return f"🔴 {val:.2f}% ({cat})"
    return f"⚪ {val:.2f}% ({cat})"

@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol): return yf.Ticker(ticker_symbol).history(period="3y").copy()

@st.cache_data(ttl=1800)
def scan_market(watchlist_list):
    breakouts, breakdowns, recent_up, recent_down = [], [], [], []
    loads_list, alerts_list, ai_picks = [], [], []
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # ⏱️ توقيت مكة المكرمة لحفظه في السجل وتتبعه
    saudi_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    now_time_str = saudi_time.strftime("%I:%M %p")
    full_time_str = saudi_time.strftime("%Y-%m-%d | %I:%M %p")

    for tk in watchlist_list:
        try:
            df_s = yf.Ticker(tk).history(period="1y")
            if len(df_s) > 200:
                c, h, l, vol = df_s['Close'], df_s['High'], df_s['Low'], df_s['Volume']
                stock_name = get_stock_name(tk)
                
                ma50, ma200 = c.rolling(50).mean(), c.rolling(200).mean()
                v_sma20, v_sma10 = vol.rolling(20).mean(), vol.rolling(10).mean()
                
                h3, l3 = h.rolling(3).max().shift(1), l.rolling(3).min().shift(1)
                h4, l4 = h.rolling(4).max().shift(1), l.rolling(4).min().shift(1)
                h10, l10 = h.rolling(10).max().shift(1), l.rolling(10).min().shift(1)
                zr_h, zr_l = h.rolling(300, min_periods=10).max().shift(1), l.rolling(300, min_periods=10).min().shift(1)
                
                up_diff, down_diff = c.diff().clip(lower=0), -1 * c.diff().clip(upper=0)
                rsi = 100 - (100 / (1 + (up_diff.ewm(com=13, adjust=False).mean() / down_diff.ewm(com=13, adjust=False).mean())))
                
                last_c, prev_c, prev2_c = c.iloc[-1], c.iloc[-2], c.iloc[-3]
                last_vol, avg_vol, avg_vol_10 = vol.iloc[-1], v_sma20.iloc[-1], v_sma10.iloc[-1]
                vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1
                vol_accel_ratio = last_vol / avg_vol_10 if avg_vol_10 > 0 else 1

                diff = c.diff()
                direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
                counter = 0; counters = []
                for d in direction:
                    if d == 1: counter = counter + 1 if counter > 0 else 1
                    elif d == -1: counter = counter - 1 if counter < 0 else -1
                    else: counter = 0
                    counters.append(counter)
                cur_count = counters[-1]
                
                if cur_count > 0: recent_up.append({"السهم": stock_name, "تاريخ": df_s.index[-cur_count].strftime("%Y-%m-%d"), "منذ كم صف": cur_count})
                elif cur_count < 0: recent_down.append({"السهم": stock_name, "تاريخ": df_s.index[-abs(cur_count)].strftime("%Y-%m-%d"), "منذ كم صف": abs(cur_count)})

                pct_1d = (last_c / prev_c - 1) * 100 if len(c)>1 and prev_c != 0 else 0
                pct_3d = (last_c / c.iloc[-4] - 1) * 100 if len(c)>3 else 0
                pct_5d = (last_c / c.iloc[-6] - 1) * 100 if len(c)>5 else 0
                pct_10d = (last_c / c.iloc[-11] - 1) * 100 if len(c)>10 else 0

                cat_1d, cat_3d, cat_5d, cat_10d = get_cat(pct_1d), get_cat(pct_3d), get_cat(pct_5d), get_cat(pct_10d)
                loads_list.append({"holding ticker": stock_name,"date Latest Date": df_s.index[-1].strftime("%Y-%m-%d"),"daily direction counter": int(cur_count),"hitting_days": abs(cur_count),"load diff 1d %": pct_1d,"1d_cat": cat_1d,"Top G/L 3Days": "✅" if pct_3d > 0 else "❌","load diff 3d %": pct_3d,"3d_cat": cat_3d,"Top G/L 5Days": "✅" if pct_5d > 0 else "❌","load diff 5d %": pct_5d,"5d_cat": cat_5d,"Top G/L 10days": "✅" if pct_10d > 0 else "❌","load diff 10d %": pct_10d,"10d_cat": cat_10d})

                bo_today, bd_today = [], []
                if last_c > h3.iloc[-1] and prev_c <= h3.iloc[-2]: bo_today.append("3أيام"); alerts_list.append({"ticker": stock_name, "frame": "يومي", "datetime": full_time_str, "filter": "اختراق 3 أيام 🟢"})
                if last_c > h4.iloc[-1] and prev_c <= h4.iloc[-2]: bo_today.append("4أيام")
                if last_c > h10.iloc[-1] and prev_c <= h10.iloc[-2]: bo_today.append("10أيام")
                if bo_today: breakouts.append({"السهم": stock_name, "التاريخ": today_str, "النوع": "+".join(bo_today)})

                if last_c < l3.iloc[-1] and prev_c >= l3.iloc[-2]: bd_today.append("3أيام"); alerts_list.append({"ticker": stock_name, "frame": "يومي", "datetime": full_time_str, "filter": "كسر 3 أيام 🔴"})
                if last_c < l4.iloc[-1] and prev_c >= l4.iloc[-2]: bd_today.append("4أيام")
                if last_c < l10.iloc[-1] and prev_c >= l10.iloc[-2]: bd_today.append("10أيام")
                if bd_today: breakdowns.append({"السهم": stock_name, "التاريخ": today_str, "النوع": "+".join(bd_today)})

                bo_yest, bd_yest = [], []
                if prev_c > h3.iloc[-2] and prev2_c <= h3.iloc[-3]: bo_yest.append("3أيام")
                if prev_c > h4.iloc[-2] and prev2_c <= h4.iloc[-3]: bo_yest.append("4أيام")
                if prev_c > h10.iloc[-2] and prev2_c <= h10.iloc[-3]: bo_yest.append("10أيام")
                if prev_c < l3.iloc[-2] and prev2_c >= l3.iloc[-3]: bd_yest.append("3أيام")
                if prev_c < l4.iloc[-2] and prev2_c >= l4.iloc[-3]: bd_yest.append("4أيام")
                if prev_c < l10.iloc[-2] and prev2_c >= l10.iloc[-3]: bd_yest.append("10أيام")

                events = []
                bo_score_add = 0
                
                if pct_1d > 0 and vol_accel_ratio > 1.2: events.append("تسارع سيولة 🌊🔥"); bo_score_add += 10

                if bo_today: events.append(f"اختراق 🚀 ({'+'.join(bo_today)})"); bo_score_add += 15
                elif bd_today: events.append(f"كسر 🩸 ({'+'.join(bd_today)})"); bo_score_add -= 20
                elif bo_yest and last_c > h3.iloc[-1]: events.append("اختراق أمس 🟢"); bo_score_add += 10
                elif bd_yest and last_c < l3.iloc[-1]: events.append("كسر أمس 🔴"); bo_score_add -= 15
                else:
                    dist_m50 = ((last_c - ma50.iloc[-1])/ma50.iloc[-1]) * 100 if pd.notna(ma50.iloc[-1]) else 100
                    if 0 <= dist_m50 <= 2.5 and cur_count > 0: events.append("ارتداد من MA50 💎"); bo_score_add += 10
                    elif -2.5 <= dist_m50 < 0 and cur_count < 0: events.append("كسر MA50 ⚠️"); bo_score_add -= 15

                if not events:
                    if cur_count > 1: events.append(f"مسار صاعد ({cur_count} أيام) 📈"); bo_score_add += 5
                    elif cur_count < -1: events.append(f"مسار هابط ({abs(cur_count)} أيام) 📉"); bo_score_add -= 5
                    else: events.append("استقرار ➖")

                event_text = " | ".join(events)

                bg_color, text_color, border_color = "transparent", "gray", "gray"
                if any(x in event_text for x in ["🚀", "🟢", "💎", "📈", "🔥"]): bg_color, text_color, border_color = "rgba(0, 230, 118, 0.12)", "#00E676", "rgba(0, 230, 118, 0.5)"
                elif any(x in event_text for x in ["🩸", "🔴", "🛑", "📉"]): bg_color, text_color, border_color = "rgba(255, 82, 82, 0.12)", "#FF5252", "rgba(255, 82, 82, 0.5)"
                elif "⚠️" in event_text: bg_color, text_color, border_color = "rgba(255, 215, 0, 0.12)", "#FFD700", "rgba(255, 215, 0, 0.5)"
                
                ch_badge = f"<span class='bo-badge' style='background-color:{bg_color}; color:{text_color}; border: 1px solid {border_color};'>{event_text}</span>"

                target = zr_h.iloc[-1] if pd.notna(zr_h.iloc[-1]) else last_c * 1.05
                sl = ma50.iloc[-1] if pd.notna(ma50.iloc[-1]) else last_c * 0.95
                if last_c < sl: sl = l3.iloc[-1] if pd.notna(l3.iloc[-1]) else last_c * 0.90

                mom_score = calc_momentum_score(pct_1d, pct_5d, pct_10d, vol_ratio)
                mom_badge = get_mom_badge(mom_score)

                ai_score, ai_dec, ai_col, _ = get_ai_analysis(last_c, ma50.iloc[-1], ma200.iloc[-1], rsi.iloc[-1], cur_count, zr_l.iloc[-1], zr_h.iloc[-1], event_text, bo_score_add, mom_score, vol_accel_ratio, pct_1d)
                
                ai_picks.append({
                    "الشركة": stock_name, 
                    "الرمز": tk,
                    "السعر": round(last_c, 2), 
                    "Score 💯": ai_score, 
                    "الزخم 🌊": mom_badge, 
                    "الحالة اللحظية ⚡": ch_badge, 
                    "الهدف 🎯": f"{target:.2f}", 
                    "الوقف 🛡️": f"{sl:.2f}", 
                    "التوصية 🚦": ai_dec,
                    "وقت الدخول 🕒": f"<span style='color:#aaa; font-size:12px;'>{now_time_str}</span>",
                    "اللون": ai_col,
                    "raw_score": ai_score, 
                    "raw_mom": mom_score,
                    "raw_events": event_text,
                    "raw_time": full_time_str,
                    "raw_target": target,
                    "raw_sl": sl
                })

        except Exception as e: continue
    return pd.DataFrame(breakouts), pd.DataFrame(breakdowns), pd.DataFrame(recent_up), pd.DataFrame(recent_down), pd.DataFrame(loads_list), pd.DataFrame(alerts_list), pd.DataFrame(ai_picks)

# ==========================================
# 🌟 5. واجهة المستخدم والتنقل
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00d2ff; font-weight: bold;'>💎 منصة مـاسـة للتحليل الكمي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-top: -10px; margin-bottom: 30px;'>مستشارك الآلي الخوارزمي | التوصيات المباشرة 🇸🇦🇺🇸</p>", unsafe_allow_html=True)

st.markdown("<div class='search-container'>", unsafe_allow_html=True)
market_choice = st.radio("اختر نطاق الماسح الآلي 🌐:", ["السوق السعودي 🇸🇦", "السوق الأمريكي 🇺🇸"], horizontal=True)

col_empty1, col_search1, col_search2, col_empty2 = st.columns([1, 3, 1, 1])

with col_search1: 
    if "السعودي" in market_choice:
        saudi_display_to_ticker = {f"{name} ({tk.replace('.SR', '')})": tk for tk, name in SAUDI_NAMES.items()}
        options = sorted(list(saudi_display_to_ticker.keys()))
        default_index = options.index('الراجحي (1120)') if 'الراجحي (1120)' in options else 0
        selected_option = st.selectbox("🎯 اختر السهم (ابحث بالاسم أو الرمز):", options, index=default_index, label_visibility="collapsed")
        
        ticker = saudi_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(SAUDI_NAMES.keys())
        currency = "ريال"
    else:
        us_display_to_ticker = {f"{name} ({tk})": tk for tk, name in US_NAMES.items()}
        options = sorted(list(us_display_to_ticker.keys()))
        default_index = options.index('NVIDIA (NVDA)') if 'NVIDIA (NVDA)' in options else 0
        selected_option = st.selectbox("🎯 اختر السهم الأمريكي (ابحث بالاسم أو الرمز):", options, index=default_index, label_visibility="collapsed")
        
        ticker = us_display_to_ticker[selected_option]
        display_name = selected_option.split(" (")[0]
        selected_watchlist = list(US_NAMES.keys())
        currency = "$"

with col_search2: analyze_btn = st.button("استخراج الفرص 💎", use_container_width=True, type="primary")
st.markdown("</div>", unsafe_allow_html=True)

if analyze_btn or ticker:
    with st.spinner(f"جاري مسح السوق وبناء التوصيات لـ ({display_name})... ⏳"):
        
        # 🛡️ المعالجة الآمنة للبيانات لتجنب الخطأ الأحمر
        df = get_stock_data(ticker).copy()
        df_bup, df_bdn, df_recent_up, df_recent_down, df_loads, df_alerts, df_ai_picks = scan_market(selected_watchlist)
        
        if df.empty:
            st.error("❌ السهم غير موجود! تأكد من الرمز المدخل.")
        else:
            close, high, low, vol = df['Close'], df['High'], df['Low'], df['Volume']

            df['SMA_50'] = close.rolling(window=50).mean()
            df['SMA_200'] = close.rolling(window=200).mean() 
            df['Vol_SMA_20'] = vol.rolling(window=20).mean()
            df['Vol_SMA_10'] = vol.rolling(window=10).mean()

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
            
            # إصلاح دالة format_cat التي سقطت
            df['Load_Diff_1D'] = df['1d_%'].apply(lambda x: format_cat(x, get_cat(x)))
            df['Load_Diff_3D'] = df['3d_%'].apply(lambda x: format_cat(x, get_cat(x)))
            df['Load_Diff_5D'] = df['5d_%'].apply(lambda x: format_cat(x, get_cat(x)))
            df['Load_Diff_10D'] = df['10d_%'].apply(lambda x: format_cat(x, get_cat(x)))
            
            diff = close.diff()
            direction = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
            counter = []; curr = 0
            for d in direction:
                if d == 1: curr = curr + 1 if curr > 0 else 1
                elif d == -1: curr = curr - 1 if curr < 0 else -1
                else: curr = 0
                counter.append(curr)
            df['Counter'] = counter
            
            up = diff.clip(lower=0)
            down = -1 * diff.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))

            df['ZR_High'] = high.rolling(window=300, min_periods=10).max().shift(1)
            df['ZR_Low'] = low.rolling(window=300, min_periods=10).min().shift(1)

            last_close, prev_close, prev2_close = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            pct_change = ((last_close - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            
            pct_1d_main = df['1d_%'].iloc[-1] if not pd.isna(df['1d_%'].iloc[-1]) else 0
            pct_5d_main = df['5d_%'].iloc[-1] if not pd.isna(df['5d_%'].iloc[-1]) else 0
            pct_10d_main = df['10d_%'].iloc[-1] if not pd.isna(df['10d_%'].iloc[-1]) else 0
            
            last_sma200, last_sma50 = df['SMA_200'].iloc[-1], df['SMA_50'].iloc[-1]
            last_vol, avg_vol, avg_vol10 = df['Volume'].iloc[-1], df['Vol_SMA_20'].iloc[-1], df['Vol_SMA_10'].iloc[-1]
            last_zr_high, last_zr_low = df['ZR_High'].iloc[-1], df['ZR_Low'].iloc[-1]
            last_rsi, last_counter = df['RSI'].iloc[-1], df['Counter'].iloc[-1]
            
            main_vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1
            main_vol_accel_ratio = last_vol / avg_vol10 if avg_vol10 > 0 else 1

            main_bo_msgs_sys, main_bd_msgs_sys = [], []
            if last_close > df['High_3D'].iloc[-1] and prev_close <= df['High_3D'].iloc[-2]: main_bo_msgs_sys.append("3أيام")
            if last_close > df['High_4D'].iloc[-1] and prev_close <= df['High_4D'].iloc[-2]: main_bo_msgs_sys.append("4أيام")
            if last_close > df['High_10D'].iloc[-1] and prev_close <= df['High_10D'].iloc[-2]: main_bo_msgs_sys.append("10أيام")

            if last_close < df['Low_3D'].iloc[-1] and prev_close >= df['Low_3D'].iloc[-2]: main_bd_msgs_sys.append("3أيام")
            if last_close < df['Low_4D'].iloc[-1] and prev_close >= df['Low_4D'].iloc[-2]: main_bd_msgs_sys.append("4أيام")
            if last_close < df['Low_10D'].iloc[-1] and prev_close >= df['Low_10D'].iloc[-2]: main_bd_msgs_sys.append("10أيام")

            main_events = []
            main_bo_score_add = 0
            
            if pct_1d_main > 0 and main_vol_accel_ratio >= 1.2:
                main_events.append("تسارع سيولة 🌊🔥")
                main_bo_score_add += 10

            if main_bo_msgs_sys: 
                main_events.append("اختراق 🚀 (" + "+".join(main_bo_msgs_sys) + ")")
                main_bo_score_add += 15
            elif main_bd_msgs_sys: 
                main_events.append("كسر 🩸 (" + "+".join(main_bd_msgs_sys) + ")")
                main_bo_score_add -= 20
            elif prev_close > df['High_3D'].iloc[-2] and prev2_close <= df['High_3D'].iloc[-3] and last_close > df['High_3D'].iloc[-1]:
                main_events.append("اختراق أمس 🟢")
                main_bo_score_add += 10
            elif prev_close < df['Low_3D'].iloc[-2] and prev2_close >= df['Low_3D'].iloc[-3] and last_close < df['Low_3D'].iloc[-1]:
                main_events.append("كسر أمس 🔴")
                main_bo_score_add -= 15
            else:
                if pd.notna(last_sma50):
                    main_dist_ma50 = ((last_close - last_sma50)/last_sma50) * 100
                    if 0 <= main_dist_ma50 <= 2.5 and last_counter > 0:
                        main_events.append("ارتداد من MA50 💎")
                        main_bo_score_add += 10
                    elif -2.5 <= main_dist_ma50 < 0 and last_counter < 0:
                        main_events.append("كسر MA50 ⚠️")
                        main_bo_score_add -= 15

            if not main_events:
                if last_counter > 1: main_events.append(f"مسار صاعد ({last_counter} أيام) 📈"); main_bo_score_add += 5
                elif last_counter < -1: main_events.append(f"مسار هابط ({abs(last_counter)} أيام) 📉"); main_bo_score_add -= 5
                else: main_events.append("استقرار ➖")

            main_event_text = " | ".join(main_events)

            if pd.notna(last_sma200) and pd.notna(last_sma50):
                if last_close > last_sma200 and last_close > last_sma50: trend, trend_color = "مسار صاعد 🚀", "🟢"
                elif last_close < last_sma200 and last_close < last_sma50: trend, trend_color = "مسار هابط 🔴", "🔴"
                else: trend, trend_color = "تذبذب (حيرة) ⚖️", "🟡"
            else:
                trend, trend_color = "جاري الحساب...", "⚪"

            vol_status, vol_color = ("تسارع سيولة", "🔥") if main_vol_accel_ratio >= 1.2 else ("سيولة جيدة", "📈") if last_vol > avg_vol else ("سيولة ضعيفة", "❄️")
            zr_status, zr_color = ("يختبر سقف زيرو", "⚠️") if last_close >= last_zr_high * 0.98 else ("يختبر قاع زيرو", "💎") if last_close <= last_zr_low * 1.05 else ("في منتصف القناة", "⚖️")

            st.markdown(f"### 🤖 قراءة استراتيجية ماسة لسهم ({display_name}):")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"الإغلاق الأخير ({currency})", f"{last_close:.2f}", f"{pct_change:.2f}%")
            m2.metric(f"الترند الاستراتيجي {trend_color}", trend)
            m3.metric(f"تدفق السيولة {vol_color}", vol_status)
            m4.metric(f"قراءة زيرو {zr_color}", zr_status)
            st.markdown("<br>", unsafe_allow_html=True)

            tab_vip, tab_track, tab_ai, tab1, tab5, tab6, tab2, tab3, tab4 = st.tabs([
                "👑 VIP ماسة",
                "📂 مراقبة الأداء (Tracker) 🆕",
                "🧠 لوحة التوصيات",
                "🎯 شارت الاختراقات", 
                "🗂️ ماسح السوق (Loads)",
                "🚨 رادار التنبيهات",
                "🌐 TradingView", 
                "📊 شارت الخوارزمية", 
                "📋 بيانات السهم"
            ])

            # ==========================================
            # 👑 1. قسم VIP ماسة
            # ==========================================
            with tab_vip:
                if not df_ai_picks.empty:
                    df_vip_full = pd.DataFrame(df_ai_picks)
                    df_vip = df_vip_full[
                        (df_vip_full['raw_score'] >= 80) & 
                        (df_vip_full['raw_mom'] >= 75) & 
                        (~df_vip_full['raw_events'].str.contains('كسر|هابط|تصحيح'))
                    ].sort_values(by=['raw_score', 'raw_mom'], ascending=[False, False]).head(3)
                    
                    if not df_vip.empty:
                        st.markdown("<h3 style='text-align: center; color: #ffd700; font-weight: 900; margin-bottom: 5px;'>👑 الصندوق الأسود: أقوى الفرص الاستثمارية الآن</h3>", unsafe_allow_html=True)
                        st.markdown("<p style='text-align: center; color: #888; font-size: 15px; margin-bottom: 20px;'>هذه الأسهم اجتازت جميع فلاتر الأمان (السيولة، الزخم، الاتجاه، الدعم) وجاهزة للشراء.</p>", unsafe_allow_html=True)
                        
                        # 💾 زر حفظ الفرص في سجل المراقبة
                        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
                        with col_btn2:
                            if st.button("💾 حفظ هذه التوصيات في سجل المراقبة (Paper Trading)", use_container_width=True):
                                save_to_tracker(df_vip, market_choice)
                                st.success("✅ تم الحفظ بنجاح! راجع تبويب (مراقبة الأداء Tracker).")
                                
                        # 🛡️ بناء البطاقات برمجياً بسطر واحد متصل لمنع تسرب الأكواد!
                        cards_html = "<div class='vip-container'>"
                        for _, row in df_vip.iterrows():
                            card = "<div class='vip-card'><div class='vip-crown'>👑</div><div class='vip-title'>" + str(row['الشركة']) + "</div><div class='vip-time'>⏱️ " + str(row['raw_time']) + "</div><div class='vip-price'>" + f"{row['السعر']:.2f}" + " <span style='font-size:16px; color:#aaa; font-weight:normal;'>" + currency + "</span></div><div class='vip-details'><div>الهدف 🎯<br><span class='vip-target'>" + str(row['الهدف 🎯']) + "</span></div><div>الوقف 🛡️<br><span class='vip-stop'>" + str(row['الوقف 🛡️']) + "</span></div></div><div style='margin-bottom: 15px;'>" + str(row['الحالة اللحظية ⚡']) + "</div><div class='vip-score'>التقييم: " + str(row['raw_score']) + "/100</div></div>"
                            cards_html += card
                        cards_html += "</div>"
                        
                        st.markdown(cards_html, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='vip-empty'>👑 الصندوق مغلق حالياً!<br>لا يوجد أسهم في السوق اليوم تحقق الشروط القاسية (سكور +80 وزخم سيولة عالي). الحفاظ على الكاش هو الأفضل الآن.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='vip-empty'>قم بمسح السوق أولاً لعرض فرص VIP.</div>", unsafe_allow_html=True)

            # ==========================================
            # 📂 2. قسم مراقبة الأداء (Tracker) والمحفظة الوهمية
            # ==========================================
            with tab_track:
                st.markdown("<h3 style='text-align: center; color: #00d2ff; font-weight: bold;'>📂 محفظة المراقبة (Paper Trading)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: gray;'>احفظ أسهم VIP هنا لمراقبة أدائها، واضغط (تحديث الأسعار) لمعرفة دقة التوصيات ونسبة الربح/الخسارة لاحقاً.</p>", unsafe_allow_html=True)
                
                if os.path.exists(TRACKER_FILE):
                    df_track = pd.read_csv(TRACKER_FILE)
                    
                    if not df_track.empty:
                        # 🔄 زر تحديث الأسعار اللحظي لحساب الأرباح
                        if st.button("🔄 تحديث الأسعار وحساب الربح/الخسارة 📊", type="primary", use_container_width=True):
                            with st.spinner("جاري جلب الأسعار اللحظية من السوق..."):
                                current_prices = []
                                pnl_list = []
                                status_list = []
                                
                                for idx, row in df_track.iterrows():
                                    try:
                                        ticker_sym = row['الرمز']
                                        ticker_data = yf.Ticker(ticker_sym).history(period="1d")
                                        if not ticker_data.empty:
                                            cp = ticker_data['Close'].iloc[-1]
                                            entry = row['سعر الدخول']
                                            target = row['الهدف']
                                            stop = row['الوقف']
                                            
                                            current_prices.append(round(cp, 2))
                                            pnl = ((cp - entry) / entry) * 100
                                            pnl_list.append(pnl)
                                            
                                            if cp >= target: status_list.append("✅ حقق الهدف")
                                            elif cp <= stop: status_list.append("❌ ضرب الوقف")
                                            elif pnl > 0: status_list.append("🟢 ربح عائم")
                                            else: status_list.append("🔴 خسارة عائمة")
                                        else:
                                            current_prices.append(None); pnl_list.append(None); status_list.append("غير متاح")
                                    except:
                                        current_prices.append(None); pnl_list.append(None); status_list.append("خطأ")
                                        
                                df_track['السعر الحالي'] = current_prices
                                df_track['الربح/الخسارة %'] = pnl_list
                                df_track['الحالة'] = status_list
                                
                                df_disp = df_track.drop(columns=['Date_Only', 'الرمز'], errors='ignore').iloc[::-1]
                                
                                def style_pnl(val):
                                    if pd.isna(val): return ''
                                    if val > 0: return 'color: #00E676; font-weight: bold;'
                                    elif val < 0: return 'color: #FF5252; font-weight: bold;'
                                    return ''
                                
                                def format_pct(x):
                                    if pd.isna(x): return ""
                                    return f"+{x:.2f}%" if x > 0 else f"{x:.2f}%"
                                    
                                df_disp['الربح/الخسارة %'] = df_disp['الربح/الخسارة %'].apply(format_pct)
                                st.dataframe(df_disp.style.applymap(style_pnl, subset=['الربح/الخسارة %']), use_container_width=True, hide_index=True)
                        else:
                            df_disp = df_track.drop(columns=['Date_Only', 'الرمز'], errors='ignore').iloc[::-1]
                            st.dataframe(df_disp, use_container_width=True, hide_index=True)
                            
                        col_down, col_del = st.columns(2)
                        with col_down:
                            csv_data = df_track.to_csv(index=False).encode('utf-8-sig')
                            st.download_button("📥 تصدير السجل (Excel)", data=csv_data, file_name='Masa_PaperTrading.csv', mime='text/csv', use_container_width=True)
                        with col_del:
                            if st.button("🗑️ مسح السجل بالكامل", use_container_width=True):
                                os.remove(TRACKER_FILE)
                                st.rerun()
                    else:
                        st.info("السجل فارغ. قم بحفظ التوصيات من قسم VIP أولاً.")
                else:
                    st.info("لم تقم بحفظ أي صفقات للمراقبة حتى الآن. اذهب لقسم VIP واضغط زر الحفظ عندما تظهر الفرص.")

            # ==========================================
            # 🧠 3. لوحة التوصيات الشاملة
            # ==========================================
            with tab_ai:
                col_ai_main, col_ai_reports = st.columns([2.5, 1.2])
                
                with col_ai_main:
                    main_mom_score = calc_momentum_score(pct_1d_main, pct_5d_main, pct_10d_main, main_vol_ratio)
                    ai_score, ai_decision, ai_color, ai_reasons = get_ai_analysis(last_close, last_sma50, last_sma200, last_rsi, last_counter, last_zr_low, last_zr_high, main_event_text, main_bo_score_add, main_mom_score, main_vol_accel_ratio, pct_1d_main)
                    
                    st.markdown(f"""
                    <div class="ai-box" style="border-top-color: {ai_color};">
                        <div class="ai-header-flex">
                            <div class="ai-title" style="color: {ai_color};">🎯 خطة التداول المُباشرة: ({display_name})</div>
                            <div class="ai-score-circle" style="border-color: {ai_color}; color: {ai_color};">
                                <span class="ai-score-num">{ai_score}</span>
                                <span class="ai-score-max">/ 100</span>
                            </div>
                        </div>
                        <div class="ai-decision-text" style="color: {ai_color}; border-color: {ai_color};">
                            {ai_decision}
                        </div>
                        <div style="margin-top: 15px;">
                            {''.join([f'<div class="ai-reason-item" dir="rtl">{r}</div>' for r in ai_reasons])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("#### 🎯 التوصيات المباشرة لأسهم القائمة:")
                    if not df_ai_picks.empty:
                        df_ai_disp = pd.DataFrame(df_ai_picks).drop(columns=['الرمز', 'raw_score', 'raw_mom', 'raw_events', 'raw_time', 'raw_target', 'raw_sl']).sort_values(by="Score 💯", ascending=False)
                        html_ai = "<table class='ai-table' dir='rtl'><tr><th>الشركة</th><th>السعر</th><th>Score 💯</th><th>الزخم 🌊</th><th>الحالة اللحظية ⚡</th><th>وقت الدخول 🕒</th><th>الهدف 🎯</th><th>الوقف 🛡️</th><th>التوصية 🚦</th></tr>"
                        for _, row in df_ai_disp.iterrows():
                            html_ai += f"<tr><td style='color:#00d2ff; font-weight:bold; font-size:15px;'>{row['الشركة']}</td><td>{row['السعر']:.2f}</td><td style='color:{row['اللون']}; font-size:18px; font-weight:bold;'>{row['Score 💯']}/100</td><td>{row['الزخم 🌊']}</td><td>{row['الحالة اللحظية ⚡']}</td><td>{row['وقت الدخول 🕒']}</td><td><span class='target-text'>{row['الهدف 🎯']}</span></td><td><span class='sl-text'>{row['الوقف 🛡️']}</span></td><td style='color:{row['اللون']};'><span class='rec-badge' style='background-color:{row['اللون']}20; border:1px solid {row['اللون']}50;'>{row['التوصية 🚦']}</span></td></tr>"
                        html_ai += "</table>"
                        st.markdown(html_ai, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='empty-box'>السوق هادئ جداً. لا توجد أسهم تم التقاطها حالياً.</div>", unsafe_allow_html=True)

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
                        for _, row in df_up_recent.iterrows(): html_up += f"<tr><td>{row['منذ كم صف']}</td><td>{row['تاريخ']}</td><td><span style='background-color: #1565c0; color: white; padding: 2px 8px; border-radius: 4px; font-weight:bold;'>{row['السهم']}</span></td></tr>"
                        html_up += "</table>"
                        st.markdown(html_up, unsafe_allow_html=True)
                    else: st.markdown(f"<table class='qafah-table' dir='rtl'><tr><th style='background-color:#4CAF50; color:white;'>تغير إلى صاعد</th></tr><tr><td class='empty-box'>لا توجد تغيرات صاعدة آخر {n_days} صفوف</td></tr></table>", unsafe_allow_html=True)
                    
                    if not df_dn_recent.empty:
                        html_dn = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#e53935; color:white;'>منذ كم صف</th><th style='background-color:#e53935; color:white;'>تغير إلى هابط</th><th style='background-color:#e53935; color:white;'>السهم</th></tr>"
                        for _, row in df_dn_recent.iterrows(): html_dn += f"<tr><td style='background-color:rgba(229, 57, 53, 0.1);'>{row['منذ كم صف']}</td><td style='background-color:rgba(229, 57, 53, 0.1);'>{row['تاريخ']}</td><td style='color:#ef9a9a; font-weight:bold; background-color:rgba(229, 57, 53, 0.1);'>{row['السهم']}</td></tr>"
                        html_dn += "</table>"
                        st.markdown(html_dn, unsafe_allow_html=True)
                    else: st.markdown(f"<table class='qafah-table' dir='rtl'><tr><th style='background-color:#e53935; color:white;'>تغير إلى هابط</th></tr><tr><td class='empty-box'>لا توجد تغيرات هابطة آخر {n_days} صفوف</td></tr></table>", unsafe_allow_html=True)

                    st.markdown("<hr style='border-color: #2d303e;'>", unsafe_allow_html=True)
                    st.markdown("<div class='scanner-header'>اختراق المقاومة (اليوم) 🚀</div>", unsafe_allow_html=True)
                    if not df_bup.empty:
                        html_bup = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#2e7d32; color:white;'>النوع</th><th style='background-color:#2e7d32; color:white;'>السهم</th></tr>"
                        for _, row in df_bup.iterrows(): html_bup += f"<tr><td style='font-size:11px;'>{row['النوع']}</td><td style='color:#00d2ff; font-weight:bold;'>{row['السهم']}</td></tr>"
                        html_bup += "</table>"
                        st.markdown(html_bup, unsafe_allow_html=True)
                    else: st.markdown("<div class='empty-box'>لا توجد اختراقات اليوم</div>", unsafe_allow_html=True)
                        
                    st.markdown("<div class='scanner-header-red'>كسر الدعم (اليوم) 🩸</div>", unsafe_allow_html=True)
                    if not df_bdn.empty:
                        html_bdn = "<table class='qafah-table' dir='rtl'><tr><th style='background-color:#c62828; color:white;'>النوع</th><th style='background-color:#c62828; color:white;'>السهم</th></tr>"
                        for _, row in df_bdn.iterrows(): html_bdn += f"<tr><td style='font-size:11px;'>{row['النوع']}</td><td style='color:#ef9a9a; font-weight:bold;'>{row['السهم']}</td></tr>"
                        html_bdn += "</table>"
                        st.markdown(html_bdn, unsafe_allow_html=True)
                    else: st.markdown("<div class='empty-box'>لا توجد كسور اليوم</div>", unsafe_allow_html=True)

            # (باقي التبويبات بدون أي تغيير)
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
                    st.markdown(f"""<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:8px; margin-bottom: 20px;"><span class="filter-btn-active">All ({len(df_loads)})</span></div>""", unsafe_allow_html=True)
                    df_loads_styled = df_loads.copy()
                    def color_loads_values(val):
                        if isinstance(val, str) and "%" in val:
                            if "-" in val: return 'color: #f44336; font-weight: bold;'
                            elif val.startswith("0.0000"): return 'color: gray;'
                            else: return 'color: #4caf50; font-weight: bold;'
                        elif isinstance(val, int) and (val > 0): return 'color: #4caf50; font-weight: bold;'
                        elif isinstance(val, int) and (val < 0): return 'color: #f44336; font-weight: bold;'
                        return ''
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
                tv_ticker = ticker.replace('.SR', '') if ticker.endswith('.SR') else ticker
                tv_symbol = f"TADAWUL:{tv_ticker}" if ticker.endswith('.SR') else tv_ticker
                tz = "Asia/Riyadh" if ticker.endswith('.SR') else "America/New_York"
                tradingview_html = f"""<div class="tradingview-widget-container" style="height:700px;width:100%"><div id="tradingview_masa" style="height:100%;width:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true,"symbol": "{tv_symbol}","interval": "D","timezone": "{tz}","theme": "dark","style": "1","locale": "ar_AE","enable_publishing": false,"backgroundColor": "#1a1c24","gridColor": "#2d303e","hide_top_toolbar": false,"hide_legend": false,"save_image": false,"container_id": "tradingview_masa","toolbar_bg": "#1e2129","studies": ["Volume@tv-basicstudies","RSI@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"]}});</script></div>"""
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
                st.download_button(label="📥 تصدير البيانات للإكسل", data=csv, file_name=f'Masa_{display_name}.csv', mime='text/csv', use_container_width=True)
