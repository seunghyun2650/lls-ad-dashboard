import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
import pandas as pd
from datetime import date, timedelta

# ── 유튜브 영상 매핑 ──────────────────────────────────────────
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
            pw = st.text_input("", type="password", placeholder="비밀번호 입력")
            if st.button("로그인", use_container_width=True):
                if pw == st.secrets.get("DASHBOARD_PASSWORD", "lls2024"):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
        st.stop()

check_login()

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
</style>
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
        체크 후 불러오기 → Meta에서 최신 데이터 재조회<br>
        미체크 시 같은 날짜면 저장된 데이터 사용 (빠름)
    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if "df" not in st.session_state:
    st.session_state.df = None
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "구매전환금액"

# ── 캐싱 함수 (날짜가 같으면 API 재호출 없음) ─────────────────
@st.cache_data(show_spinner=False)
def fetch_ad_data(start_date_str, end_date_str, access_token, ad_account_id, app_id, app_secret):
    """날짜 범위가 같으면 캐시된 데이터 반환, 다르면 API 새로 호출"""
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

    # 광고 크리에이티브 일괄 조회
    ad_cache = {}
    ad_cache_error = ""
    try:
        ads_cursor = account.get_ads(fields=[
            "id", "effective_status", "created_time",
            "creative{thumbnail_url,image_url,video_id}",
        ], params={"limit": 200})
        for ad_item in ads_cursor:
            d = dict(ad_item)
            ad_cache[d.get("id", "")] = d
    except Exception as e:
        ad_cache_error = str(e)

    debug_info = {
        "count": len(ad_cache),
        "error": ad_cache_error,
        "sample": dict(list(ad_cache.values())[0]) if ad_cache else {},
    }

    rows = []
    for insight in insights:
        data = dict(insight)
        spend = float(data.get("spend", 0))
        ctr = float(data.get("ctr", 0))
        cpc = float(data.get("cpc", 0))
        impressions = int(data.get("impressions", 0))
        clicks = int(data.get("clicks", 0))
        ad_id = data.get("ad_id", "")
        purchases = 0
        purchase_value = 0.0
        for action in data.get("actions", []):
            if action["action_type"] == "offsite_conversion.fb_pixel_purchase":
                purchases += int(float(action["value"]))
        for action in data.get("action_values", []):
            if action["action_type"] == "offsite_conversion.fb_pixel_purchase":
                purchase_value += float(action["value"])
        roas = round(purchase_value / spend, 2) if spend > 0 else 0

        thumbnail_url = ""
        is_video = False
        status = "알 수 없음"
        start_time = ""

        ad_info = ad_cache.get(ad_id, {})
        if ad_info:
            status = ad_info.get("effective_status", "알 수 없음")
            start_time = str(ad_info.get("created_time", ""))[:10]
            creative = ad_info.get("creative", {})
            video_id = creative.get("video_id", "")
            if video_id:
                is_video = True
                thumbnail_url = creative.get("thumbnail_url", "")
            else:
                thumbnail_url = (
                    creative.get("image_url") or
                    creative.get("thumbnail_url", "")
                )

        rows.append({
            "썸네일": thumbnail_url,
            "영상여부": is_video,
            "광고명": data.get("ad_name", ""),
            "광고세트": data.get("adset_name", ""),
            "상태": status,
            "시작일": start_time,
            "비용": spend,
            "구매전환": purchases,
            "구매전환금액": purchase_value,
            "ROAS": roas,
            "CTR(%)": round(ctr, 2),
            "CPC": round(cpc, 2),
            "노출수": impressions,
            "클릭수": clicks,
            "CVR(%)": round(purchases / clicks * 100, 2) if clicks > 0 else 0,
            "구매당비용": round(spend / purchases, 0) if purchases > 0 else 999999999,
        })

    return rows, debug_info

# ── 데이터 fetch ──────────────────────────────────────────────
if fetch_btn:
    if force_refresh:
        fetch_ad_data.clear()  # 캐시 초기화 → API 강제 재호출
    with st.spinner("Meta API에서 데이터 가져오는 중..."):
        try:
            rows, debug_info = fetch_ad_data(
                str(start_date), str(end_date),
                ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET
            )
            st.session_state.df = pd.DataFrame(rows)
            st.session_state.ad_cache_debug = debug_info
            cache_msg = " (새로고침)" if force_refresh else " (캐시 사용 가능)"
            st.success(f"✅  총 {len(rows)}개 소재 로드 완료{cache_msg}")
        except Exception as e:
            st.error(f"오류 발생: {e}")

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

    # ── 정렬 ──
    st.markdown('<p class="section-title">소재별 성과</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, _ = st.columns([1.4, 1.2, 1.2, 1.5, 3])
    with c1:
        if st.button("💰 전환금액 높은순"): st.session_state.sort_by = "구매전환금액"
    with c2:
        if st.button("📈 ROAS 높은순"):     st.session_state.sort_by = "ROAS"
    with c3:
        if st.button("🎯 CVR 높은순"):      st.session_state.sort_by = "CVR(%)"
    with c4:
        if st.button("💸 구매당비용 낮은순"): st.session_state.sort_by = "구매당비용_asc"

    sort_label_map = {
        "구매전환금액":   "전환금액 높은순",
        "ROAS":          "ROAS 높은순",
        "CVR(%)":        "CVR 높은순",
        "구매당비용_asc": "구매당비용 낮은순",
    }
    st.caption(f"정렬 기준 : {sort_label_map.get(st.session_state.sort_by, '')}")

    ascending = st.session_state.sort_by == "구매당비용_asc"
    sort_col  = "구매당비용" if st.session_state.sort_by == "구매당비용_asc" else st.session_state.sort_by
    df_sorted = df.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    # ── 헬퍼 ──
    def roas_color_class(r):
        if r >= 3:   return "kv-green"
        elif r >= 1: return "kv-amber"
        return "kv-red"

    def thumb_html(row):
        """그리드 카드용 썸네일 HTML — (height_px, inner_html) 튜플 반환"""
        ad_name = row["광고명"]
        yt_id = get_youtube_id(ad_name)

        THUMB_H = 220  # 모든 카드 썸네일 높이 통일

        if yt_id:
            # YouTube: 가로형 썸네일 → 블러 배경 + cover로 꽉 채움
            thumb    = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            fallback = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
            yt_url   = f"https://youtube.com/shorts/{yt_id}"
            inner = f'''<a href="{yt_url}" target="_blank" style="display:block;height:100%;">
  <img src="{thumb}" onerror="this.src='{fallback}'"
       style="width:100%;height:100%;object-fit:cover;display:block;" />
  <span class="yt-badge">▶ YouTube</span>
</a>'''
            return THUMB_H, inner

        url = row["썸네일"]
        if url:
            # 이미지형: 블러 배경 + 원본 contain → 세로 이미지 전체 표시
            inner = f'''
<div style="position:absolute;inset:-20px;
            background-image:url('{url}');
            background-size:cover;background-position:center;
            filter:blur(20px);opacity:0.5;transform:scale(1.1);"></div>
<img src="{url}"
     style="position:relative;z-index:1;
            width:100%;height:100%;
            object-fit:contain;display:block;" />'''
            return THUMB_H, inner

        label = "🎬 영상 소재" if row["영상여부"] else "이미지 없음"
        return THUMB_H, f'<div class="thumb-no-img">{label}</div>'

    def build_kpi_html(row, sort_by, roas_pct, rc, spend_per):
        """정렬 기준에 따라 KPI 박스 3개를 동적으로 구성"""
        all_kpis = {
            "전환금액":  ("전환금액",  f"{row['구매전환금액']:,.0f}원", ""),
            "ROAS":      ("ROAS",      roas_pct,                        rc),
            "비용":      ("비용",      f"{row['비용']:,.0f}원",          ""),
            "CVR":       ("CVR",       f"{row['CVR(%)']}%",             ""),
            "구매당비용": ("구매당비용", spend_per,                       ""),
        }
        # 정렬 기준별 순서: 첫 번째가 핵심 지표
        order_map = {
            "구매전환금액":   ["전환금액", "ROAS", "비용"],
            "ROAS":          ["ROAS",     "전환금액", "비용"],
            "CVR(%)":        ["CVR",      "ROAS", "전환금액"],
            "구매당비용_asc": ["구매당비용", "ROAS", "전환금액"],
        }
        keys = order_map.get(sort_by, ["ROAS", "전환금액", "비용"])
        html = '<div class="kpi-row">'
        for idx, key in enumerate(keys):
            label, value, cls = all_kpis[key]
            if idx == 0:
                html += f'<div class="kpi-box kpi-box-active"><div class="kpi-lbl-active">{label}</div><div class="kpi-val {cls}">{value}</div></div>'
            else:
                html += f'<div class="kpi-box"><div class="kpi-lbl">{label}</div><div class="kpi-val {cls}">{value}</div></div>'
        html += '</div>'
        return html

    def render_grid(df_render, show_rank=False, sort_by="구매전환금액"):
        cards = ""
        for i, (_, row) in enumerate(df_render.iterrows()):
            roas_pct = f"{row['ROAS']*100:.0f}%"
            rc = roas_color_class(row["ROAS"])
            spend_per = "∞" if row["구매당비용"] == 999999999 else f"{row['구매당비용']:,.0f}원"

            sp_cls  = "sp-active" if row["상태"] == "ACTIVE" else "sp-paused"
            sp_text = "운영중" if row["상태"] == "ACTIVE" else ("정지" if row["상태"] == "PAUSED" else row["상태"])

            rank_badge = f'<span style="position:absolute;top:9px;right:9px;background:rgba(0,0,0,0.55);color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:100px;">#{i+1}</span>' if show_rank else ""

            date_txt = f'📅 {row["시작일"]}' if row["시작일"] else ""

            thumb_h, thumb_inner = thumb_html(row)
            kpi_html = build_kpi_html(row, sort_by, roas_pct, rc, spend_per)

            cards += f"""
<div class="ad-card-g">
  <div class="thumb-area" style="height:{thumb_h}px;">
    {thumb_inner}
    <span class="status-pill {sp_cls}">{sp_text}</span>
    {rank_badge}
  </div>
  <div class="card-body">
    <div class="card-ad-name" title="{row['광고명']}">{row['광고명']}</div>
    <div class="card-adset" title="{row['광고세트']}">{row['광고세트']}</div>
    {f'<div class="card-date">{date_txt}</div>' if date_txt else ''}
    {kpi_html}
    <div class="card-tags">
      <span class="tag">구매 {row['구매전환']}건</span>
      <span class="tag">CVR {row['CVR(%)']}%</span>
      <span class="tag">CTR {row['CTR(%)']}%</span>
      <span class="tag">구매당 {spend_per}</span>
      <span class="tag">노출 {row['노출수']:,}</span>
    </div>
  </div>
</div>"""

        st.markdown(f'<div class="ad-grid">{cards}</div>', unsafe_allow_html=True)

    render_grid(df_sorted, sort_by=st.session_state.sort_by)

    # ── TOP 5 ──
    st.markdown("<div style='margin-top:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">🏆 베스트 소재 TOP 5 <span style="font-size:0.75rem;color:#a1a1aa;font-weight:400;">ROAS 기준</span></p>', unsafe_allow_html=True)
    render_grid(df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True), show_rank=True, sort_by="ROAS")

    # ── 디버그 / CSV ──
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("🔍 디버그"):
        debug_df = df[["광고명", "썸네일", "영상여부", "상태"]].head(5)
        st.dataframe(debug_df)
        if "ad_cache_debug" in st.session_state:
            dbg = st.session_state.ad_cache_debug
            st.write(f"캐시된 광고 수: {dbg['count']}개")
            if dbg["error"]:
                st.error(f"캐시 오류: {dbg['error']}")
            if dbg["sample"]:
                st.json(dbg["sample"])

    csv = df.drop(columns=["썸네일", "영상여부"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "ad_performance.csv", "text/csv")
