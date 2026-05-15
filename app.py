import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
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
}

def parse_youtube_id(url):
    """YouTube URL에서 영상 ID 추출 (Shorts/일반/단축 URL 모두 지원)"""
    import re
    patterns = [
        r'youtube\.com/shorts/([A-Za-z0-9_-]{11})',
        r'youtu\.be/([A-Za-z0-9_-]{11})',
        r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})',
        r'youtube\.com/embed/([A-Za-z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_id(ad_name):
    """광고명으로 YouTube ID 조회 - 세션 → Secrets → 기본맵 순으로 확인"""
    # 1. 세션 추가분 (UI에서 방금 등록한 것)
    session_map = st.session_state.get("youtube_additions", {})
    if ad_name in session_map:
        return session_map[ad_name]
    # 2. Streamlit Secrets의 [youtube_map] 섹션
    try:
        secrets_map = st.secrets.get("youtube_map", {})
        if ad_name in secrets_map:
            return secrets_map[ad_name]
    except Exception:
        pass
    # 3. 코드에 하드코딩된 기본 키워드 매핑
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
            pw = st.text_input("", type="password", placeholder="비밀번호 입력")
            if st.button("로그인", use_container_width=True):
                if pw == st.secrets.get("DASHBOARD_PASSWORD", "lls2024"):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
        st.stop()

# check_login()  # TEST 페이지 — 비밀번호 없음

ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
AD_ACCOUNT_ID = st.secrets["AD_ACCOUNT_ID"]
APP_ID = st.secrets["APP_ID"]
APP_SECRET = st.secrets["APP_SECRET"]

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

/* ── 대시보드 헤더 ── */
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

/* ── 요약 메트릭 바 ── */
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

/* ── 섹션 타이틀 ── */
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

/* ── 정렬 버튼 ── */
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

/* ── 광고 그리드 ── */
.ad-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
}

/* ── 광고 카드 ── */
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

/* ── 썸네일 영역 ── */
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

/* 상태 뱃지 */
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

/* YouTube 뱃지 */
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

/* ── 카드 본문 ── */
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

/* KPI 박스 3개 */
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

/* 하단 태그열 */
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

/* ── 로그아웃 버튼 크기 ── */
div[data-testid="column"]:last-child .stButton > button {
    font-size: 0.72rem !important;
    padding: 0.2rem 0.7rem !important;
    color: #a1a1aa !important;
    border-color: #e4e4e7 !important;
}

/* date_input, caption 색 */
.stDateInput label { font-size: 0.78rem !important; color: #71717a !important; }
.stCaption { color: #a1a1aa !important; font-size: 0.75rem !important; }

/* expander */
.streamlit-expanderHeader { font-size: 0.8rem !important; }

/* ── 리스트 뷰 ── */
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

/* ── Summary 뷰 ── */
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

# ── 광고 ON/OFF API ───────────────────────────────────────────
def toggle_ad_status(ad_id, new_status):
    """Meta API로 광고 상태 변경 (ACTIVE / PAUSED)
    ⚠️ TEST 모드: 실제 API 호출 비활성화 — main 배포 시 주석 해제"""
    # TODO: main 배포 전 아래 주석 해제
    # try:
    #     FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)
    #     ad = Ad(ad_id)
    #     ad[Ad.Field.status] = new_status
    #     ad.remote_update()
    #     return True
    # except Exception as e:
    #     return str(e)
    return True  # TEST 모드: 항상 성공으로 처리

# ── TEST 배너 ─────────────────────────────────────────────────
st.markdown("""
<div style="background:#ef4444;color:white;text-align:center;
            padding:0.6rem;border-radius:10px;margin-bottom:1rem;
            font-weight:700;font-size:0.95rem;letter-spacing:0.05em;">
    🚧 TEST 페이지 — 실제 운영 사이트가 아닙니다
</div>
""", unsafe_allow_html=True)

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
    start_date = st.date_input("시작일", date.today() - timedelta(days=30))
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
if "youtube_additions" not in st.session_state:
    st.session_state.youtube_additions = {}

# ── 캐싱 함수 (날짜가 같으면 API 재호출 없음) ─────────────────
@st.cache_data(show_spinner=False)
def fetch_ad_data(start_date_str, end_date_str, access_token, ad_account_id, app_id, app_secret):
    """날짜 범위가 같으면 캐시된 데이터 반환, 다르면 API 새로 호출.
    반환값은 순수 Python 기본 타입(list of dict)만 사용."""
    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    fields = [
        AdsInsights.Field.ad_id,
        AdsInsights.Field.ad_name,
        AdsInsights.Field.adset_id,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks,
        AdsInsights.Field.ctr,
        AdsInsights.Field.cpc,
        AdsInsights.Field.actions,
        AdsInsights.Field.action_values,
    ]
    params = {
        "time_range": {"since": start_date_str, "until": end_date_str},
        "level": "ad",
        "limit": 500,
    }
    insights = account.get_insights(fields=fields, params=params)

    # 광고 크리에이티브 일괄 조회 (plain dict만 저장)
    ad_cache = {}
    try:
        ads_cursor = account.get_ads(fields=[
            "id", "status", "effective_status", "created_time",
            "creative{thumbnail_url,image_url,video_id}",
        ], params={"limit": 200})
        for ad_item in ads_cursor:
            raw = dict(ad_item)
            ad_id = str(raw.get("id", ""))
            # creative 필드를 plain dict로 변환
            creative_raw = raw.get("creative", {})
            creative = dict(creative_raw) if creative_raw else {}
            ad_cache[ad_id] = {
                "status":           str(raw.get("status", "")),
                "effective_status": str(raw.get("effective_status", "")),
                "created_time":     str(raw.get("created_time", "")),
                "thumbnail_url":    str(creative.get("thumbnail_url", "")),
                "image_url":        str(creative.get("image_url", "")),
                "video_id":         str(creative.get("video_id", "")),
            }
    except Exception:
        pass

    rows = []
    for insight in insights:
        data = dict(insight)
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
            start_time = ad_info["created_time"][:10]
            video_id   = ad_info["video_id"]
            if video_id and video_id != "None":
                is_video      = True
                thumbnail_url = ad_info["thumbnail_url"]
            else:
                thumbnail_url = ad_info["image_url"] or ad_info["thumbnail_url"]

        rows.append({
            "ad_id":       ad_id,
            "ad_status":   ad_info.get("status", ""),
            "썸네일":      thumbnail_url,
            "영상여부":     is_video,
            "광고명":      str(data.get("ad_name", "")),
            "광고세트":     str(data.get("adset_name", "")),
            "상태":        status,
            "시작일":      start_time,
            "비용":        spend,
            "구매전환":     purchases,
            "구매전환금액":  purchase_value,
            "ROAS":        roas,
            "CTR(%)":      round(ctr, 2),
            "CPC":         round(cpc, 2),
            "노출수":      impressions,
            "클릭수":      clicks,
            "CVR(%)":      round(purchases / clicks * 100, 2) if clicks > 0 else 0.0,
            "구매당비용":   round(spend / purchases, 0) if purchases > 0 else 999999999,
        })

    return rows  # 순수 list[dict] → pickle 직렬화 가능

# ── 데이터 fetch ──────────────────────────────────────────────
if fetch_btn:
    if force_refresh:
        fetch_ad_data.clear()  # 캐시 초기화 → API 강제 재호출
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

# ── YouTube 썸네일 관리 ───────────────────────────────────────
if st.session_state.df is not None:
    df_check = st.session_state.df
    # 영상 소재 중 YouTube 매핑이 없는 것만 필터
    unmapped = df_check[df_check["영상여부"] == True]["광고명"].unique()
    unmapped = [n for n in unmapped if get_youtube_id(n) is None]

    if unmapped:
        with st.expander(f"🎬 YouTube 썸네일 미등록 영상 {len(unmapped)}개 — 클릭해서 등록"):
            st.markdown(
                '<p style="font-size:0.78rem;color:#71717a;margin-bottom:1rem;">'
                'YouTube Shorts URL을 붙여넣으면 바로 썸네일이 적용됩니다.<br>'
                '등록한 내용은 현재 세션 동안 유지되며, 새로고침 후에도 유지하려면 '
                'Streamlit Cloud → Settings → Secrets에 추가해주세요.</p>',
                unsafe_allow_html=True
            )
            for ad_name in unmapped:
                col_name, col_input, col_btn = st.columns([3, 4, 1])
                with col_name:
                    st.markdown(
                        f'<p style="font-size:0.8rem;color:#18181b;font-weight:600;'
                        f'padding-top:0.5rem;white-space:nowrap;overflow:hidden;'
                        f'text-overflow:ellipsis;" title="{ad_name}">{ad_name}</p>',
                        unsafe_allow_html=True
                    )
                with col_input:
                    url = st.text_input(
                        "URL", key=f"yt_input_{ad_name}",
                        placeholder="https://youtube.com/shorts/...",
                        label_visibility="collapsed"
                    )
                with col_btn:
                    if st.button("등록", key=f"yt_btn_{ad_name}"):
                        yt_id = parse_youtube_id(url) if url else None
                        if yt_id:
                            st.session_state.youtube_additions[ad_name] = yt_id
                            st.success(f"✅ 등록 완료!")
                            st.rerun()
                        else:
                            st.error("URL을 확인해주세요")

            pass  # TOML 코드는 배너 밖에서 표시

# ── YouTube 등록 후 Secrets 저장 안내 ────────────────────────
if st.session_state.get("youtube_additions"):
    toml_lines = "\n".join(
        f'"{k}" = "{v}"'
        for k, v in st.session_state.youtube_additions.items()
    )
    st.info(
        "🔒 **영구 저장 필요** — 아래 코드를 복사해서 "
        "Streamlit Cloud → Settings → Secrets에 붙여넣으세요. "
        "저장하지 않으면 새로고침 시 사라져요."
    )
    st.code(f"[youtube_map]\n{toml_lines}", language="toml")

# ── 렌더링 ────────────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    # 요약 메트릭
    total_spend      = df["비용"].sum()
    total_purchases  = df["구매전환"].sum()
    total_conv_value = df["구매전환금액"].sum()
    overall_roas     = round(total_conv_value / total_spend, 2) if total_spend > 0 else 0
    overall_roas_pct = f"{overall_roas * 100:.0f}%"
    cost_per_purchase = round(total_spend / total_purchases, 0) if total_purchases > 0 else 0

    st.markdown(f"""
    <div class="metrics-bar">
        <div class="metric-item">
            <div class="mi-label">총 광고비용</div>
            <div class="mi-value">{total_spend:,.0f}원</div>
        </div>
        <div class="metric-item">
            <div class="mi-label">총 구매전환</div>
            <div class="mi-value">{total_purchases:,}건</div>
        </div>
        <div class="metric-item">
            <div class="mi-label">전체 ROAS</div>
            <div class="mi-value mi-roas">{overall_roas_pct}</div>
        </div>
        <div class="metric-item">
            <div class="mi-label">총 전환금액</div>
            <div class="mi-value">{total_conv_value:,.0f}원</div>
        </div>
        <div class="metric-item">
            <div class="mi-label">평균 구매당비용</div>
            <div class="mi-value">{cost_per_purchase:,.0f}원</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 헬퍼 함수 ──────────────────────────────────────────────
    def roas_color_class(r):
        if r >= 3:   return "kv-green"
        elif r >= 1: return "kv-amber"
        return "kv-red"

    def thumb_inner_html(row, height=160):
        """썸네일 inner HTML 반환 (list/summary 공용)"""
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
        """리스트형 렌더링 — 썸네일 크게 왼쪽, 지표 오른쪽"""
        # 정렬 기준별 지표 순서 (첫 번째가 강조)
        metric_order = {
            "ROAS":     ["ROAS", "전환금액", "광고비", "구매당비용", "CVR", "구매수", "CTR", "노출"],
            "구매당비용": ["구매당비용", "광고비", "ROAS", "전환금액", "CVR", "구매수", "CTR", "노출"],
            "CVR":      ["CVR", "ROAS", "광고비", "전환금액", "구매당비용", "구매수", "CTR", "노출"],
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
                "ROAS":     (roas_pct, rc),
                "전환금액":  (f"{row['구매전환금액']:,.0f}원", ""),
                "광고비":    (f"{row['비용']:,.0f}원", ""),
                "CVR":      (f"{row['CVR(%)']}%", ""),
                "구매당비용": (spend_per, ""),
                "구매수":    (f"{row['구매전환']}건", ""),
                "CTR":      (f"{row['CTR(%)']}%", ""),
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
        """Summary 탭 — 전체 현황 + TOP 5 랭킹"""
        active_cnt    = len(df[df["상태"] == "ACTIVE"])
        paused_cnt    = len(df[df["상태"] == "PAUSED"])
        profitable    = len(df[df["ROAS"] >= 1])
        total_cnt     = len(df)

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
            # 구매가 있는 소재만 (999999999 제외)
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

    def sort_df(df, col, ascending):
        """운영중 소재 먼저, 그 안에서 지표 기준 정렬"""
        tmp = df.copy()
        tmp["_s"] = (tmp["상태"] != "ACTIVE").astype(int)  # 0=운영중, 1=정지
        return (tmp.sort_values(["_s", col], ascending=[True, ascending])
                   .drop(columns=["_s"])
                   .reset_index(drop=True))

    # ── 광고세트별 보기 ────────────────────────────────────────
    def render_adset_view(df_all, col_key="ROAS", asc=False, sort_label="ROAS"):
        adset_groups = df_all.groupby("광고세트")
        for adset_name, df_adset in adset_groups:
            adset_spend     = df_adset["비용"].sum()
            adset_cv        = df_adset["구매전환금액"].sum()
            adset_roas      = round(adset_cv / adset_spend, 2) if adset_spend > 0 else 0
            adset_roas_pct  = f"{adset_roas * 100:.0f}%"
            adset_purchases = int(df_adset["구매전환"].sum())
            active_cnt      = int((df_adset["상태"] == "ACTIVE").sum())
            rc = "color:#16a34a;" if adset_roas >= 1 else "color:#dc2626;"

            st.markdown(f"""
<div style="background:#fff;border-radius:14px;padding:1rem 1.3rem;
            margin-bottom:0.7rem;border:1px solid #e4e4e7;
            box-shadow:0 1px 4px rgba(0,0,0,0.05);">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.7rem;">
    <span style="font-size:0.95rem;font-weight:700;color:#18181b;">📁 {adset_name}</span>
    <span style="font-size:0.72rem;color:#a1a1aa;">{len(df_adset)}개 소재 · 운영중 {active_cnt}개</span>
  </div>
  <div style="display:flex;gap:2rem;">
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">광고비</div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_spend:,.0f}원</div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">ROAS</div>
         <div style="font-size:0.9rem;font-weight:700;{rc}">{adset_roas_pct}</div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">구매수</div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_purchases}건</div></div>
    <div><div style="font-size:0.62rem;color:#a1a1aa;margin-bottom:0.1rem;">전환금액</div>
         <div style="font-size:0.9rem;font-weight:700;">{adset_cv:,.0f}원</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
            render_list(sort_df(df_adset, col_key, asc), sort_label)
            st.markdown("<div style='margin-bottom:1.8rem;'></div>", unsafe_allow_html=True)

    # ── AI 효율 분석 ───────────────────────────────────────────
    def render_ai_analysis(df_all):
        st.markdown('<p class="section-title">🤖 AI 광고 효율 분석</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="section-sub">ROAS 1순위 · 구매당비용 2순위 기준 · OFF 소재 포함 분석</p>',
            unsafe_allow_html=True
        )

        df_a = df_all.copy()

        # 점수 계산: ROAS 주요, 구매당비용 보조
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

        # 끄기 제안: 운영중 + ROAS < 1.0 + 의미 있는 비용
        avg_spend = df_a["비용"].mean()
        turn_off = df_a[
            (df_a["상태"] == "ACTIVE") &
            (df_a["ROAS"] < 1.0) &
            (df_a["비용"] >= max(avg_spend * 0.3, 5000))
        ]
        # 켜기 제안: 정지 상태 + ROAS >= 1.5 + 구매 1건 이상
        paused_mask = ~df_a["상태"].isin(["ACTIVE"])
        turn_on = df_a[
            paused_mask &
            (df_a["ROAS"] >= 1.5) &
            (df_a["구매전환"] >= 1)
        ]

        # 요약 카드
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
<div style="background:#fef2f2;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #fecaca;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#dc2626;">{len(turn_off)}</div>
  <div style="font-size:0.72rem;color:#ef4444;margin-top:0.2rem;">🔴 끄기 제안</div>
</div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
<div style="background:#f0fdf4;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #bbf7d0;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#16a34a;">{len(turn_on)}</div>
  <div style="font-size:0.72rem;color:#16a34a;margin-top:0.2rem;">🟢 켜기 제안</div>
</div>""", unsafe_allow_html=True)
        with col_c:
            others = len(df_a) - len(turn_off) - len(turn_on)
            st.markdown(f"""
<div style="background:#f8fafc;border-radius:12px;padding:1rem;
            text-align:center;border:1px solid #e2e8f0;margin-bottom:1.2rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#64748b;">{others}</div>
  <div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem;">⚪ 현상 유지</div>
</div>""", unsafe_allow_html=True)

        def ad_row_html(row, border_color):
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"
            perf_lbl, perf_clr, _ = perf_info(row)
            return f"""
<div style="background:#fff;border-radius:12px;padding:0.85rem 1rem;
            border:1px solid {border_color};margin-bottom:0.5rem;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;">
    <span style="font-size:0.85rem;font-weight:700;color:#18181b;
                 flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;
                 white-space:nowrap;">{row['광고명']}</span>
    <span style="font-size:0.65rem;color:#a1a1aa;flex-shrink:0;">{row['광고세트']}</span>
  </div>
  <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">
    <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
    <span style="font-size:0.75rem;">광고비 <strong>{row['비용']:,.0f}원</strong></span>
    <span style="font-size:0.75rem;">구매당비용 <strong>{spend_per}</strong></span>
    <span style="font-size:0.75rem;">구매수 <strong>{int(row['구매전환'])}건</strong></span>
  </div>
</div>"""

        # 끄기 제안 섹션
        if len(turn_off) > 0:
            st.markdown(f'<p class="section-title">🔴 끄기 제안 — {len(turn_off)}개 소재</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">운영 중이지만 ROAS가 낮아 비용이 낭비되고 있는 소재입니다.</p>', unsafe_allow_html=True)
            for _, row in turn_off.iterrows():
                col_card, col_btn = st.columns([6, 1])
                with col_card:
                    st.markdown(ad_row_html(row, "#fecaca"), unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='padding-top:0.35rem;'>", unsafe_allow_html=True)
                    ad_id = str(row.get("ad_id", ""))
                    if ad_id and st.button("⏸ 끄기", key=f"off_{ad_id}",
                                           type="primary", use_container_width=True):
                        res = toggle_ad_status(ad_id, "PAUSED")
                        if res is True:
                            st.success("정지됨!")
                            fetch_ad_data.clear()
                            st.rerun()
                        else:
                            st.error(f"오류: {res}")
                    st.markdown("</div>", unsafe_allow_html=True)

        # 켜기 제안 섹션
        if len(turn_on) > 0:
            st.markdown(f'<p class="section-title" style="margin-top:1.2rem;">🟢 켜기 제안 — {len(turn_on)}개 소재</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-sub">현재 정지 상태지만 과거 성과가 좋았던 소재입니다.</p>', unsafe_allow_html=True)
            for _, row in turn_on.iterrows():
                col_card, col_btn = st.columns([6, 1])
                with col_card:
                    st.markdown(ad_row_html(row, "#bbf7d0"), unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='padding-top:0.35rem;'>", unsafe_allow_html=True)
                    ad_id = str(row.get("ad_id", ""))
                    if ad_id and st.button("▶ 켜기", key=f"on_{ad_id}",
                                           use_container_width=True):
                        res = toggle_ad_status(ad_id, "ACTIVE")
                        if res is True:
                            st.success("활성화!")
                            fetch_ad_data.clear()
                            st.rerun()
                        else:
                            st.error(f"오류: {res}")
                    st.markdown("</div>", unsafe_allow_html=True)

        if len(turn_off) == 0 and len(turn_on) == 0:
            st.success("✅ 현재 모든 소재가 최적 상태입니다! 특별한 조치가 필요하지 않아요.")

        # 전체 순위 테이블
        st.markdown('<p class="section-title" style="margin-top:1.8rem;">📋 전체 소재 효율 순위</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">ROAS · 구매당비용 기준 종합 점수순 정렬 (OFF 소재 포함)</p>', unsafe_allow_html=True)
        for rank_i, (_, row) in enumerate(df_a.iterrows()):
            perf_lbl, perf_clr, perf_emoji = perf_info(row)
            roas_pct  = f"{row['ROAS']*100:.0f}%"
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"
            status_ico = "🟢 운영중" if row["상태"] == "ACTIVE" else "⏸ 정지"
            st.markdown(f"""
<div style="background:#fff;border-radius:10px;padding:0.65rem 1rem;
            border:1px solid #f0f0f0;border-left:4px solid {perf_clr};
            margin-bottom:0.35rem;display:flex;align-items:center;gap:0.8rem;">
  <span style="font-size:0.78rem;font-weight:700;color:#a1a1aa;min-width:22px;">#{rank_i+1}</span>
  <span style="font-size:0.9rem;">{perf_emoji}</span>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.82rem;font-weight:700;color:#18181b;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row['광고명']}</div>
    <div style="font-size:0.65rem;color:#a1a1aa;">{status_ico} · {row['광고세트']}</div>
  </div>
  <div style="display:flex;gap:1.2rem;flex-shrink:0;flex-wrap:wrap;justify-content:flex-end;">
    <span style="font-size:0.75rem;">ROAS <strong style="color:{perf_clr};">{roas_pct}</strong></span>
    <span style="font-size:0.75rem;">구매당비용 <strong>{spend_per}</strong></span>
    <span style="font-size:0.75rem;">광고비 <strong>{row['비용']:,.0f}원</strong></span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── 탭 ────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "📊  Summary",
        "📋  소재 목록",
        "🤖  AI 분석",
    ])

    with tab1:
        render_summary(df)

    with tab2:
        # 정렬 옵션 (광고세트 안에서 적용)
        sort_options = {
            "📈 ROAS":      ("ROAS",        False, "ROAS"),
            "💸 구매당비용": ("구매당비용",   True,  "구매당비용"),
            "🎯 CVR":       ("CVR(%)",       False, "CVR"),
            "💰 전환금액":  ("구매전환금액",  False, "전환금액"),
        }

        if "list_sort" not in st.session_state:
            st.session_state.list_sort = "📈 ROAS"

        st.markdown(
            '<p style="font-size:0.72rem;color:#a1a1aa;margin:0 0 0.4rem 0;">세트 내 소재 정렬 기준</p>',
            unsafe_allow_html=True
        )
        cols = st.columns(len(sort_options))
        for i, label in enumerate(sort_options):
            with cols[i]:
                is_active = (st.session_state.list_sort == label)
                if st.button(
                    label,
                    key=f"sort_btn_{label}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.list_sort = label
                    st.rerun()

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        col_key, asc, sort_label = sort_options[st.session_state.list_sort]
        render_adset_view(df, col_key, asc, sort_label)

    with tab3:
        render_ai_analysis(df)

    # ── CSV ───────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    csv = df.drop(columns=["썸네일", "영상여부", "ad_id", "ad_status"], errors="ignore").to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "ad_performance.csv", "text/csv")
