import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
import pandas as pd
from datetime import date, timedelta

# ?? ?좏뒠釉??곸긽 留ㅽ븨 (湲곕낯媛?- ?ㅼ썙???곸긽ID) ????????????????
YOUTUBE_MAP = {
    "tegi":       "A6yhM5cof-A",
    "treeh0me":   "4ezU_-2qUqI",
    "annaro":     "lc5mJXUNcwY",
    "darlene":    "kScggDky4To",
    "greentica":  "K9ySFTLm_oE",
    "hyejeong":   "AEBPuroGCFg",
    "milkwood":   "t0ApHhQw_58",
    "skyhome":    "LNdsbtmcseI",
    "yodanara":   "zu0j2ZFWfwY",
    "yongyoung":  "odUv2ZC06NQ",
    "ysh":        "7slrfAou8KE",
    "solseom":    "6KGIQBNj_1s",
    "fav.things":  "eS6YCQQPSpA",
    "@fav.things": "eS6YCQQPSpA",
    "casa_de_oze": "CuURqAdbDJI",
    "硫?고꺆_a":    "Memt7hADi8U",
    "硫?고꺆_b":    "UyoT0y9NdHU",
    "硫?고꺆_c":    "x8PYIpQYzA0",
    "dahyunjae":   "Zh6qo1DdFew",
    "@dahyunjae":  "Zh6qo1DdFew",
    "援ъ씪??:      "Nn84wnsQssQ",
}

def get_youtube_id(ad_name):
    name_lower = ad_name.lower()
    for keyword, vid_id in YOUTUBE_MAP.items():
        if keyword in name_lower:
            return vid_id
    return None

# ?? ?섏씠吏 ?ㅼ젙 ???????????????????????????????????????????????
st.set_page_config(page_title="LLS AD Dashboard", page_icon="?뙼", layout="wide")

# ?? 濡쒓렇??????????????????????????????????????????????????????
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;
                    height:70vh;flex-direction:column;gap:0.4rem;'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>?뙼</div>
            <h1 style='color:#18181b;font-size:1.8rem;font-weight:700;margin:0;'>LLS AD Dashboard</h1>
            <p style='color:#a1a1aa;font-size:0.9rem;margin:0 0 1.5rem 0;'>愿묎퀬 ?뚯옱 ?⑥쑉 遺꾩꽍 ??쒕낫??/p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.2, 1, 1.2])
        with col2:
            pw = st.text_input("", type="password", placeholder="鍮꾨?踰덊샇 ?낅젰")
            if st.button("濡쒓렇??, use_container_width=True):
                if pw == st.secrets.get("DASHBOARD_PASSWORD", "lls2024"):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("鍮꾨?踰덊샇媛 ??몄뒿?덈떎.")
        st.stop()

# check_login()  # TEST ?섏씠吏 ??鍮꾨?踰덊샇 ?놁쓬

ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
AD_ACCOUNT_ID = st.secrets["AD_ACCOUNT_ID"]
APP_ID = st.secrets["APP_ID"]
APP_SECRET = st.secrets["APP_SECRET"]

# ?? CSS ???????????????????????????????????????????????????????
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 諛곌꼍 */
.stApp, .stAppViewContainer,
section[data-testid="stMain"] > div,
.block-container {
    background: #f7f6f3 !important;
}

/* ?곷떒 ?ㅻ뜑 諛??④? */
header[data-testid="stHeader"] { background: transparent !important; }

/* ?? ??쒕낫???ㅻ뜑 ?? */
.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #e4e4e7;
    margin-bottom: 1.5rem;
}
.dash-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #18181b;
    margin: 0;
}
.dash-sub {
    font-size: 0.8rem;
    color: #a1a1aa;
    margin: 0.1rem 0 0 0;
}

/* ?? ?붿빟 硫뷀듃由?諛??? */
.metrics-bar {
    display: flex;
    background: #ffffff;
    border-radius: 16px;
    padding: 1.4rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 1.8rem;
}
.metric-item {
    flex: 1;
    text-align: center;
    padding: 0 1rem;
}
.metric-item + .metric-item {
    border-left: 1px solid #f0f0f0;
}
.mi-label {
    font-size: 0.72rem;
    color: #a1a1aa;
    font-weight: 500;
    margin-bottom: 0.3rem;
    letter-spacing: 0.02em;
}
.mi-value {
    font-size: 1.45rem;
    font-weight: 700;
    color: #18181b;
    line-height: 1.2;
}
.mi-roas { color: #16a34a !important; }

/* ?? ?뱀뀡 ??댄? ?? */
.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #18181b;
    margin: 0.2rem 0 0.8rem 0;
}
.section-sub {
    font-size: 0.78rem;
    color: #a1a1aa;
    margin: -0.4rem 0 0.8rem 0;
}

/* ?? ?뺣젹 踰꾪듉 ?? */
.stButton > button {
    background: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    color: #52525b !important;
    border-radius: 100px !important;
    padding: 0.28rem 1rem !important;
    font-size: 0.77rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
.stButton > button:hover {
    background: #18181b !important;
    color: #ffffff !important;
    border-color: #18181b !important;
}
.stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ?? 愿묎퀬 洹몃━???? */
.ad-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
}

/* ?? 愿묎퀬 移대뱶 ?? */
.ad-card-g {
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    border: 1px solid #f0f0f0;
}
.ad-card-g:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

/* ?? ?몃꽕???곸뿭 ?? */
.thumb-area {
    position: relative;
    width: 100%;
    height: 190px;
    overflow: hidden;
    background: #f4f4f5;
}
.thumb-area img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.thumb-no-img {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #a1a1aa;
    font-size: 0.82rem;
}

/* ?곹깭 諭껋? */
.status-pill {
    position: absolute;
    top: 9px;
    left: 9px;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 100px;
    backdrop-filter: blur(4px);
    z-index: 10;
}
.sp-active {
    background: rgba(220,252,231,0.92);
    color: #15803d;
}
.sp-paused {
    background: rgba(244,244,245,0.92);
    color: #71717a;
}

/* YouTube 諭껋? */
.yt-badge {
    position: absolute;
    bottom: 9px;
    right: 9px;
    background: rgba(185,0,0,0.88);
    color: white;
    font-size: 0.62rem;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
}

/* ?? 移대뱶 蹂몃Ц ?? */
.card-body {
    padding: 0.85rem 0.95rem 0.95rem;
}
.card-ad-name {
    font-size: 0.82rem;
    font-weight: 700;
    color: #18181b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.1rem;
}
.card-adset {
    font-size: 0.68rem;
    color: #a1a1aa;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.7rem;
}
.card-date {
    font-size: 0.65rem;
    color: #c4c4c4;
    margin-bottom: 0.65rem;
}

/* KPI 諛뺤뒪 3媛?*/
.kpi-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    margin-bottom: 0.65rem;
}
.kpi-box {
    background: #fafaf9;
    border-radius: 9px;
    padding: 0.45rem 0.3rem;
    text-align: center;
    border: 1px solid #f0f0f0;
}
.kpi-box-active {
    background: #f0f9ff;
    border: 1.5px solid #bae6fd;
}
.kpi-lbl {
    font-size: 0.6rem;
    color: #a1a1aa;
    margin-bottom: 0.15rem;
    font-weight: 500;
}
.kpi-lbl-active {
    font-size: 0.6rem;
    color: #0284c7;
    margin-bottom: 0.15rem;
    font-weight: 700;
}
.kpi-val {
    font-size: 0.82rem;
    font-weight: 700;
    color: #18181b;
}
.kv-green { color: #16a34a !important; }
.kv-amber { color: #d97706 !important; }
.kv-red   { color: #dc2626 !important; }

/* ?섎떒 ?쒓렇??*/
.card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}
.tag {
    font-size: 0.65rem;
    color: #71717a;
    background: #f4f4f5;
    border-radius: 5px;
    padding: 2px 7px;
    font-weight: 500;
}

/* ?? 濡쒓렇?꾩썐 踰꾪듉 ?ш린 ?? */
div[data-testid="column"]:last-child .stButton > button {
    font-size: 0.72rem !important;
    padding: 0.2rem 0.7rem !important;
    color: #a1a1aa !important;
    border-color: #e4e4e7 !important;
}

/* date_input, caption ??*/
.stDateInput label { font-size: 0.78rem !important; color: #71717a !important; }
.stCaption { color: #a1a1aa !important; font-size: 0.75rem !important; }

/* expander */
.streamlit-expanderHeader { font-size: 0.8rem !important; }

/* ?? 由ъ뒪??酉??? */
.ad-list { display: flex; flex-direction: column; gap: 10px; }

.list-row {
    background: #fff;
    border-radius: 14px;
    display: flex;
    align-items: stretch;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0;
    overflow: hidden;
    transition: box-shadow 0.2s ease;
}
.list-row:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.list-thumb {
    position: relative;
    width: 140px;
    flex-shrink: 0;
    background: #f4f4f5;
    overflow: hidden;
}
.list-thumb img {
    width: 100%; height: 100%;
    object-fit: cover; display: block;
}

.list-body {
    flex: 1;
    padding: 0.85rem 1.1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-width: 0;
    gap: 0.6rem;
}
.list-name {
    font-size: 0.9rem; font-weight: 700; color: #18181b;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    margin-bottom: 0.1rem;
}
.list-meta {
    font-size: 0.7rem; color: #a1a1aa;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.list-metrics {
    display: flex; flex-wrap: wrap; gap: 6px;
}
.lm-item {
    background: #fafaf9; border-radius: 8px;
    padding: 0.35rem 0.65rem; text-align: center;
    border: 1px solid #f0f0f0; min-width: 72px;
}
.lm-primary {
    background: #f0f9ff; border-color: #bae6fd;
}
.lm-lbl {
    font-size: 0.58rem; color: #a1a1aa;
    font-weight: 500; margin-bottom: 0.1rem;
}
.lm-lbl-primary {
    font-size: 0.58rem; color: #0284c7;
    font-weight: 700; margin-bottom: 0.1rem;
}
.lm-val {
    font-size: 0.82rem; font-weight: 700; color: #18181b;
}

/* ?? Summary 酉??? */
.sum-stat {
    flex: 1; background: white; border-radius: 12px;
    padding: 1rem 1.2rem; text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0;
}
.sum-stat-val { font-size: 1.8rem; font-weight: 700; color: #18181b; }
.sum-stat-lbl { font-size: 0.72rem; color: #a1a1aa; margin-top: 0.2rem; }

.sum-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 0.8rem; border-radius: 10px;
    margin-bottom: 6px; background: white;
    border: 1px solid #f0f0f0;
}
.sum-rank { font-size: 0.7rem; font-weight: 700; color: #a1a1aa; min-width: 22px; }
.sum-thumb {
    position: relative; width: 56px; height: 56px;
    border-radius: 8px; overflow: hidden; flex-shrink: 0;
    background: #f4f4f5;
}
.sum-thumb img { width:100%; height:100%; object-fit:cover; display:block; }
.sum-name {
    font-size: 0.8rem; font-weight: 600; color: #18181b;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    margin-bottom: 0.1rem;
}
.sum-roas { font-size: 0.9rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ?? 愿묎퀬 ON/OFF API ???????????????????????????????????????????
def toggle_ad_status(ad_id, new_status):
    try:
        import requests
        url = f"https://graph.facebook.com/v19.0/{ad_id}"
        resp = requests.post(url, data={"status": new_status, "access_token": ACCESS_TOKEN})
        result = resp.json()
        if "error" in result:
            return result["error"].get("message", str(result["error"]))
        return True
    except Exception as e:
        return str(e)


# ?? ?ㅻ뜑 ?????????????????????????????????????????????????????
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem 0; border-bottom:1px solid #e4e4e7; margin-bottom:1.5rem;">
        <p style="font-size:1.3rem;font-weight:700;color:#18181b;margin:0;">?뙼 LLS AD Dashboard</p>
        <p style="font-size:0.78rem;color:#a1a1aa;margin:0.1rem 0 0 0;">Meta 愿묎퀬 ?뚯옱 ?⑥쑉 遺꾩꽍</p>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.markdown("<div style='padding-top:0.6rem;'>", unsafe_allow_html=True)
    if st.button("濡쒓렇?꾩썐"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ?? ?좎쭨 & 議고쉶 ??????????????????????????????????????????????
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
with col1:
    start_date = st.date_input("?쒖옉??, date.today().replace(day=1))
with col2:
    end_date = st.date_input("醫낅즺??, date.today())
with col3:
    st.markdown("<div style='padding-top:1.6rem;'>", unsafe_allow_html=True)
    fetch_btn = st.button("?뱤  ?곗씠??遺덈윭?ㅺ린", use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div style='padding-top:1.8rem;'>", unsafe_allow_html=True)
    force_refresh = st.checkbox("?봽 理쒖떊 ?곗씠?곕줈 ?덈줈怨좎묠", value=False)
    st.markdown("""
    <p style="font-size:0.7rem;color:#a1a1aa;margin:0.2rem 0 0 1.6rem;line-height:1.5;">
        愿묎퀬瑜??덈줈 異붽??덇굅???곗씠?곌? 諛붾?寃쎌슦 泥댄겕?섏꽭??br>
        ?됱냼??泥댄겕 ?놁씠 遺덈윭?ㅻ㈃ ??鍮좊Ⅴ寃?議고쉶?⑸땲??    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if "df" not in st.session_state:
    st.session_state.df = None
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "援щℓ?꾪솚湲덉븸"

# ?? 罹먯떛 ?⑥닔 (?좎쭨媛 媛숈쑝硫?API ?ы샇異??놁쓬) ?????????????????
@st.cache_data(show_spinner=False)
def fetch_ad_data(start_date_str, end_date_str, access_token, ad_account_id, app_id, app_secret):
    """?좎쭨 踰붿쐞媛 媛숈쑝硫?罹먯떆???곗씠??諛섑솚, ?ㅻⅤ硫?API ?덈줈 ?몄텧.
    諛섑솚媛믪? ?쒖닔 Python 湲곕낯 ???list of dict)留??ъ슜."""
    import requests as _req
    import json as _json

    BASE = "https://graph.facebook.com/v19.0"

    def _paginate(url, params):
        results = []
        while url:
            r = _req.get(url, params=params, timeout=30)
            d = r.json()
            if "error" in d:
                raise Exception(d["error"].get("message", str(d["error"])))
            results.extend(d.get("data", []))
            url = d.get("paging", {}).get("next")
            params = {}
        return results

    # ?몄궗?댄듃 議고쉶
    all_insights = _paginate(
        f"{BASE}/{ad_account_id}/insights",
        {
            "fields": "ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,spend,impressions,clicks,ctr,cpc,actions,action_values",
            "time_range": _json.dumps({"since": start_date_str, "until": end_date_str}),
            "level": "ad",
            "limit": 500,
            "access_token": access_token,
        },
    )

    # 愿묎퀬 ?щ━?먯씠?곕툕 議고쉶
    ad_cache = {}
    try:
        ads = _paginate(
            f"{BASE}/{ad_account_id}/ads",
            {
                "fields": "id,status,effective_status,created_time,creative{thumbnail_url,image_url,video_id,instagram_permalink_url}",
                "limit": 200,
                "access_token": access_token,
            },
        )
        for ad in ads:
            creative = ad.get("creative", {})
            ad_cache[str(ad["id"])] = {
                "status":                  str(ad.get("status", "")),
                "effective_status":        str(ad.get("effective_status", "")),
                "created_time":            str(ad.get("created_time", "")),
                "thumbnail_url":           str(creative.get("thumbnail_url", "")),
                "image_url":               str(creative.get("image_url", "")),
                "video_id":                str(creative.get("video_id", "")),
                "instagram_permalink_url": str(creative.get("instagram_permalink_url", "")),
            }
    except Exception:
        pass

    rows = []
    for data in all_insights:
        spend       = float(data.get("spend", 0))
        ctr         = float(data.get("ctr", 0))
        cpc         = float(data.get("cpc", 0))
        impressions = int(data.get("impressions", 0))
        clicks      = int(data.get("clicks", 0))
        ad_id       = str(data.get("ad_id", ""))
        purchases = 0
        purchase_value = 0.0
        for action in data.get("actions", []):
            if action["action_type"] == "offsite_conversion.fb_pixel_purchase":
                purchases += int(float(action["value"]))
        for action in data.get("action_values", []):
            if action["action_type"] == "offsite_conversion.fb_pixel_purchase":
                purchase_value += float(action["value"])
        roas = round(purchase_value / spend, 2) if spend > 0 else 0.0

        thumbnail_url = ""
        is_video      = False
        status        = "?????놁쓬"
        start_time    = ""

        ad_info = ad_cache.get(ad_id, {})
        if ad_info:
            status     = ad_info["effective_status"]
            start_time = ad_info["created_time"][:10] if ad_info["created_time"] else ""
            video_id   = ad_info["video_id"]
            if video_id and video_id != "None":
                is_video      = True
                thumbnail_url = ad_info["thumbnail_url"]
            else:
                thumbnail_url = ad_info["image_url"] or ad_info["thumbnail_url"]

        rows.append({
            "ad_id":          ad_id,
            "ad_status":      ad_info.get("status", ""),
            "?몃꽕??:         thumbnail_url,
            "instagram_url":  ad_info.get("instagram_permalink_url", ""),
            "?곸긽?щ?":        is_video,
            "罹좏럹??:         str(data.get("campaign_name", "")),
            "愿묎퀬紐?:         str(data.get("ad_name", "")),
            "愿묎퀬?명듃":       str(data.get("adset_name", "")),
            "?곹깭":           status,
            "?쒖옉??:         start_time,
            "鍮꾩슜":           spend,
            "援щℓ?꾪솚":       purchases,
            "援щℓ?꾪솚湲덉븸":   purchase_value,
            "ROAS":           roas,
            "CTR(%)":         round(ctr, 2),
            "CPC":            round(cpc, 2),
            "?몄텧??:         impressions,
            "?대┃??:         clicks,
            "CVR(%)":         round(purchases / clicks * 100, 2) if clicks > 0 else 0.0,
            "援щℓ?밸퉬??:     round(spend / purchases, 0) if purchases > 0 else 999999999,
        })

    return rows  # ?쒖닔 list[dict] ??pickle 吏곷젹??媛??
# ?? ?곗씠??fetch ??????????????????????????????????????????????
if fetch_btn:
    if force_refresh:
        fetch_ad_data.clear()  # 罹먯떆 珥덇린????API 媛뺤젣 ?ы샇異?    with st.spinner("Meta API?먯꽌 ?곗씠??媛?몄삤??以?.."):
        try:
            rows = fetch_ad_data(
                str(start_date), str(end_date),
                ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET
            )
            st.session_state.df = pd.DataFrame(rows)
            cache_msg = " (?덈줈怨좎묠)" if force_refresh else ""
            st.success(f"?? 珥?{len(rows)}媛??뚯옱 濡쒕뱶 ?꾨즺{cache_msg}")
        except Exception as e:
            st.error(f"?ㅻ쪟 諛쒖깮: {e}")


# ?? ?뚮뜑留?????????????????????????????????????????????????????
if st.session_state.df is not None:
    df = st.session_state.df

    if df.empty or "鍮꾩슜" not in df.columns:
        st.info("?뱤 議고쉶 踰꾪듉???뚮윭 愿묎퀬 ?곗씠?곕? 遺덈윭?ㅼ꽭??")
        st.stop()

    # ?붿빟 硫뷀듃由?    total_spend      = df["鍮꾩슜"].sum()
    total_purchases  = df["援щℓ?꾪솚"].sum()
    total_conv_value = df["援щℓ?꾪솚湲덉븸"].sum()
    overall_roas     = round(total_conv_value / total_spend, 2) if total_spend > 0 else 0
    overall_roas_pct = f"{overall_roas * 100:.0f}%"
    cost_per_purchase = round(total_spend / total_purchases, 0) if total_purchases > 0 else 0

    st.markdown(f"""
    <div class="metrics-bar">
        <div class="metric-item">
            <div class="mi-label">珥?愿묎퀬鍮꾩슜</div>
            <div class="mi-value">{total_spend:,.0f}??/div>
        </div>
        <div class="metric-item">
            <div class="mi-label">珥?援щℓ?꾪솚</div>
            <div class="mi-value">{total_purchases:,}嫄?/div>
        </div>
        <div class="metric-item">
            <div class="mi-label">?꾩껜 ROAS</div>
            <div class="mi-value mi-roas">{overall_roas_pct}</div>
        </div>
        <div class="metric-item">
            <div class="mi-label">珥??꾪솚湲덉븸</div>
            <div class="mi-value">{total_conv_value:,.0f}??/div>
        </div>
        <div class="metric-item">
            <div class="mi-label">?됯퇏 援щℓ?밸퉬??/div>
            <div class="mi-value">{cost_per_purchase:,.0f}??/div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ?? ?ы띁 ?⑥닔 ??????????????????????????????????????????????
    def roas_color_class(r):
        if r >= 3:   return "kv-green"
        elif r >= 1: return "kv-amber"
        return "kv-red"

    def thumb_inner_html(row, height=160):
        """?몃꽕??inner HTML 諛섑솚 (list/summary 怨듭슜)"""
        yt_id = get_youtube_id(row["愿묎퀬紐?])
        if yt_id:
            thumb    = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            fallback = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
            yt_url   = f"https://youtube.com/shorts/{yt_id}"
            return f'''<a href="{yt_url}" target="_blank" style="display:block;height:100%;">
  <img src="{thumb}" onerror="this.src='{fallback}'"
       style="width:100%;height:100%;object-fit:cover;display:block;" />
  <span class="yt-badge">??YouTube</span>
</a>'''
        url = row["?몃꽕??]
        if url:
            return f'''
<div style="position:absolute;inset:-20px;background-image:url('{url}');
            background-size:cover;background-position:center;
            filter:blur(20px);opacity:0.5;transform:scale(1.1);"></div>
<img src="{url}" style="position:relative;z-index:1;
     width:100%;height:100%;object-fit:contain;display:block;" />'''
        label = "?렗 ?곸긽" if row["?곸긽?щ?"] else "?대?吏 ?놁쓬"
        return f'<div class="thumb-no-img">{label}</div>'

    def render_list(df_render, sort_key="ROAS"):
        """由ъ뒪?명삎 ?뚮뜑留????몃꽕???ш쾶 ?쇱そ, 吏???ㅻⅨ履?""
        # ?뺣젹 湲곗?蹂?吏???쒖꽌 (泥?踰덉㎏媛 媛뺤“)
        metric_order = {
            "ROAS":     ["ROAS", "?꾪솚湲덉븸", "愿묎퀬鍮?, "援щℓ?밸퉬??, "CVR", "援щℓ??, "CTR", "?몄텧"],
            "援щℓ?밸퉬??: ["援щℓ?밸퉬??, "愿묎퀬鍮?, "ROAS", "?꾪솚湲덉븸", "CVR", "援щℓ??, "CTR", "?몄텧"],
            "CVR":      ["CVR", "ROAS", "愿묎퀬鍮?, "?꾪솚湲덉븸", "援щℓ?밸퉬??, "援щℓ??, "CTR", "?몄텧"],
            "?꾪솚湲덉븸":  ["?꾪솚湲덉븸", "ROAS", "愿묎퀬鍮?, "援щℓ?밸퉬??, "CVR", "援щℓ??, "CTR", "?몄텧"],
        }
        order = metric_order.get(sort_key, metric_order["ROAS"])

        rows_html = ""
        for i, (_, row) in enumerate(df_render.iterrows()):
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            rc        = roas_color_class(row["ROAS"])
            spend_per = "?? if row["援щℓ?밸퉬??] == 999999999 else f"{row['援щℓ?밸퉬??]:,.0f}??
            sp_cls    = "sp-active" if row["?곹깭"] == "ACTIVE" else "sp-paused"
            sp_text   = "?댁쁺以? if row["?곹깭"] == "ACTIVE" else ("?뺤?" if row["?곹깭"] == "PAUSED" else row["?곹깭"])
            date_txt  = row["?쒖옉??] if row["?쒖옉??] else "-"

            all_metrics = {
                "ROAS":     (roas_pct, rc),
                "?꾪솚湲덉븸":  (f"{row['援щℓ?꾪솚湲덉븸']:,.0f}??, ""),
                "愿묎퀬鍮?:    (f"{row['鍮꾩슜']:,.0f}??, ""),
                "CVR":      (f"{row['CVR(%)']}%", ""),
                "援щℓ?밸퉬??: (spend_per, ""),
                "援щℓ??:    (f"{row['援щℓ?꾪솚']}嫄?, ""),
                "CTR":      (f"{row['CTR(%)']}%", ""),
                "?몄텧":      (f"{row['?몄텧??]:,}", ""),
            }

            metrics_html = ""
            for idx, key in enumerate(order):
                val, cls = all_metrics[key]
                if idx == 0:
                    metrics_html += f'''<div class="lm-item lm-primary">
  <div class="lm-lbl lm-lbl-primary">{key}</div>
  <div class="lm-val {cls}">{val}</div>
</div>'''
                else:
                    metrics_html += f'''<div class="lm-item">
  <div class="lm-lbl">{key}</div>
  <div class="lm-val {cls}">{val}</div>
</div>'''

            inner = thumb_inner_html(row)
            rows_html += f"""
<div class="list-row">
  <div class="list-thumb">
    {inner}
    <span class="status-pill {sp_cls}">{sp_text}</span>
  </div>
  <div class="list-body">
    <div>
      <div class="list-name">{row['愿묎퀬紐?]}</div>
      <div class="list-meta">{row['愿묎퀬?명듃']} 쨌 {date_txt}</div>
    </div>
    <div class="list-metrics">{metrics_html}</div>
  </div>
</div>"""

        st.markdown(f'<div class="ad-list">{rows_html}</div>', unsafe_allow_html=True)

    def render_summary(df):
        """Summary ?????꾩껜 ?꾪솴 + TOP 5 ??궧"""
        active_cnt    = len(df[df["?곹깭"] == "ACTIVE"])
        paused_cnt    = len(df[df["?곹깭"] == "PAUSED"])
        profitable    = len(df[df["ROAS"] >= 1])
        total_cnt     = len(df)

        st.markdown(f"""
<div style="display:flex;gap:12px;margin-bottom:1.8rem;">
  <div class="sum-stat"><div class="sum-stat-val">{total_cnt}</div><div class="sum-stat-lbl">?꾩껜 ?뚯옱</div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#15803d;">{active_cnt}</div><div class="sum-stat-lbl">?댁쁺以?/div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#71717a;">{paused_cnt}</div><div class="sum-stat-lbl">?뺤?</div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#0284c7;">{profitable}</div><div class="sum-stat-lbl">ROAS 100% ?댁긽</div></div>
</div>
""", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<p class="section-title">?룇 ROAS TOP 5</p>', unsafe_allow_html=True)
            top5 = df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True)
            rows = ""
            for i, (_, r) in enumerate(top5.iterrows()):
                roas_pct = f"{r['ROAS']*100:.0f}%"
                rc = roas_color_class(r["ROAS"])
                inner = thumb_inner_html(r, height=56)
                sp_cls = "sp-active" if r["?곹깭"] == "ACTIVE" else "sp-paused"
                sp_text = "?댁쁺以? if r["?곹깭"] == "ACTIVE" else "?뺤?"
                rows += f"""
<div class="sum-row">
  <span class="sum-rank">#{i+1}</span>
  <div class="sum-thumb">
    {inner}
    <span class="status-pill {sp_cls}" style="font-size:0.55rem;padding:2px 5px;top:4px;left:4px;">{sp_text}</span>
  </div>
  <div style="flex:1;min-width:0;">
    <div class="sum-name">{r['愿묎퀬紐?]}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r['愿묎퀬?명듃']}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    <div class="sum-roas {rc}">{roas_pct}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">{r['援щℓ?꾪솚湲덉븸']:,.0f}??/div>
  </div>
</div>"""
            st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<p class="section-title">?뮯 援щℓ?밸퉬???????TOP 5</p>', unsafe_allow_html=True)
            # 援щℓ媛 ?덈뒗 ?뚯옱留?(999999999 ?쒖쇅)
            top5c = (df[df["援щℓ?밸퉬??] < 999999999]
                     .sort_values("援щℓ?밸퉬??, ascending=True)
                     .head(5).reset_index(drop=True))
            rows = ""
            for i, (_, r) in enumerate(top5c.iterrows()):
                roas_pct = f"{r['ROAS']*100:.0f}%"
                rc = roas_color_class(r["ROAS"])
                inner = thumb_inner_html(r, height=56)
                sp_cls = "sp-active" if r["?곹깭"] == "ACTIVE" else "sp-paused"
                sp_text = "?댁쁺以? if r["?곹깭"] == "ACTIVE" else "?뺤?"
                rows += f"""
<div class="sum-row">
  <span class="sum-rank">#{i+1}</span>
  <div class="sum-thumb">
    {inner}
    <span class="status-pill {sp_cls}" style="font-size:0.55rem;padding:2px 5px;top:4px;left:4px;">{sp_text}</span>
  </div>
  <div style="flex:1;min-width:0;">
    <div class="sum-name">{r['愿묎퀬紐?]}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r['愿묎퀬?명듃']}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    <div style="font-size:0.9rem;font-weight:700;color:#18181b;">{r['援щℓ?밸퉬??]:,.0f}??/div>
    <div style="font-size:0.65rem;color:#a1a1aa;">ROAS <span class="{rc}">{roas_pct}</span></div>
  </div>
</div>"""
            st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

    def sort_df(df, col, ascending):
        """?댁쁺以??뚯옱 癒쇱?, 洹??덉뿉??吏??湲곗? ?뺣젹"""
        tmp = df.copy()
        tmp["_s"] = (tmp["?곹깭"] != "ACTIVE").astype(int)  # 0=?댁쁺以? 1=?뺤?
        return (tmp.sort_values(["_s", col], ascending=[True, ascending])
                   .drop(columns=["_s"])
                   .reset_index(drop=True))

    # ?? 愿묎퀬?명듃蹂?蹂닿린 ????????????????????????????????????????
    def render_adset_view(df_all, col_key="ROAS", asc=False, sort_label="ROAS"):
        adset_groups = df_all.groupby("愿묎퀬?명듃")
        for adset_name, df_adset in adset_groups:
            adset_spend     = df_adset["鍮꾩슜"].sum()
            adset_cv        = df_adset["援щℓ?꾪솚湲덉븸"].sum()
            adset_roas      = round(adset_cv / adset_spend, 2) if adset_spend > 0 else 0
            adset_roas_pct  = f"{adset_roas * 100:.0f}%"
            adset_purchases = int(df_adset["援щℓ?꾪솚"].sum())
            active_cnt      = int((df_adset["?곹깭"] == "ACTIVE").sum())
            rc = "color:#16a34a;" if adset_roas >= 1 else "color:#dc2626;"

            st.markdown(f"""
<div style="background:#fff;border-radius:14px;padding:1rem 1.3rem;
            margin-bottom:0.7rem;border:1px solid #e4e4e7;
            box-shadow:0 1px 4px rgba(0,0,0,0.05);">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.7rem;">
    <span style="font-size:0.95rem;font-weight:700;color:#18181b;">?뱚 {adset_name}</span>
    <span style="font-size:0.72rem;color:#a1a1aa;">{len(df_adset)}媛??뚯옱 쨌 ?댁쁺以?{active_cnt}媛?/span>
  </div>
  <div style="display:flex;gap:2rem;">
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">愿묎퀬鍮?/div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_spend:,.0f}??/div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">ROAS</div>
         <div style="font-size:0.9rem;font-weight:700;{rc}">{adset_roas_pct}</div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">援щℓ??/div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_purchases}嫄?/div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">?꾪솚湲덉븸</div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_cv:,.0f}??/div></div>
  </div>
</div>
""", unsafe_allow_html=True)
            render_list(sort_df(df_adset, col_key, asc), sort_label)
            st.markdown("<div style='margin-bottom:1.8rem;'></div>", unsafe_allow_html=True)

    # ?? 愿묎퀬?명듃蹂?媛濡?蹂닿린 (移몃컲) ????????????????????????????
    MAX_COLS = 5  # ??以꾩뿉 理쒕? 愿묎퀬?명듃 ??    def render_adset_horizontal(df_all, col_key="ROAS", asc=False, sort_label="ROAS"):
        adset_groups = list(df_all.groupby("愿묎퀬?명듃"))
        # ?댁쁺以??뚯옱 留롮? ?명듃 ?쇱そ, OFF ?명듃 ?ㅻⅨ履?        adset_groups.sort(key=lambda x: (x[1]["?곹깭"] == "ACTIVE").sum(), reverse=True)
        n = len(adset_groups)
        if n == 0:
            return
        # MAX_COLS ?⑥쐞濡???遺꾪븷
        for row_start in range(0, n, MAX_COLS):
            row_groups = adset_groups[row_start:row_start + MAX_COLS]
            st_cols = st.columns(len(row_groups))
            for st_col, (adset_name, df_adset) in zip(st_cols, row_groups):
                with st_col:
                    adset_spend     = df_adset["鍮꾩슜"].sum()
                    adset_cv        = df_adset["援щℓ?꾪솚湲덉븸"].sum()
                    adset_roas      = round(adset_cv / adset_spend, 2) if adset_spend > 0 else 0
                    adset_roas_pct  = f"{adset_roas * 100:.0f}%"
                    adset_purchases = int(df_adset["援щℓ?꾪솚"].sum())
                    active_cnt      = int((df_adset["?곹깭"] == "ACTIVE").sum())
                    border_clr      = "#16a34a" if adset_roas >= 1 else "#dc2626"
                    roas_clr        = "#16a34a" if adset_roas >= 1 else "#dc2626"

                    # ?명듃 ?ㅻ뜑 移대뱶
                    bg_clr   = "rgba(220,252,231,0.6)" if adset_roas >= 1 else "rgba(254,226,226,0.6)"
                    st.markdown(f"""
<div style="background:{bg_clr};border-radius:14px;padding:1rem 1.1rem;
            margin-bottom:0.9rem;border:2px solid {border_clr};
            box-shadow:0 2px 8px rgba(0,0,0,0.08);">
  <div style="font-size:0.65rem;font-weight:600;color:{border_clr};
              letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.25rem;">
    ?뱚 愿묎퀬?명듃
  </div>
  <div style="font-size:0.88rem;font-weight:800;color:#18181b;
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
              margin-bottom:0.75rem;" title="{adset_name}">{adset_name}</div>
  <div style="display:flex;align-items:center;justify-content:space-between;
              background:rgba(255,255,255,0.7);border-radius:10px;
              padding:0.6rem 0.8rem;margin-bottom:0.5rem;">
    <div style="text-align:center;">
      <div style="font-size:0.58rem;color:#71717a;margin-bottom:0.1rem;">ROAS</div>
      <div style="font-size:1.3rem;font-weight:800;color:{roas_clr};line-height:1;">{adset_roas_pct}</div>
    </div>
    <div style="width:1px;height:30px;background:#e4e4e7;"></div>
    <div style="text-align:center;">
      <div style="font-size:0.58rem;color:#71717a;margin-bottom:0.1rem;">援щℓ??/div>
      <div style="font-size:1.1rem;font-weight:800;color:#18181b;line-height:1;">{adset_purchases}嫄?/div>
    </div>
    <div style="width:1px;height:30px;background:#e4e4e7;"></div>
    <div style="text-align:center;">
      <div style="font-size:0.58rem;color:#71717a;margin-bottom:0.1rem;">?댁쁺以?/div>
      <div style="font-size:1.1rem;font-weight:800;color:#15803d;line-height:1;">{active_cnt}媛?/div>
    </div>
  </div>
  <div style="font-size:0.72rem;color:#71717a;text-align:right;">
    愿묎퀬鍮?<strong style="color:#18181b;">{adset_spend:,.0f}??/strong>
    &nbsp;쨌&nbsp; ?뚯옱 <strong style="color:#18181b;">{len(df_adset)}媛?/strong>
  </div>
</div>
""", unsafe_allow_html=True)

                    # ?뚯옱 移대뱶 紐⑸줉
                    df_sorted  = sort_df(df_adset, col_key, asc)
                    cards_html = ""
                    for _, row in df_sorted.iterrows():
                        roas_pct  = f"{row['ROAS']*100:.0f}%"
                        rc        = "#16a34a" if row["ROAS"] >= 2 else ("#d97706" if row["ROAS"] >= 1 else "#dc2626")
                        sp_cls    = "sp-active" if row["?곹깭"] == "ACTIVE" else "sp-paused"
                        sp_text   = "?댁쁺以? if row["?곹깭"] == "ACTIVE" else "?뺤?"
                        spend_per = "?? if row["援щℓ?밸퉬??] == 999999999 else f"{row['援щℓ?밸퉬??]:,.0f}??

                        # ?뺣젹 湲곗????곕씪 媛뺤“ 吏???숈쟻 寃곗젙
                        primary_map = {
                            "ROAS":     ("ROAS",     roas_pct,                        rc),
                            "援щℓ?밸퉬??: ("援щℓ?밸퉬??, spend_per,                       "#18181b"),
                            "CVR":      ("CVR",      f"{row['CVR(%)']}%",             "#18181b"),
                            "?꾪솚湲덉븸":  ("?꾪솚湲덉븸",  f"{row['援щℓ?꾪솚湲덉븸']:,.0f}??,   "#18181b"),
                        }
                        p_lbl, p_val, p_clr = primary_map.get(sort_label, ("ROAS", roas_pct, rc))

                        # ?섎㉧吏 3媛?蹂댁“ 吏??(湲곗? ?쒖쇅)
                        all_sec = [
                            ("ROAS",     roas_pct,                      rc),
                            ("援щℓ?밸퉬??, spend_per,                     "#18181b"),
                            ("愿묎퀬鍮?,   f"{row['鍮꾩슜']:,.0f}??,          "#18181b"),
                            ("援щℓ??,   f"{int(row['援щℓ?꾪솚'])}嫄?,       "#18181b"),
                        ]
                        sec = [m for m in all_sec if m[0] != p_lbl][:3]

                        yt_id = get_youtube_id(row["愿묎퀬紐?])
                        ig_url = row.get("instagram_url", "")
                        if yt_id:
                            fb      = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
                            yt_link = f"https://www.youtube.com/shorts/{yt_id}"
                            th  = f'<a href="{yt_link}" target="_blank" style="display:block;width:100%;height:100%;"><img src="https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg" onerror="this.src=\'{fb}\'" style="width:100%;height:100%;object-fit:contain;"></a>'
                        elif row["?몃꽕??]:
                            img = f'<img src="{row["?몃꽕??]}" style="width:100%;height:100%;object-fit:contain;">'
                            th  = f'<a href="{ig_url}" target="_blank" style="display:block;width:100%;height:100%;">{img}</a>' if ig_url else img
                        else:
                            lbl = "?렗" if row["?곸긽?щ?"] else "??
                            th  = f'<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:#a1a1aa;">{lbl}</div>'

                        cards_html += f"""
<div style="background:#fff;border-radius:12px;overflow:hidden;
            border:1px solid #f0f0f0;margin-bottom:8px;
            box-shadow:0 1px 3px rgba(0,0,0,0.05);">
  <div style="position:relative;height:200px;background:#18181b;overflow:hidden;">
    {th}
    <span class="status-pill {sp_cls}">{sp_text}</span>
  </div>
  <div style="padding:0.6rem 0.65rem;">
    <div style="font-size:0.75rem;font-weight:700;color:#18181b;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                margin-bottom:0.45rem;" title="{row['愿묎퀬紐?]}">{row['愿묎퀬紐?]}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
      <div style="background:#f0f9ff;border:1.5px solid #bae6fd;border-radius:6px;
                  padding:0.35rem;text-align:center;grid-column:span 2;">
        <div style="font-size:0.55rem;color:#0284c7;font-weight:700;">{p_lbl}</div>
        <div style="font-size:0.88rem;font-weight:700;color:{p_clr};">{p_val}</div>
      </div>
      {''.join(f"""<div style="background:#fafaf9;border-radius:6px;padding:0.3rem;
                  text-align:center;border:1px solid #f0f0f0;">
        <div style="font-size:0.55rem;color:#a1a1aa;">{m[0]}</div>
        <div style="font-size:0.72rem;font-weight:700;color:{m[2]};">{m[1]}</div>
      </div>""" for m in sec)}
    </div>
  </div>
</div>"""
                    st.markdown(cards_html, unsafe_allow_html=True)
            # ???ъ씠 援щ텇??            if row_start + MAX_COLS < n:
                st.markdown("<hr style='border:none;border-top:1px solid #e4e4e7;margin:1.5rem 0;'>",
                            unsafe_allow_html=True)

    # ?? AI ?⑥쑉 遺꾩꽍 ???????????????????????????????????????????
    def render_ai_analysis(df_all, ai_start_str="", ai_end_str=""):
        st.markdown('<p class="section-title">?쨼 AI 愿묎퀬 ?⑥쑉 遺꾩꽍</p>', unsafe_allow_html=True)
        period_txt = f"{ai_start_str} ~ {ai_end_str} (理쒓렐 28??" if ai_start_str else ""
        st.markdown(
            f'<p class="section-sub">ROAS 1?쒖쐞 쨌 援щℓ?밸퉬??2?쒖쐞 湲곗? 쨌 OFF ?뚯옱 ?ы븿 遺꾩꽍'
            f'{"  |  ?뿎 " + period_txt if period_txt else ""}</p>',
            unsafe_allow_html=True
        )

        df_a = df_all.copy()

        # ?먯닔 怨꾩궛: ROAS 二쇱슂, 援щℓ?밸퉬??蹂댁“
        max_cpp = df_a[df_a["援щℓ?밸퉬??] < 999999999]["援щℓ?밸퉬??].max() if (df_a["援щℓ?밸퉬??] < 999999999).any() else 1
        def score(row):
            r = row["ROAS"] * 100
            c = (1 - row["援щℓ?밸퉬??] / max_cpp) * 20 if row["援щℓ?밸퉬??] < 999999999 else -20
            return r + c
        df_a["_score"] = df_a.apply(score, axis=1)
        df_a = df_a.sort_values("_score", ascending=False).reset_index(drop=True)

        def perf_info(row):
            if row["ROAS"] >= 2.0: return "?곗닔", "#16a34a", "?윟"
            if row["ROAS"] >= 1.0: return "?묓샇", "#d97706", "?윞"
            return "?議?, "#dc2626", "?뵶"

        CPO_LIMIT = 79000  # 援щℓ?밸퉬???곹븳 (3援ъ냼耳?湲곗?)

        # ?꾧린 ?쒖븞: ?댁쁺以?+ (ROAS < 1.0 OR 援щℓ?밸퉬??> ?곹븳) + ?섎? ?덈뒗 鍮꾩슜
        avg_spend = df_a["鍮꾩슜"].mean()
        min_spend = max(avg_spend * 0.3, 5000)
        turn_off = df_a[
            (df_a["?곹깭"] == "ACTIVE") &
            (df_a["鍮꾩슜"] >= min_spend) &
            (
                (df_a["ROAS"] < 1.0) |
                (
                    (df_a["援щℓ?꾪솚"] >= 1) &
                    (df_a["援щℓ?밸퉬??] > CPO_LIMIT)
                )
            )
        ]
        # 耳쒓린 ?쒖븞: ?뺤? ?곹깭 + ROAS >= 1.5 + 援щℓ?밸퉬??<= ?곹븳 + 援щℓ 1嫄??댁긽
        paused_mask = ~df_a["?곹깭"].isin(["ACTIVE"])
        turn_on = df_a[
            paused_mask &
            (df_a["ROAS"] >= 1.5) &
            (df_a["援щℓ?꾪솚"] >= 1) &
            (df_a["援щℓ?밸퉬??] <= CPO_LIMIT)
        ]

        # ?붿빟 移대뱶
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
<div style="background:#fef2f2;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #fecaca;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#dc2626;">{len(turn_off)}</div>
  <div style="font-size:0.72rem;color:#ef4444;margin-top:0.2rem;">?뵶 ?꾧린 ?쒖븞</div>
</div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
<div style="background:#f0fdf4;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #bbf7d0;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#16a34a;">{len(turn_on)}</div>
  <div style="font-size:0.72rem;color:#16a34a;margin-top:0.2rem;">?윟 耳쒓린 ?쒖븞</div>
</div>""", unsafe_allow_html=True)
        with col_c:
            others = len(df_a) - len(turn_off) - len(turn_on)
            st.markdown(f"""
<div style="background:#f8fafc;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #e2e8f0;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#64748b;">{others}</div>
  <div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem;">???꾩긽 ?좎?</div>
</div>""", unsafe_allow_html=True)

        def ad_row_html(row, border_color):
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "?? if row["援щℓ?밸퉬??] == 999999999 else f"{row['援щℓ?밸퉬??]:,.0f}??
            perf_lbl, perf_clr, _ = perf_info(row)
            return f"""
<div style="background:#fff;border-radius:12px;padding:0.85rem 1rem;
            border:1px solid {border_color};margin-bottom:0.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;">
    <span style="font-size:0.85rem;font-weight:700;color:#18181b;
                 flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;
                 white-space:nowrap;">{row['愿묎퀬紐?]}</span>
    <span style="font-size:0.65rem;color:#a1a1aa;flex-shrink:0;">{row['愿묎퀬?명듃']}</span>
  </div>
  <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">
    <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
    <span style="font-size:0.75rem;">愿묎퀬鍮?<strong>{row['鍮꾩슜']:,.0f}??/strong></span>
    <span style="font-size:0.75rem;">援щℓ?밸퉬??<strong>{spend_per}</strong></span>
    <span style="font-size:0.75rem;">援щℓ??<strong>{int(row['援щℓ?꾪솚'])}嫄?/strong></span>
  </div>
</div>"""

        # ?꾧린 ?쒖븞 ?뱀뀡
        if len(turn_off) > 0:
            st.markdown(f'<p class="section-title">?뵶 ?꾧린 ?쒖븞 ??{len(turn_off)}媛??뚯옱</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">?댁쁺 以묒씠吏留?ROAS媛 ??굅??援щℓ?밸퉬?⑹씠 79,000?먯쓣 珥덇낵?섎뒗 ?뚯옱?낅땲??</p>', unsafe_allow_html=True)
            for _, row in turn_off.iterrows():
                st.markdown(ad_row_html(row, "#fecaca"), unsafe_allow_html=True)

        # 耳쒓린 ?쒖븞 ?뱀뀡
        if len(turn_on) > 0:
            st.markdown(f'<p class="section-title" style="margin-top:1.2rem;">?윟 耳쒓린 ?쒖븞 ??{len(turn_on)}媛??뚯옱</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">?뺤? ?곹깭吏留?ROAS 150% ?댁긽 + 援щℓ?밸퉬??79,000???댄븯濡??깃낵媛 寃利앸맂 ?뚯옱?낅땲??</p>', unsafe_allow_html=True)
            for _, row in turn_on.iterrows():
                st.markdown(ad_row_html(row, "#bbf7d0"), unsafe_allow_html=True)

        if len(turn_off) == 0 and len(turn_on) == 0:
            st.success("???꾩옱 紐⑤뱺 ?뚯옱媛 理쒖쟻 ?곹깭?낅땲?? ?밸퀎??議곗튂媛 ?꾩슂?섏? ?딆븘??")

        # ?꾩껜 ?쒖쐞 ?뚯씠釉?        st.markdown('<p class="section-title" style="margin-top:1.8rem;">?뱥 ?꾩껜 ?뚯옱 ?⑥쑉 ?쒖쐞</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">ROAS 쨌 援щℓ?밸퉬??湲곗? 醫낇빀 ?먯닔???뺣젹 (OFF ?뚯옱 ?ы븿)</p>', unsafe_allow_html=True)
        for rank_i, (_, row) in enumerate(df_a.iterrows()):
            perf_lbl, perf_clr, perf_emoji = perf_info(row)
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "?? if row["援щℓ?밸퉬??] == 999999999 else f"{row['援щℓ?밸퉬??]:,.0f}??
            status_ico = "?윟 ?댁쁺以? if row["?곹깭"] == "ACTIVE" else "???뺤?"
            st.markdown(f"""
<div style="background:#fff;border-radius:10px;padding:0.65rem 1rem;
            border:1px solid #f0f0f0;border-left:4px solid {perf_clr};
            margin-bottom:0.35rem;display:flex;align-items:center;gap:0.8rem;">
  <span style="font-size:0.78rem;font-weight:700;color:#a1a1aa;min-width:22px;">#{rank_i+1}</span>
  <span style="font-size:0.9rem;">{perf_emoji}</span>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.82rem;font-weight:700;color:#18181b;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row['愿묎퀬紐?]}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">{status_ico} 쨌 {row['愿묎퀬?명듃']}</div>
  </div>
  <div style="display:flex;gap:1.2rem;flex-shrink:0;flex-wrap:wrap;justify-content:flex-end;">
    <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
    <span style="font-size:0.75rem;">援щℓ?밸퉬??<strong>{spend_per}</strong></span>
    <span style="font-size:0.75rem;">愿묎퀬鍮?<strong>{row['鍮꾩슜']:,.0f}??/strong></span>
  </div>
</div>""", unsafe_allow_html=True)

    # ?? ?ㅻ퉬寃뚯씠??(?몄뀡 ?ㅽ뀒?댄듃濡????좎?) ?????????????????????
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "summary"

    nav_items = {
        "summary": "?뱤  Summary",
        "list":    "?뱥  ?뚯옱 紐⑸줉",
        "ai":      "?쨼  AI 遺꾩꽍",
    }
    nav_cols = st.columns(len(nav_items))
    for col, (key, label) in zip(nav_cols, nav_items.items()):
        with col:
            is_active = (st.session_state.active_tab == key)
            if st.button(
                label,
                key=f"nav_{key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_tab = key

    st.markdown("<div style='margin-top:1rem;border-top:1px solid #e4e4e7;padding-top:1.2rem;'></div>",
                unsafe_allow_html=True)

    # ?? 而⑦뀗痢??뚮뜑留??????????????????????????????????????????
    if st.session_state.active_tab == "summary":
        render_summary(df)

    elif st.session_state.active_tab == "list":
        sort_options = {
            "?뱢 ROAS":      ("ROAS",        False, "ROAS"),
            "?뮯 援щℓ?밸퉬??: ("援щℓ?밸퉬??,   True,  "援щℓ?밸퉬??),
            "?렞 CVR":       ("CVR(%)",       False, "CVR"),
            "?뮥 ?꾪솚湲덉븸":  ("援щℓ?꾪솚湲덉븸",  False, "?꾪솚湲덉븸"),
        }
        if "list_sort" not in st.session_state:
            st.session_state.list_sort = "?뱢 ROAS"

        # ?? 罹좏럹???꾪꽣 ??????????????????????????????????????????
        campaign_list = sorted(df["罹좏럹??].dropna().unique().tolist())
        if "selected_campaign" not in st.session_state or st.session_state.selected_campaign not in campaign_list:
            st.session_state.selected_campaign = campaign_list[0] if campaign_list else None

        if len(campaign_list) > 1:
            st.markdown(
                '<p style="font-size:0.72rem;color:#a1a1aa;margin:0 0 0.3rem 0;">罹좏럹???좏깮</p>',
                unsafe_allow_html=True
            )
            camp_cols = st.columns(len(campaign_list))
            for i, camp in enumerate(campaign_list):
                with camp_cols[i]:
                    is_sel = (st.session_state.selected_campaign == camp)
                    # 吏㏐쾶 ?쒖떆 (??15??
                    short_name = camp[:15] + "?? if len(camp) > 15 else camp
                    if st.button(
                        short_name,
                        key=f"camp_btn_{i}",
                        type="primary" if is_sel else "secondary",
                        use_container_width=True,
                        help=camp,
                    ):
                        st.session_state.selected_campaign = camp
            st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

        # ?좏깮??罹좏럹?몄쑝濡??꾪꽣留?        df_filtered = df[df["罹좏럹??] == st.session_state.selected_campaign] if st.session_state.selected_campaign else df

        st.markdown(
            '<p style="font-size:0.72rem;color:#a1a1aa;margin:0 0 0.4rem 0;">?명듃 ???뚯옱 ?뺣젹 湲곗?</p>',
            unsafe_allow_html=True
        )
        sort_cols = st.columns(len(sort_options))
        for i, label in enumerate(sort_options):
            with sort_cols[i]:
                is_active = (st.session_state.list_sort == label)
                if st.button(
                    label,
                    key=f"sort_btn_{label}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.list_sort = label

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
        col_key, asc, sort_label = sort_options[st.session_state.list_sort]
        render_adset_horizontal(df_filtered, col_key, asc, sort_label)

    elif st.session_state.active_tab == "ai":
        # AI 遺꾩꽍? ??긽 理쒓렐 28???곗씠???ъ슜
        ai_end   = date.today()
        ai_start = ai_end - timedelta(days=27)  # ?ㅻ뒛 ?ы븿 28??        ai_start_str = str(ai_start)
        ai_end_str   = str(ai_end)

        # ?좎쭨媛 諛붾뚮㈃ 罹먯떆 臾댄슚??        if st.session_state.get("ai_date_range") != (ai_start_str, ai_end_str):
            st.session_state.pop("df_ai", None)
            st.session_state.ai_date_range = (ai_start_str, ai_end_str)

        if "df_ai" not in st.session_state:
            with st.spinner("AI 遺꾩꽍???곗씠??議고쉶 以?(理쒓렐 28??..."):
                try:
                    ai_rows = fetch_ad_data(
                        ai_start_str, ai_end_str,
                        ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET
                    )
                    st.session_state.df_ai = pd.DataFrame(ai_rows)
                except Exception as e:
                    st.error(f"AI 遺꾩꽍 ?곗씠???ㅻ쪟: {e}")
                    st.session_state.df_ai = df.copy()

        render_ai_analysis(st.session_state.df_ai, ai_start_str, ai_end_str)

    # ?? CSV ???????????????????????????????????????????????????
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    csv = df.drop(columns=["?몃꽕??, "?곸긽?щ?", "ad_id", "ad_status", "instagram_url"], errors="ignore").to_csv(index=False).encode("utf-8-sig")
    st.download_button("?뱿 CSV ?ㅼ슫濡쒕뱶", csv, "ad_performance.csv", "text/csv")

