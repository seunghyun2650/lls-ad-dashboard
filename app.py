import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ── 유튜브 영상 매핑 (기본값 - 키워드:영상ID) ────────────────
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
    "멀티탭_a":    "Memt7hADi8U",
    "멀티탭_b":    "UyoT0y9NdHU",
    "멀티탭_c":    "x8PYIpQYzA0",
    "dahyunjae":   "Zh6qo1DdFew",
    "@dahyunjae":  "Zh6qo1DdFew",
    "구일이":      "Nn84wnsQssQ",
}

def get_youtube_id(ad_name):
    name_lower = ad_name.lower()
    for keyword, vid_id in YOUTUBE_MAP.items():
        if keyword in name_lower:
            return vid_id
    return None

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(page_title="LLS AD Dashboard", page_icon="🌿", layout="wide")

# ── 로그인 ────────────────────────────────────────────────────
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;
                    height:70vh;flex-direction:column;gap:0.4rem;'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>🌿</div>
            <h1 style='color:#18181b;font-size:1.8rem;font-weight:700;margin:0;'>LLS AD Dashboard</h1>
            <p style='color:#a1a1aa;font-size:0.9rem;margin:0 0 1.5rem 0;'>광고 소재 효율 분석 대시보드</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.2, 1, 1.2])
        with col2:
            pw = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
            if st.button("로그인", use_container_width=True):
                if pw == st.secrets.get("DASHBOARD_PASSWORD", "lls2024"):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
        st.stop()

check_login()

try:
    ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
    AD_ACCOUNT_ID = st.secrets["AD_ACCOUNT_ID"]
    APP_ID = st.secrets["APP_ID"]
    APP_SECRET = st.secrets["APP_SECRET"]
except Exception as _se:
    st.error(f"⚠️ Secrets 설정 오류: {_se}")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 */
.stApp, .stAppViewContainer,
section[data-testid="stMain"] > div,
.block-container {
    background: #f7f6f3 !important;
}

/* 상단 헤더 바 숨김 */
header[data-testid="stHeader"] { background: transparent !important; }

.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #e4e4e7;
    margin-bottom: 1.5rem;
}
.dash-title { font-size: 1.4rem; font-weight: 700; color: #18181b; margin: 0; }
.dash-sub { font-size: 0.8rem; color: #a1a1aa; margin: 0.1rem 0 0 0; }

.metrics-bar {
    display: flex;
    background: #ffffff;
    border-radius: 16px;
    padding: 1.4rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 1.8rem;
}
.metric-item { flex: 1; text-align: center; padding: 0 1rem; }
.metric-item + .metric-item { border-left: 1px solid #f0f0f0; }
.mi-label { font-size: 0.72rem; color: #a1a1aa; font-weight: 500; margin-bottom: 0.3rem; letter-spacing: 0.02em; }
.mi-value { font-size: 1.45rem; font-weight: 700; color: #18181b; line-height: 1.2; }
.mi-roas { color: #16a34a !important; }

.section-title { font-size: 0.95rem; font-weight: 700; color: #18181b; margin: 0.2rem 0 0.8rem 0; }
.section-sub { font-size: 0.78rem; color: #a1a1aa; margin: -0.4rem 0 0.8rem 0; }

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
.stButton > button:hover { background: #18181b !important; color: #ffffff !important; border-color: #18181b !important; }
.stButton > button:focus { box-shadow: none !important; outline: none !important; }

.ad-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }

.ad-card-g {
    background: #ffffff; border-radius: 16px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease; border: 1px solid #f0f0f0;
}
.ad-card-g:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }

.thumb-area { position: relative; width: 100%; height: 190px; overflow: hidden; background: #f4f4f5; }
.thumb-area img { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb-no-img { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #a1a1aa; font-size: 0.82rem; }

.status-pill {
    position: absolute; top: 9px; left: 9px; font-size: 0.65rem; font-weight: 600;
    padding: 3px 8px; border-radius: 100px; backdrop-filter: blur(4px); z-index: 10;
}
.sp-active { background: rgba(220,252,231,0.92); color: #15803d; }
.sp-paused { background: rgba(244,244,245,0.92); color: #71717a; }

.yt-badge {
    position: absolute; bottom: 9px; right: 9px; background: rgba(185,0,0,0.88);
    color: white; font-size: 0.62rem; padding: 2px 7px; border-radius: 4px; font-weight: 700;
}

.card-body { padding: 0.85rem 0.95rem 0.95rem; }
.card-ad-name { font-size: 0.82rem; font-weight: 700; color: #18181b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.1rem; }
.card-adset { font-size: 0.68rem; color: #a1a1aa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.7rem; }
.card-date { font-size: 0.65rem; color: #c4c4c4; margin-bottom: 0.65rem; }

.kpi-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 0.65rem; }
.kpi-box { background: #fafaf9; border-radius: 9px; padding: 0.45rem 0.3rem; text-align: center; border: 1px solid #f0f0f0; }
.kpi-box-active { background: #f0f9ff; border: 1.5px solid #bae6fd; }
.kpi-lbl { font-size: 0.6rem; color: #a1a1aa; margin-bottom: 0.15rem; font-weight: 500; }
.kpi-lbl-active { font-size: 0.6rem; color: #0284c7; margin-bottom: 0.15rem; font-weight: 700; }
.kpi-val { font-size: 0.82rem; font-weight: 700; color: #18181b; }
.kv-green { color: #16a34a !important; }
.kv-amber { color: #d97706 !important; }
.kv-red   { color: #dc2626 !important; }

.card-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.tag { font-size: 0.65rem; color: #71717a; background: #f4f4f5; border-radius: 5px; padding: 2px 7px; font-weight: 500; }

div[data-testid="column"]:last-child .stButton > button {
    font-size: 0.72rem !important; padding: 0.2rem 0.7rem !important;
    color: #a1a1aa !important; border-color: #e4e4e7 !important;
}

.stDateInput label { font-size: 0.78rem !important; color: #71717a !important; }
.stCaption { color: #a1a1aa !important; font-size: 0.75rem !important; }
.streamlit-expanderHeader { font-size: 0.8rem !important; }

.ad-list { display: flex; flex-direction: column; gap: 10px; }

.list-row {
    background: #fff; border-radius: 14px; display: flex; align-items: stretch;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #f0f0f0;
    overflow: hidden; transition: box-shadow 0.2s ease;
}
.list-row:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.list-thumb { position: relative; width: 140px; flex-shrink: 0; background: #f4f4f5; overflow: hidden; }
.list-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }

.list-body {
    flex: 1; padding: 0.85rem 1.1rem; display: flex; flex-direction: column;
    justify-content: space-between; min-width: 0; gap: 0.6rem;
}
.list-name { font-size: 0.9rem; font-weight: 700; color: #18181b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.1rem; }
.list-meta { font-size: 0.7rem; color: #a1a1aa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.list-metrics { display: flex; flex-wrap: wrap; gap: 6px; }
.lm-item { background: #fafaf9; border-radius: 8px; padding: 0.35rem 0.65rem; text-align: center; border: 1px solid #f0f0f0; min-width: 72px; }
.lm-primary { background: #f0f9ff; border-color: #bae6fd; }
.lm-lbl { font-size: 0.58rem; color: #a1a1aa; font-weight: 500; margin-bottom: 0.1rem; }
.lm-lbl-primary { font-size: 0.58rem; color: #0284c7; font-weight: 700; margin-bottom: 0.1rem; }
.lm-val { font-size: 0.82rem; font-weight: 700; color: #18181b; }

.sum-stat { flex: 1; background: white; border-radius: 12px; padding: 1rem 1.2rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #f0f0f0; }
.sum-stat-val { font-size: 1.8rem; font-weight: 700; color: #18181b; }
.sum-stat-lbl { font-size: 0.72rem; color: #a1a1aa; margin-top: 0.2rem; }

.sum-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem 0.8rem; border-radius: 10px; margin-bottom: 6px; background: white; border: 1px solid #f0f0f0; }
.sum-rank { font-size: 0.7rem; font-weight: 700; color: #a1a1aa; min-width: 22px; }
.sum-thumb { position: relative; width: 56px; height: 56px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #f4f4f5; }
.sum-thumb img { width:100%; height:100%; object-fit:cover; display:block; }
.sum-name { font-size: 0.8rem; font-weight: 600; color: #18181b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.1rem; }
.sum-roas { font-size: 0.9rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── 광고 ON/OFF API ───────────────────────────────────────────
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


# ── 헤더 ─────────────────────────────────────────────────────
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem 0; border-bottom:1px solid #e4e4e7; margin-bottom:1.5rem;">
        <p style="font-size:1.3rem;font-weight:700;color:#18181b;margin:0;">🌿 LLS AD Dashboard</p>
        <p style="font-size:0.78rem;color:#a1a1aa;margin:0.1rem 0 0 0;">Meta 광고 소재 효율 분석</p>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.markdown("<div style='padding-top:0.6rem;'>", unsafe_allow_html=True)
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── 날짜 & 조회 ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
with col1:
    start_date = st.date_input("시작일", date.today().replace(day=1))
with col2:
    end_date = st.date_input("종료일", date.today())
with col3:
    st.markdown("<div style='padding-top:1.6rem;'>", unsafe_allow_html=True)
    fetch_btn = st.button("📊  데이터 불러오기", use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div style='padding-top:1.8rem;'>", unsafe_allow_html=True)
    force_refresh = st.checkbox("🔄 최신 데이터로 새로고침", value=False)
    st.markdown("""
    <p style="font-size:0.7rem;color:#a1a1aa;margin:0.2rem 0 0 1.6rem;line-height:1.5;">
        광고를 새로 추가했거나 데이터가 바뀐 경우 체크하세요<br>
        평소엔 체크 없이 불러오면 더 빠르게 조회됩니다
    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if "df" not in st.session_state:
    st.session_state.df = None
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "구매전환금액"

# ── 캐싱 함수 ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_ad_data(start_date_str, end_date_str, access_token, ad_account_id, app_id, app_secret):
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

    ad_cache = {}
    try:
        ads = _paginate(
            f"{BASE}/{ad_account_id}/ads",
            {
                "fields": "id,name,status,effective_status,created_time,adset{id,name},campaign{id,name},creative{thumbnail_url,image_url,video_id,instagram_permalink_url}",
                "limit": 200,
                "access_token": access_token,
            },
        )
        for ad in ads:
            creative = ad.get("creative", {})
            ad_cache[str(ad["id"])] = {
                "name":                    str(ad.get("name", "")),
                "adset_name":              str(ad.get("adset", {}).get("name", "")),
                "campaign_name":           str(ad.get("campaign", {}).get("name", "")),
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
        status        = "알 수 없음"
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
            "ad_id":        ad_id,
            "ad_status":    ad_info.get("status", ""),
            "썸네일":       thumbnail_url,
            "instagram_url": ad_info.get("instagram_permalink_url", ""),
            "영상여부":      is_video,
            "캠페인":       str(data.get("campaign_name", "")),
            "광고명":       str(data.get("ad_name", "")),
            "광고세트":     str(data.get("adset_name", "")),
            "상태":         status,
            "시작일":       start_time,
            "비용":         spend,
            "구매전환":     purchases,
            "구매전환금액": purchase_value,
            "ROAS":         roas,
            "CTR(%)":       round(ctr, 2),
            "CPC":          round(cpc, 2),
            "노출수":       impressions,
            "클릭수":       clicks,
            "CVR(%)":       round(purchases / clicks * 100, 2) if clicks > 0 else 0.0,
            "구매당비용":   round(spend / purchases, 0) if purchases > 0 else 999999999,
        })

    # 인사이트에 없는 PAUSED 광고도 목록에 추가 (ON 버튼 표시용)
    insight_ad_ids = {r["ad_id"] for r in rows}
    for ad_id, ad_info in ad_cache.items():
        if ad_id in insight_ad_ids:
            continue
        video_id = ad_info.get("video_id", "")
        is_video = bool(video_id and video_id != "None")
        thumb = ad_info.get("thumbnail_url", "") if is_video else (ad_info.get("image_url", "") or ad_info.get("thumbnail_url", ""))
        rows.append({
            "ad_id":        ad_id,
            "ad_status":    ad_info.get("status", ""),
            "썸네일":       thumb,
            "instagram_url": ad_info.get("instagram_permalink_url", ""),
            "영상여부":      is_video,
            "캠페인":       ad_info.get("campaign_name", ""),
            "광고명":       ad_info.get("name", ""),
            "광고세트":     ad_info.get("adset_name", ""),
            "상태":         ad_info.get("effective_status", ad_info.get("status", "")),
            "시작일":       ad_info["created_time"][:10] if ad_info.get("created_time") else "",
            "비용":         0.0,
            "구매전환":     0,
            "구매전환금액": 0.0,
            "ROAS":         0.0,
            "CTR(%)":       0.0,
            "CPC":          0.0,
            "노출수":       0,
            "클릭수":       0,
            "CVR(%)":       0.0,
            "구매당비용":   999999999,
        })

    return rows

# ── 데이터 fetch ──────────────────────────────────────────────
if fetch_btn:
    if force_refresh:
        fetch_ad_data.clear()
    with st.spinner("Meta API에서 데이터 가져오는 중..."):
        try:
            rows = fetch_ad_data(
                str(start_date), str(end_date),
                ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET
            )
            st.session_state.df = pd.DataFrame(rows)
            cache_msg = " (새로고침)" if force_refresh else ""
            st.success(f"✅  총 {len(rows)}개 소재 로드 완료{cache_msg}")
        except Exception as e:
            st.error(f"오류 발생: {e}")


# ── 렌더링 ────────────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df
    df = df[~df["상태"].str.upper().str.contains("DELETE", na=False)].copy()
    df = df[df["상태"] != "알 수 없음"].copy()

    if df.empty or "비용" not in df.columns:
        st.info("📊 조회 버튼을 눌러 광고 데이터를 불러오세요.")
        st.stop()

    # 요약 메트릭
    total_spend      = df["비용"].sum()
    total_purchases  = df["구매전환"].sum()
    total_conv_value = df["구매전환금액"].sum()
    overall_roas     = round(total_conv_value / total_spend, 2) if total_spend > 0 else 0
    overall_roas_pct = f"{overall_roas * 100:.0f}%"
    cost_per_purchase = round(total_spend / total_purchases, 0) if total_purchases > 0 else 0

    st.markdown(f"""
    <div class="metrics-bar">
        <div class="metric-item"><div class="mi-label">총 광고비용</div><div class="mi-value">{total_spend:,.0f}원</div></div>
        <div class="metric-item"><div class="mi-label">총 구매전환</div><div class="mi-value">{total_purchases:,}건</div></div>
        <div class="metric-item"><div class="mi-label">전체 ROAS</div><div class="mi-value mi-roas">{overall_roas_pct}</div></div>
        <div class="metric-item"><div class="mi-label">총 전환금액</div><div class="mi-value">{total_conv_value:,.0f}원</div></div>
        <div class="metric-item"><div class="mi-label">평균 구매당비용</div><div class="mi-value">{cost_per_purchase:,.0f}원</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── 헬퍼 함수 ──────────────────────────────────────────────
    def roas_color_class(r):
        if r >= 3:   return "kv-green"
        elif r >= 1: return "kv-amber"
        return "kv-red"

    def thumb_inner_html(row, height=160):
        yt_id = get_youtube_id(row["광고명"])
        if yt_id:
            thumb    = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            fallback = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
            yt_url   = f"https://youtube.com/shorts/{yt_id}"
            return f'''<a href="{yt_url}" target="_blank" style="display:block;height:100%;">
  <img src="{thumb}" onerror="this.src='{fallback}'"
       style="width:100%;height:100%;object-fit:cover;display:block;" />
  <span class="yt-badge">▶ YouTube</span>
</a>'''
        url = row["썸네일"]
        if url:
            return f'''
<div style="position:absolute;inset:-20px;background-image:url('{url}');
            background-size:cover;background-position:center;
            filter:blur(20px);opacity:0.5;transform:scale(1.1);"></div>
<img src="{url}" style="position:relative;z-index:1;
     width:100%;height:100%;object-fit:contain;display:block;" />'''
        label = "🎬 영상" if row["영상여부"] else "이미지 없음"
        return f'<div class="thumb-no-img">{label}</div>'

    def render_list(df_render, sort_key="ROAS"):
        metric_order = {
            "ROAS":      ["ROAS", "전환금액", "광고비", "구매당비용", "CVR", "구매수", "CTR", "노출"],
            "구매당비용": ["구매당비용", "광고비", "ROAS", "전환금액", "CVR", "구매수", "CTR", "노출"],
            "CVR":       ["CVR", "ROAS", "광고비", "전환금액", "구매당비용", "구매수", "CTR", "노출"],
            "전환금액":  ["전환금액", "ROAS", "광고비", "구매당비용", "CVR", "구매수", "CTR", "노출"],
        }
        order = metric_order.get(sort_key, metric_order["ROAS"])

        rows_html = ""
        for i, (_, row) in enumerate(df_render.iterrows()):
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            rc        = roas_color_class(row["ROAS"])
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"
            sp_cls    = "sp-active" if row["상태"] == "ACTIVE" else "sp-paused"
            sp_text   = "운영중" if row["상태"] == "ACTIVE" else ("정지" if row["상태"] == "PAUSED" else row["상태"])
            date_txt  = row["시작일"] if row["시작일"] else "-"

            all_metrics = {
                "ROAS":      (roas_pct, rc),
                "전환금액":  (f"{row['구매전환금액']:,.0f}원", ""),
                "광고비":    (f"{row['비용']:,.0f}원", ""),
                "CVR":       (f"{row['CVR(%)']}%", ""),
                "구매당비용": (spend_per, ""),
                "구매수":    (f"{row['구매전환']}건", ""),
                "CTR":       (f"{row['CTR(%)']}%", ""),
                "노출":      (f"{row['노출수']:,}", ""),
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
      <div class="list-name">{row['광고명']}</div>
      <div class="list-meta">{row['광고세트']} · {date_txt}</div>
    </div>
    <div class="list-metrics">{metrics_html}</div>
  </div>
</div>"""

        st.markdown(f'<div class="ad-list">{rows_html}</div>', unsafe_allow_html=True)

    def render_summary(df):
        active_cnt  = len(df[df["상태"] == "ACTIVE"])
        paused_cnt  = len(df[df["상태"] == "PAUSED"])
        profitable  = len(df[df["ROAS"] >= 1])
        total_cnt   = len(df)

        st.markdown(f"""
<div style="display:flex;gap:12px;margin-bottom:1.8rem;">
  <div class="sum-stat"><div class="sum-stat-val">{total_cnt}</div><div class="sum-stat-lbl">전체 소재</div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#15803d;">{active_cnt}</div><div class="sum-stat-lbl">운영중</div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#71717a;">{paused_cnt}</div><div class="sum-stat-lbl">정지</div></div>
  <div class="sum-stat"><div class="sum-stat-val" style="color:#0284c7;">{profitable}</div><div class="sum-stat-lbl">ROAS 100% 이상</div></div>
</div>
""", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<p class="section-title">🏆 ROAS TOP 5</p>', unsafe_allow_html=True)
            top5 = df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True)
            rows = ""
            for i, (_, r) in enumerate(top5.iterrows()):
                roas_pct = f"{r['ROAS']*100:.0f}%"
                rc = roas_color_class(r["ROAS"])
                inner = thumb_inner_html(r, height=56)
                sp_cls = "sp-active" if r["상태"] == "ACTIVE" else "sp-paused"
                sp_text = "운영중" if r["상태"] == "ACTIVE" else "정지"
                rows += f"""
<div class="sum-row">
  <span class="sum-rank">#{i+1}</span>
  <div class="sum-thumb">
    {inner}
    <span class="status-pill {sp_cls}" style="font-size:0.55rem;padding:2px 5px;top:4px;left:4px;">{sp_text}</span>
  </div>
  <div style="flex:1;min-width:0;">
    <div class="sum-name">{r['광고명']}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r['광고세트']}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    <div class="sum-roas {rc}">{roas_pct}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">{r['구매전환금액']:,.0f}원</div>
  </div>
</div>"""
            st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<p class="section-title">💸 구매당비용 낮은순 TOP 5</p>', unsafe_allow_html=True)
            top5c = (df[df["구매당비용"] < 999999999]
                     .sort_values("구매당비용", ascending=True)
                     .head(5).reset_index(drop=True))
            rows = ""
            for i, (_, r) in enumerate(top5c.iterrows()):
                roas_pct = f"{r['ROAS']*100:.0f}%"
                rc = roas_color_class(r["ROAS"])
                inner = thumb_inner_html(r, height=56)
                sp_cls = "sp-active" if r["상태"] == "ACTIVE" else "sp-paused"
                sp_text = "운영중" if r["상태"] == "ACTIVE" else "정지"
                rows += f"""
<div class="sum-row">
  <span class="sum-rank">#{i+1}</span>
  <div class="sum-thumb">
    {inner}
    <span class="status-pill {sp_cls}" style="font-size:0.55rem;padding:2px 5px;top:4px;left:4px;">{sp_text}</span>
  </div>
  <div style="flex:1;min-width:0;">
    <div class="sum-name">{r['광고명']}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r['광고세트']}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    <div style="font-size:0.9rem;font-weight:700;color:#18181b;">{r['구매당비용']:,.0f}원</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">ROAS <span class="{rc}">{roas_pct}</span></div>
  </div>
</div>"""
            st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

    def render_ad_table(df_all):
        if "tbl_sort" not in st.session_state:
            st.session_state.tbl_sort = "ROAS"
            st.session_state.tbl_asc  = False

        SORT_MAP = {
            "ROAS":       ("ROAS",        False),
            "광고비":     ("비용",         False),
            "노출":       ("노출수",       False),
            "구매수":     ("구매전환",     False),
            "구매당비용": ("구매당비용",   True),
        }
        W = [0.7, 4.2, 1.1, 1.0, 1.3, 1.1, 0.9, 1.4]

        # ── CSS: 행 간격 제거 + 호버 ──────────────────────────
        st.markdown("""
<style>
div[data-testid="stVerticalBlock"]:has(.tbl-r) {
    gap: 0 !important;
}
div[data-testid="stVerticalBlock"]:has(.tbl-r) > div[data-testid="stHorizontalBlock"] {
    border-bottom: 1px solid #f0f0f0;
    align-items: center !important;
    background: #fff;
    padding-top:    0 !important;
    padding-bottom: 0 !important;
    min-height: 56px;
    transition: background 0.12s;
}
div[data-testid="stVerticalBlock"]:has(.tbl-r) > div[data-testid="stHorizontalBlock"]:hover {
    background: #f0f7ff !important;
}
div[data-testid="stVerticalBlock"]:has(.tbl-r) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding-top:    0 !important;
    padding-bottom: 0 !important;
}
div[data-testid="stVerticalBlock"]:has(.tbl-r) .stButton button {
    font-size: 0.74rem;
    min-height: 30px;
    padding: 0 0.5rem;
    border-radius: 6px;
}
</style>""", unsafe_allow_html=True)

        # ── 헤더 ──────────────────────────────────────────────
        hdr = st.columns(W)
        with hdr[0]:
            st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#6b7280;margin:0 0 0.35rem 0;">ON/OFF</p>', unsafe_allow_html=True)
        with hdr[1]:
            st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#6b7280;margin:0 0 0.35rem 0;">광고 소재</p>', unsafe_allow_html=True)
        with hdr[2]:
            st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#6b7280;margin:0 0 0.35rem 0;">상태</p>', unsafe_allow_html=True)

        for i, label in enumerate(["ROAS", "광고비", "노출", "구매수", "구매당비용"]):
            with hdr[3 + i]:
                cur   = (st.session_state.tbl_sort == label)
                arrow = (" ↑" if st.session_state.tbl_asc else " ↓") if cur else ""
                if st.button(f"{label}{arrow}", key=f"th_{label}",
                             use_container_width=True, type="primary" if cur else "secondary"):
                    if cur:
                        st.session_state.tbl_asc = not st.session_state.tbl_asc
                    else:
                        st.session_state.tbl_sort = label
                        st.session_state.tbl_asc  = SORT_MAP[label][1]
                    st.rerun()

        st.markdown('<div style="height:2px;background:#111827;margin:0.15rem 0 0 0;"></div>', unsafe_allow_html=True)

        # ── 정렬 ──────────────────────────────────────────────
        col_key = SORT_MAP[st.session_state.tbl_sort][0]
        tmp = df_all.copy()
        tmp["_active"] = (tmp["상태"] == "ACTIVE").astype(int)
        df_sorted = tmp.sort_values(["_active", col_key], ascending=[False, st.session_state.tbl_asc]).drop(columns=["_active"]).reset_index(drop=True)

        # ── 데이터 행 (container로 CSS 스코프 지정) ───────────
        with st.container():
            for _, row in df_sorted.iterrows():
                is_active  = row["상태"] == "ACTIVE"
                new_status = "PAUSED" if is_active else "ACTIVE"
                roas_pct   = f"{row['ROAS']*100:.0f}%"
                roas_clr   = "#16a34a" if row["ROAS"] >= 2 else ("#d97706" if row["ROAS"] >= 1 else "#dc2626")
                spend_per  = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"

                yt_id  = get_youtube_id(row["광고명"])
                ig_url = row.get("instagram_url", "")
                if yt_id:
                    thumb_src  = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
                    thumb_link = f"https://www.youtube.com/shorts/{yt_id}"
                elif row.get("썸네일"):
                    thumb_src, thumb_link = row["썸네일"], (ig_url or "")
                else:
                    thumb_src, thumb_link = "", ""

                if thumb_src and thumb_link:
                    th_html = f'<a href="{thumb_link}" target="_blank" style="display:block;width:40px;height:40px;flex-shrink:0;border-radius:6px;overflow:hidden;border:1px solid #e5e7eb;"><img src="{thumb_src}" style="width:100%;height:100%;object-fit:cover;"></a>'
                elif thumb_src:
                    th_html = f'<div style="width:40px;height:40px;flex-shrink:0;border-radius:6px;overflow:hidden;border:1px solid #e5e7eb;"><img src="{thumb_src}" style="width:100%;height:100%;object-fit:cover;"></div>'
                else:
                    icon = "🎬" if row.get("영상여부") else "📷"
                    th_html = f'<div style="width:40px;height:40px;flex-shrink:0;border-radius:6px;background:#f3f4f6;display:flex;align-items:center;justify-content:center;font-size:1rem;">{icon}</div>'

                r = st.columns(W)

                with r[0]:
                    st.markdown('<span class="tbl-r" style="display:none"></span>', unsafe_allow_html=True)
                    btn_lbl = "⏸ OFF" if is_active else "▶ ON"
                    if st.button(btn_lbl, key=f"tbl_{row['ad_id']}", use_container_width=True):
                        res = toggle_ad_status(row["ad_id"], new_status)
                        if res is True:
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"오류: {res}")

                with r[1]:
                    st.markdown(f'''<div style="display:flex;align-items:center;gap:0.55rem;">
  {th_html}
  <div style="min-width:0;">
    <div style="font-size:0.82rem;font-weight:600;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{row['광고명']}">{row['광고명']}</div>
    <div style="font-size:0.65rem;color:#9ca3af;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row['광고세트']}</div>
  </div>
</div>''', unsafe_allow_html=True)

                with r[2]:
                    if is_active:
                        st.markdown('<span style="display:inline-flex;align-items:center;gap:5px;background:#dcfce7;color:#15803d;border-radius:20px;font-size:0.65rem;font-weight:600;padding:3px 10px;white-space:nowrap;"><span style="width:6px;height:6px;border-radius:50%;background:#16a34a;flex-shrink:0;"></span>운영중</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="display:inline-flex;align-items:center;gap:5px;background:#f3f4f6;color:#6b7280;border-radius:20px;font-size:0.65rem;font-weight:600;padding:3px 10px;white-space:nowrap;"><span style="width:6px;height:6px;border-radius:50%;background:#9ca3af;flex-shrink:0;"></span>정지</span>', unsafe_allow_html=True)

                with r[3]:
                    st.markdown(f'<span style="font-size:0.88rem;font-weight:700;color:{roas_clr};">{roas_pct}</span>', unsafe_allow_html=True)

                with r[4]:
                    st.markdown(f'<span style="font-size:0.82rem;color:#374151;">{row["비용"]:,.0f}원</span>', unsafe_allow_html=True)

                with r[5]:
                    st.markdown(f'<span style="font-size:0.82rem;color:#374151;">{row["노출수"]:,}</span>', unsafe_allow_html=True)

                with r[6]:
                    st.markdown(f'<span style="font-size:0.82rem;color:#374151;">{int(row["구매전환"])}건</span>', unsafe_allow_html=True)

                with r[7]:
                    st.markdown(f'<span style="font-size:0.82rem;color:#374151;">{spend_per}</span>', unsafe_allow_html=True)

    # ── AI 효율 분석 ───────────────────────────────────────────
    def render_ai_analysis(df_all, ai_start_str="", ai_end_str=""):
        st.markdown('<p class="section-title">🤖 AI 광고 효율 분석</p>', unsafe_allow_html=True)
        period_txt = f"{ai_start_str} ~ {ai_end_str} (최근 28일)" if ai_start_str else ""
        st.markdown(
            f'<p class="section-sub">ROAS 1순위 · 구매당비용 2순위 기준 · OFF 소재 포함 분석'
            f'{"  |  🗓 " + period_txt if period_txt else ""}</p>',
            unsafe_allow_html=True
        )

        df_a = df_all.copy()
        max_cpp = df_a[df_a["구매당비용"] < 999999999]["구매당비용"].max() if (df_a["구매당비용"] < 999999999).any() else 1
        def score(row):
            r = row["ROAS"] * 100
            c = (1 - row["구매당비용"] / max_cpp) * 20 if row["구매당비용"] < 999999999 else -20
            return r + c
        df_a["_score"] = df_a.apply(score, axis=1)
        df_a = df_a.sort_values("_score", ascending=False).reset_index(drop=True)

        def perf_info(row):
            if row["ROAS"] >= 2.0: return "우수", "#16a34a", "🟢"
            if row["ROAS"] >= 1.0: return "양호", "#d97706", "🟡"
            return "저조", "#dc2626", "🔴"

        CPO_LIMIT = 79000
        avg_spend = df_a["비용"].mean()
        min_spend = max(avg_spend * 0.3, 5000)
        turn_off = df_a[
            (df_a["상태"] == "ACTIVE") &
            (df_a["비용"] >= min_spend) &
            ((df_a["ROAS"] < 1.0) | ((df_a["구매전환"] >= 1) & (df_a["구매당비용"] > CPO_LIMIT)))
        ]
        paused_mask = ~df_a["상태"].isin(["ACTIVE"])
        turn_on = df_a[
            paused_mask &
            (df_a["ROAS"] >= 1.5) &
            (df_a["구매전환"] >= 1) &
            (df_a["구매당비용"] <= CPO_LIMIT)
        ]

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f'<div style="background:#fef2f2;border-radius:12px;padding:1rem;text-align:center;border:1px solid #fecaca;margin-bottom:1.2rem;"><div style="font-size:1.8rem;font-weight:700;color:#dc2626;">{len(turn_off)}</div><div style="font-size:0.72rem;color:#ef4444;margin-top:0.2rem;">🔴 끄기 제안</div></div>', unsafe_allow_html=True)
        with col_b:
            st.markdown(f'<div style="background:#f0fdf4;border-radius:12px;padding:1rem;text-align:center;border:1px solid #bbf7d0;margin-bottom:1.2rem;"><div style="font-size:1.8rem;font-weight:700;color:#16a34a;">{len(turn_on)}</div><div style="font-size:0.72rem;color:#16a34a;margin-top:0.2rem;">🟢 켜기 제안</div></div>', unsafe_allow_html=True)
        with col_c:
            others = len(df_a) - len(turn_off) - len(turn_on)
            st.markdown(f'<div style="background:#f8fafc;border-radius:12px;padding:1rem;text-align:center;border:1px solid #e2e8f0;margin-bottom:1.2rem;"><div style="font-size:1.8rem;font-weight:700;color:#64748b;">{others}</div><div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem;">⚪ 현상 유지</div></div>', unsafe_allow_html=True)

        def render_ad_row_with_btn(row, border_color, btn_label, new_status, btn_color, section=""):
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"
            _, perf_clr, _ = perf_info(row)

            yt_id  = get_youtube_id(row["광고명"])
            ig_url = row.get("instagram_url", "")
            if yt_id:
                thumb_src = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
                thumb_link = f"https://www.youtube.com/shorts/{yt_id}"
            elif row.get("썸네일"):
                thumb_src  = row["썸네일"]
                thumb_link = ig_url if ig_url else ""
            else:
                thumb_src  = ""
                thumb_link = ig_url if ig_url else ""

            if thumb_src:
                thumb_html = f'''<a href="{thumb_link}" target="_blank" style="display:block;width:56px;height:56px;flex-shrink:0;border-radius:8px;overflow:hidden;border:1px solid #f0f0f0;">
  <img src="{thumb_src}" style="width:100%;height:100%;object-fit:cover;">
</a>''' if thumb_link else f'<div style="width:56px;height:56px;flex-shrink:0;border-radius:8px;overflow:hidden;border:1px solid #f0f0f0;"><img src="{thumb_src}" style="width:100%;height:100%;object-fit:cover;"></div>'
            else:
                thumb_html = f'<div style="width:56px;height:56px;flex-shrink:0;border-radius:8px;background:#f4f4f5;display:flex;align-items:center;justify-content:center;font-size:1.2rem;">{"🎬" if row.get("영상여부") else "📷"}</div>'

            col_info, col_btn = st.columns([9, 1])
            with col_info:
                st.markdown(f"""
<div style="background:#fff;border-radius:12px;padding:0.75rem 1rem;border:1px solid {border_color};margin-bottom:0.5rem;display:flex;align-items:center;gap:0.85rem;">
  {thumb_html}
  <div style="flex:1;min-width:0;">
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
      <span style="font-size:0.85rem;font-weight:700;color:#18181b;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row['광고명']}</span>
      <span style="font-size:0.65rem;color:#a1a1aa;flex-shrink:0;">{row['광고세트']}</span>
    </div>
    <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">
      <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
      <span style="font-size:0.75rem;">광고비 <strong>{row['비용']:,.0f}원</strong></span>
      <span style="font-size:0.75rem;">구매당비용 <strong>{spend_per}</strong></span>
      <span style="font-size:0.75rem;">구매수 <strong>{int(row['구매전환'])}건</strong></span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='padding-top:0.4rem;'>", unsafe_allow_html=True)
                if st.button(btn_label, key=f"toggle_{section}_{row['ad_id']}_{new_status}"):
                    result = toggle_ad_status(row["ad_id"], new_status)
                    if result is True:
                        st.success(f"✅ {btn_label} 완료")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"오류: {result}")
                st.markdown("</div>", unsafe_allow_html=True)

        if len(turn_off) > 0:
            st.markdown(f'<p class="section-title">🔴 끄기 제안 — {len(turn_off)}개 소재</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">운영 중이지만 ROAS가 낮거나 구매당비용이 79,000원을 초과하는 소재입니다.</p>', unsafe_allow_html=True)
            for _, row in turn_off.iterrows():
                render_ad_row_with_btn(row, "#fecaca", "⏸ OFF", "PAUSED", "#dc2626", section="off")

        if len(turn_on) > 0:
            st.markdown(f'<p class="section-title" style="margin-top:1.2rem;">🟢 켜기 제안 — {len(turn_on)}개 소재</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">정지 상태지만 ROAS 150% 이상 + 구매당비용 79,000원 이하로 성과가 검증된 소재입니다.</p>', unsafe_allow_html=True)
            for _, row in turn_on.iterrows():
                render_ad_row_with_btn(row, "#bbf7d0", "▶ ON", "ACTIVE", "#16a34a", section="on")

        if len(turn_off) == 0 and len(turn_on) == 0:
            st.success("✅ 현재 모든 소재가 최적 상태입니다! 특별한 조치가 필요하지 않아요.")

        # 현상 유지 소재 (끄기/켜기 제안 제외한 나머지 ACTIVE 소재)
        turnoff_ids = set(turn_off["ad_id"].tolist())
        turnon_ids  = set(turn_on["ad_id"].tolist())
        status_quo  = df_a[
            (df_a["상태"] == "ACTIVE") &
            (~df_a["ad_id"].isin(turnoff_ids))
        ]
        if len(status_quo) > 0:
            st.markdown(f'<p class="section-title" style="margin-top:1.8rem;">⚪ 현상 유지 소재 — {len(status_quo)}개</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">AI가 별도 조치를 제안하지 않은 운영 중 소재입니다. 결이 안 맞으면 직접 끄세요.</p>', unsafe_allow_html=True)
            for _, row in status_quo.iterrows():
                render_ad_row_with_btn(row, "#f0f0f0", "⏸ OFF", "PAUSED", "#71717a", section="sq")

        # 현재 꺼진 소재 전체 목록 (성과 무관)
        all_paused = df_a[~df_a["상태"].isin(["ACTIVE"])]
        if len(all_paused) > 0:
            st.markdown(f'<p class="section-title" style="margin-top:1.8rem;">⏸ 현재 정지된 소재 — {len(all_paused)}개</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">현재 꺼져 있는 소재 전체입니다. 바로 켤 수 있어요.</p>', unsafe_allow_html=True)
            for _, row in all_paused.iterrows():
                render_ad_row_with_btn(row, "#e4e4e7", "▶ ON", "ACTIVE", "#16a34a", section="paused")

        st.markdown('<p class="section-title" style="margin-top:1.8rem;">📋 전체 소재 효율 순위</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">ROAS · 구매당비용 기준 종합 점수순 정렬 (OFF 소재 포함)</p>', unsafe_allow_html=True)
        for rank_i, (_, row) in enumerate(df_a.iterrows()):
            perf_lbl, perf_clr, perf_emoji = perf_info(row)
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"
            status_ico = "🟢 운영중" if row["상태"] == "ACTIVE" else "⏸ 정지"
            st.markdown(f"""
<div style="background:#fff;border-radius:10px;padding:0.65rem 1rem;border:1px solid #f0f0f0;border-left:4px solid {perf_clr};margin-bottom:0.35rem;display:flex;align-items:center;gap:0.8rem;">
  <span style="font-size:0.78rem;font-weight:700;color:#a1a1aa;min-width:22px;">#{rank_i+1}</span>
  <span style="font-size:0.9rem;">{perf_emoji}</span>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.82rem;font-weight:700;color:#18181b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row['광고명']}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">{status_ico} · {row['광고세트']}</div>
  </div>
  <div style="display:flex;gap:1.2rem;flex-shrink:0;flex-wrap:wrap;justify-content:flex-end;">
    <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
    <span style="font-size:0.75rem;">구매당비용 <strong>{spend_per}</strong></span>
    <span style="font-size:0.75rem;">광고비 <strong>{row['비용']:,.0f}원</strong></span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── (협력광고 탭 제거됨) ──────────────────────────────────
    def create_collab_ad(ad_name, adset_id, ad_code, landing_url, content_url):
        from facebook_business.adobjects.adaccount import AdAccount
        import re as _re
        shortcode_match = _re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", content_url)
        if not shortcode_match:
            raise ValueError("올바른 인스타그램 URL이 아닙니다.")
        import requests as _req
        creative_params = {
            "name": f"{ad_name}_크리에이티브",
            "instagram_permalink_url": content_url,
            "call_to_action": {
                "type": "SHOP_NOW",
                "value": {"link": landing_url}
            },
        }
        if ad_code:
            creative_params["tracking_specs"] = [
                {"action.type": ["offsite_conversion"], "fb_pixel": [ad_code]}
            ]
        account = AdAccount(AD_ACCOUNT_ID)
        creative = account.create_ad_creative(params=creative_params)
        ad_params = {
            "name": ad_name,
            "adset_id": adset_id,
            "creative": {"creative_id": creative["id"]},
            "status": "ACTIVE",
        }
        ad = account.create_ad(params=ad_params)
        return ad["id"]

    def render_collab_ad(df_all):
        from facebook_business.adobjects.adaccount import AdAccount
        st.markdown('<p class="section-title">📢 협력광고 자동 생성</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">인플루언서 DM으로 받은 정보를 입력하면 메타 광고가 자동으로 만들어집니다.</p>', unsafe_allow_html=True)

        adset_list = sorted(df_all["광고세트"].dropna().unique().tolist())
        adset_options = {name: name for name in adset_list}

        with st.form("collab_ad_form"):
            ad_name = st.text_input("광고 이름 *", placeholder="예) 240601_솔섬_협력광고")
            selected_adset = st.selectbox("광고세트 선택 * (맥스팀이 미리 만들어 둔 광고세트)", options=adset_list)
            ad_code = st.text_input("광고코드 *", placeholder="인플루언서 DM으로 받은 협력사 트래킹 코드")
            landing_url = st.text_input("랜딩 URL *", placeholder="예) https://www.lls.co.kr/product/123")
            content_url = st.text_input("콘텐츠 URL *", placeholder="예) https://www.instagram.com/p/Cxxxxxx/")
            submitted = st.form_submit_button("🚀 광고 생성하기", use_container_width=True, type="primary")

        if submitted:
            import re as _re
            missing = [n for v, n in [(ad_name, "광고 이름"), (ad_code, "광고코드"), (landing_url, "랜딩 URL"), (content_url, "콘텐츠 URL")] if not v]
            if missing:
                st.error(f"입력이 빠졌어요: {', '.join(missing)}")
            elif not _re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", content_url):
                st.error("콘텐츠 URL이 올바른 인스타그램 주소가 아닙니다.\n예) https://www.instagram.com/p/Cxxxxxx/")
            elif not landing_url.startswith("http"):
                st.error("랜딩 URL은 http:// 또는 https://로 시작해야 합니다.")
            else:
                adset_id_map = df_all[["광고세트"]].drop_duplicates()
                adset_rows = df_all[df_all["광고세트"] == selected_adset]
                adset_id = adset_rows.iloc[0]["ad_id"] if not adset_rows.empty else None

                # ad_id 대신 실제 adset_id를 Meta API에서 가져오기
                try:
                    account = AdAccount(AD_ACCOUNT_ID)
                    adsets = account.get_ad_sets(fields=["id", "name"], params={"limit": 200})
                    adset_id_real = next((a["id"] for a in adsets if a["name"] == selected_adset), None)
                    if not adset_id_real:
                        st.error(f"광고세트 '{selected_adset}'를 Meta에서 찾을 수 없습니다.")
                    else:
                        with st.spinner("광고 생성 중..."):
                            new_ad_id = create_collab_ad(ad_name, adset_id_real, ad_code, landing_url, content_url)
                        st.success(f"✅ 광고가 생성되었습니다!")
                        st.info(f"생성된 광고 ID: `{new_ad_id}`")
                        account_num = AD_ACCOUNT_ID.replace("act_", "")
                        st.markdown(f"[메타 광고 관리자에서 확인하기](https://business.facebook.com/adsmanager/manage/ads?act={account_num})")
                        st.cache_data.clear()
                except Exception as e:
                    st.error(f"광고 생성 실패: {e}")
                    st.caption("광고코드나 콘텐츠 URL을 다시 확인해주세요.")

    # ── 네비게이션 ─────────────────────────────────────────────
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "summary"

    nav_items = {
        "summary": "📊  Summary",
        "list":    "📋  소재 목록",
        "ai":      "🤖  AI 분석",
    }
    nav_cols = st.columns(len(nav_items))
    for col, (key, label) in zip(nav_cols, nav_items.items()):
        with col:
            is_active = (st.session_state.active_tab == key)
            if st.button(label, key=f"nav_{key}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_tab = key

    st.markdown("<div style='margin-top:1rem;border-top:1px solid #e4e4e7;padding-top:1.2rem;'></div>", unsafe_allow_html=True)

    if st.session_state.active_tab == "summary":
        render_summary(df)

    elif st.session_state.active_tab == "list":
        campaign_list = sorted(df["캠페인"].dropna().unique().tolist())
        if "selected_campaign" not in st.session_state or st.session_state.selected_campaign not in campaign_list:
            st.session_state.selected_campaign = campaign_list[0] if campaign_list else None

        if len(campaign_list) > 1:
            st.markdown('<p style="font-size:0.72rem;color:#a1a1aa;margin:0 0 0.3rem 0;">캠페인 선택</p>', unsafe_allow_html=True)
            camp_cols = st.columns(len(campaign_list))
            for i, camp in enumerate(campaign_list):
                with camp_cols[i]:
                    is_sel = (st.session_state.selected_campaign == camp)
                    short_name = camp[:15] + "…" if len(camp) > 15 else camp
                    if st.button(short_name, key=f"camp_btn_{i}", type="primary" if is_sel else "secondary", use_container_width=True, help=camp):
                        st.session_state.selected_campaign = camp
            st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

        df_filtered = df[df["캠페인"] == st.session_state.selected_campaign] if st.session_state.selected_campaign else df
        render_ad_table(df_filtered)

    elif st.session_state.active_tab == "ai":
        ai_end   = date.today()
        ai_start = ai_end - timedelta(days=27)
        ai_start_str = str(ai_start)
        ai_end_str   = str(ai_end)

        if st.session_state.get("ai_date_range") != (ai_start_str, ai_end_str):
            st.session_state.pop("df_ai", None)
            st.session_state.ai_date_range = (ai_start_str, ai_end_str)

        if "df_ai" not in st.session_state:
            with st.spinner("AI 분석용 데이터 조회 중 (최근 28일)..."):
                try:
                    ai_rows = fetch_ad_data(ai_start_str, ai_end_str, ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)
                    st.session_state.df_ai = pd.DataFrame(ai_rows)
                except Exception as e:
                    st.error(f"AI 분석 데이터 오류: {e}")
                    st.session_state.df_ai = df.copy()

        render_ai_analysis(st.session_state.df_ai, ai_start_str, ai_end_str)

    # ── CSV ───────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    csv = df.drop(columns=["썸네일", "영상여부", "ad_id", "ad_status", "instagram_url"], errors="ignore").to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "ad_performance.csv", "text/csv")
