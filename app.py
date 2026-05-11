import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
import pandas as pd
from datetime import date, timedelta

# 유튜브 영상 매핑 (광고명 키워드 → 유튜브 영상 ID)
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

st.set_page_config(page_title="LLS AD Dashboard", page_icon="📊", layout="wide")

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;height:60vh;flex-direction:column;'>
            <h1 style='color:#1a1a2e;font-size:2.5rem;margin-bottom:0.5rem;'>🌿 LLS AD Dashboard</h1>
            <p style='color:#666;margin-bottom:2rem;'>광고 소재 효율 분석 대시보드</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.header-wrap {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
}
.header-title { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
.header-sub { color: #a0c4ff; font-size: 0.9rem; margin: 0.2rem 0 0 0; }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 4px solid #0f3460;
    margin-bottom: 1rem;
}
.metric-label { color: #888; font-size: 0.8rem; font-weight: 500; margin-bottom: 0.3rem; }
.metric-value { color: #1a1a2e; font-size: 1.6rem; font-weight: 700; }

.ad-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    border: 1px solid #f0f0f0;
    overflow: visible;
}

.badge-active { background:#e8f5e9; color:#2e7d32; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.badge-paused { background:#fafafa; color:#9e9e9e; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.roas-high { color: #2e7d32; font-weight: 700; }
.roas-mid  { color: #e65100; font-weight: 700; }
.roas-low  { color: #c62828; font-weight: 700; }

.media-wrap {
    position: relative;
    width: 160px;
    height: 284px;
    border-radius: 10px;
    flex-shrink: 0;
    background: #f0f0f0;
    overflow: hidden;
    z-index: 1;
}
.media-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border-radius: 10px;
    position: relative;
    z-index: 1;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-wrap">
    <p class="header-title">🌿 LLS AD Dashboard</p>
    <p class="header-sub">Meta 광고 소재 효율 분석</p>
</div>
""", unsafe_allow_html=True)

col_logout = st.columns([6, 1])[1]
with col_logout:
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", date.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("종료일", date.today())

if "df" not in st.session_state:
    st.session_state.df = None
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "구매전환금액"

if st.button("📊 데이터 불러오기"):
    with st.spinner("Meta API에서 데이터 가져오는 중..."):
        try:
            FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)
            account = AdAccount(AD_ACCOUNT_ID)
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
                "time_range": {"since": str(start_date), "until": str(end_date)},
                "level": "ad",
                "limit": 500,
            }
            insights = account.get_insights(fields=fields, params=params)

            # 광고세트 날짜 일괄 조회
            from facebook_business.adobjects.adset import AdSet
            adset_cache = {}
            try:
                adsets_cursor = account.get_ad_sets(fields=[
                    "id", "start_time", "end_time"
                ], params={"limit": 500})
                for adset_item in adsets_cursor:
                    d = dict(adset_item)
                    adset_cache[d.get("id", "")] = d
            except Exception:
                pass

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
            st.session_state.ad_cache_debug = {
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
                video_url = ""
                is_video = False
                status = "알 수 없음"
                start_time = ""
                stop_time = ""

                ad_info_pre = ad_cache.get(ad_id, {})
                if ad_info_pre:
                    start_time = str(ad_info_pre.get("created_time", ""))[:10]

                ad_info = ad_cache.get(ad_id, {})
                if ad_info:
                    status = ad_info.get("effective_status", "알 수 없음")
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
                    "영상URL": video_url,
                    "영상여부": is_video,
                    "광고명": data.get("ad_name", ""),
                    "광고세트": data.get("adset_name", ""),
                    "상태": status,
                    "시작일": start_time,
                    "종료일": stop_time,
                    "비용": spend,
                    "구매전환": purchases,
                    "구매전환금액": purchase_value,
                    "ROAS": roas,
                    "CTR(%)": round(ctr, 2),
                    "CPC": round(cpc, 2),
                    "노출수": impressions,
                    "CVR(%)": round(purchases / int(data.get("clicks", 1)) * 100, 2) if int(data.get("clicks", 0)) > 0 else 0,
                    "구매당비용": round(spend / purchases, 0) if purchases > 0 else 999999999,
                })
            st.session_state.df = pd.DataFrame(rows)
            st.success(f"총 {len(rows)}개 소재 로드 완료!")
        except Exception as e:
            st.error(f"오류 발생: {e}")

if st.session_state.df is not None:
    df = st.session_state.df

    total_spend = df["비용"].sum()
    total_purchases = df["구매전환"].sum()
    total_conv_value = df["구매전환금액"].sum()
    overall_roas = round(total_conv_value / total_spend, 2) if total_spend > 0 else 0
    overall_roas_pct = f"{overall_roas * 100:.0f}%"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">💰 총 광고 비용</div><div class="metric-value">{total_spend:,.0f}원</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🛒 총 구매전환</div><div class="metric-value">{total_purchases:,}건</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">📈 전체 ROAS</div><div class="metric-value">{overall_roas_pct}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">💵 총 전환금액</div><div class="metric-value">{total_conv_value:,.0f}원</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("소재별 성과")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("구매전환금액 높은순"): st.session_state.sort_by = "구매전환금액"
    with c2:
        if st.button("ROAS 높은순"): st.session_state.sort_by = "ROAS"
    with c3:
        if st.button("CVR 높은순"): st.session_state.sort_by = "CVR(%)"
    with c4:
        if st.button("구매당 비용 낮은순"): st.session_state.sort_by = "구매당비용_asc"

    sort_label_map = {
        "구매전환금액": "구매전환금액 높은순",
        "ROAS": "ROAS 높은순",
        "CVR(%)": "CVR 높은순",
        "구매당비용_asc": "구매당 비용 낮은순",
    }
    st.caption(f"현재 정렬: **{sort_label_map.get(st.session_state.sort_by, st.session_state.sort_by)}**")
    ascending = st.session_state.sort_by == "구매당비용_asc"
    sort_col = "구매당비용" if st.session_state.sort_by == "구매당비용_asc" else st.session_state.sort_by
    df_sorted = df.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    def roas_class(r):
        if r >= 3: return "roas-high"
        elif r >= 1: return "roas-mid"
        return "roas-low"

    def status_badge(s):
        if s == "ACTIVE": return '<span class="badge-active">● 운영중</span>'
        elif s == "PAUSED": return '<span class="badge-paused">■ 일시정지</span>'
        return f'<span class="badge-paused">{s}</span>'

    def media_html(row):
        ad_name = row["광고명"]
        yt_id = get_youtube_id(ad_name)

        if yt_id:
            thumb = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            thumb_fallback = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
            yt_url = f"https://youtube.com/shorts/{yt_id}"
            return f'''<a href="{yt_url}" target="_blank" style="display:block;text-decoration:none;">
  <div class="media-wrap" style="cursor:pointer;background:#111;">
    <img src="{thumb}" style="object-fit:cover;" onerror="this.src='{thumb_fallback}'" />
    <div style="position:absolute;bottom:6px;right:6px;background:rgba(200,0,0,0.85);color:white;font-size:0.65rem;padding:2px 7px;border-radius:4px;font-weight:700;">▶ YouTube</div>
  </div>
</a>'''

        thumb_url = row["썸네일"]
        if not thumb_url:
            label = "🎬 영상 소재" if row["영상여부"] else "No Image"
            return f'<div class="media-wrap" style="display:flex;align-items:center;justify-content:center;color:#aaa;font-size:0.8rem;background:#f5f5f5;">{label}</div>'
        return f'<div class="media-wrap"><img src="{thumb_url}" /></div>'

    def render_ads(df_render):
        for _, row in df_render.iterrows():
            date_range = row["시작일"] if row["시작일"] else ""

            rc = roas_class(row["ROAS"])
            sb = status_badge(row["상태"])
            media = media_html(row)
            roas_pct = f"{row['ROAS'] * 100:.0f}%"

            st.markdown(f"""
<div class="ad-card">
  <div style="display:flex;gap:1.2rem;align-items:flex-start;">
    {media}
    <div style="flex:1;">
      <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.4rem;">
        <span style="font-size:1rem;font-weight:700;color:#1a1a2e;">{row['광고명']}</span>
        {sb}
      </div>
      <div style="color:#888;font-size:0.8rem;margin-bottom:0.8rem;">
        📅 생성일 {date_range if date_range else '정보 없음'} &nbsp;|&nbsp; {row['광고세트']}
      </div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
        <div><div style="color:#888;font-size:0.75rem;">비용</div><div style="font-weight:600;">{row['비용']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">구매전환</div><div style="font-weight:600;">{row['구매전환']}건</div></div>
        <div><div style="color:#888;font-size:0.75rem;">전환금액</div><div style="font-weight:600;">{row['구매전환금액']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">ROAS</div><div class="{rc}">{roas_pct}</div></div>
        <div><div style="color:#888;font-size:0.75rem;">CVR</div><div style="font-weight:600;">{row['CVR(%)']}%</div></div>
        <div><div style="color:#888;font-size:0.75rem;">구매당비용</div><div style="font-weight:600;">{"∞" if row['구매당비용'] == 999999999 else f"{row['구매당비용']:,.0f}원"}</div></div>
        <div><div style="color:#888;font-size:0.75rem;">CTR</div><div style="font-weight:600;">{row['CTR(%)']}%</div></div>
        <div><div style="color:#888;font-size:0.75rem;">CPC</div><div style="font-weight:600;">{row['CPC']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">노출수</div><div style="font-weight:600;">{row['노출수']:,}</div></div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    render_ads(df_sorted)

    with st.expander("🔍 이미지 디버그"):
        debug_df = df[["광고명", "썸네일", "영상여부", "영상URL", "상태"]].head(5)
        st.dataframe(debug_df)
        if "ad_cache_debug" in st.session_state:
            dbg = st.session_state.ad_cache_debug
            st.write(f"캐시된 광고 수: {dbg['count']}개")
            if dbg["error"]:
                st.error(f"캐시 오류: {dbg['error']}")
            if dbg["sample"]:
                st.json(dbg["sample"])

    st.markdown("---")
    st.subheader("🏆 베스트 소재 TOP 5 (ROAS 기준)")
    render_ads(df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True))

    csv = df.drop(columns=["썸네일", "영상URL", "영상여부"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "ad_performance.csv", "text/csv")
