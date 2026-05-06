import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
import pandas as pd
from datetime import date, timedelta

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
}

.badge-active { background:#e8f5e9; color:#2e7d32; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.badge-paused { background:#fafafa; color:#9e9e9e; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.roas-high { color: #2e7d32; font-weight: 700; }
.roas-mid  { color: #e65100; font-weight: 700; }
.roas-low  { color: #c62828; font-weight: 700; }

.media-wrap {
    position: relative;
    width: 240px;
    height: 135px;
    border-radius: 10px;
    overflow: hidden;
    flex-shrink: 0;
    background: #f5f5f5;
}
.media-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.25s ease;
    cursor: zoom-in;
}
.media-wrap img:hover { transform: scale(1.05); }
.media-wrap video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
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
    st.session_state.sort_by = "ROAS"

if st.button("📊 데이터 불러오기"):
    with st.spinner("Meta API에서 데이터 가져오는 중..."):
        try:
            FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)
            account = AdAccount(AD_ACCOUNT_ID)
            fields = [
                AdsInsights.Field.ad_id,
                AdsInsights.Field.ad_name,
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
                PURCHASE_TYPES = {"purchase", "offsite_conversion.fb_pixel_purchase"}
                for action in data.get("actions", []):
                    if action["action_type"] in PURCHASE_TYPES:
                        purchases += int(float(action["value"]))
                for action in data.get("action_values", []):
                    if action["action_type"] in PURCHASE_TYPES:
                        purchase_value += float(action["value"])
                roas = round(purchase_value / spend, 2) if spend > 0 else 0

                thumbnail_url = ""
                video_url = ""
                is_video = False
                status = "알 수 없음"
                start_time = ""
                stop_time = ""

                try:
                    ad = Ad(ad_id)
                    ad_data = ad.api_get(fields=[
                        "effective_status",
                        "start_time",
                        "stop_time",
                        "creative",
                    ])
                    status = ad_data.get("effective_status", "알 수 없음")
                    start_time = str(ad_data.get("start_time", ""))[:10]
                    stop_time = str(ad_data.get("stop_time", ""))[:10]

                    creative_ref = ad_data.get("creative", {})
                    creative_id = creative_ref.get("id", "")

                    if creative_id:
                        creative_obj = AdCreative(creative_id)
                        creative_data = creative_obj.api_get(fields=[
                            "thumbnail_url",
                            "image_url",
                            "object_story_spec",
                            "video_id",
                        ])

                        spec = creative_data.get("object_story_spec", {})
                        video_data = spec.get("video_data", {})
                        link_data = spec.get("link_data", {})

                        if video_data:
                            is_video = True
                            thumbnail_url = (
                                video_data.get("image_url", "") or
                                creative_data.get("thumbnail_url", "")
                            )
                            video_id = video_data.get("video_id") or creative_data.get("video_id")
                            if video_id:
                                try:
                                    vid = AdVideo(video_id)
                                    vid_data = vid.api_get(fields=["source"])
                                    video_url = vid_data.get("source", "")
                                except Exception:
                                    pass
                        else:
                            thumbnail_url = (
                                link_data.get("picture") or
                                creative_data.get("image_url") or
                                creative_data.get("thumbnail_url", "")
                            )
                except Exception:
                    pass

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
        if st.button("ROAS 높은순"): st.session_state.sort_by = "ROAS"
    with c2:
        if st.button("구매전환 높은순"): st.session_state.sort_by = "구매전환"
    with c3:
        if st.button("CPC 낮은순"): st.session_state.sort_by = "CPC_asc"
    with c4:
        if st.button("CTR 높은순"): st.session_state.sort_by = "CTR(%)"

    st.caption(f"현재 정렬: **{st.session_state.sort_by.replace('_asc', '')}**")
    ascending = st.session_state.sort_by == "CPC_asc"
    sort_col = "CPC" if st.session_state.sort_by == "CPC_asc" else st.session_state.sort_by
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
        if row["영상여부"] and row["영상URL"]:
            thumb = row["썸네일"]
            src = row["영상URL"]
            return f'''<div class="media-wrap">
  <video poster="{thumb}" muted loop preload="none"
    onmouseover="this.play()" onmouseout="this.pause();this.currentTime=0;">
    <source src="{src}">
  </video>
</div>'''
        elif row["썸네일"]:
            img_url = row["썸네일"]
            return f'<div class="media-wrap"><img src="{img_url}" loading="lazy" /></div>'
        return '<div class="media-wrap" style="display:flex;align-items:center;justify-content:center;color:#ccc;font-size:0.8rem;">No Image</div>'

    def render_ads(df_render):
        for _, row in df_render.iterrows():
            date_range = ""
            if row["시작일"]:
                date_range = row["시작일"]
                date_range += f" ~ {row['종료일']}" if row["종료일"] else " ~ 진행중"

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
        📅 {date_range if date_range else '날짜 정보 없음'} &nbsp;|&nbsp; {row['광고세트']}
      </div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
        <div><div style="color:#888;font-size:0.75rem;">비용</div><div style="font-weight:600;">{row['비용']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">구매전환</div><div style="font-weight:600;">{row['구매전환']}건</div></div>
        <div><div style="color:#888;font-size:0.75rem;">전환금액</div><div style="font-weight:600;">{row['구매전환금액']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">ROAS</div><div class="{rc}">{roas_pct}</div></div>
        <div><div style="color:#888;font-size:0.75rem;">CTR</div><div style="font-weight:600;">{row['CTR(%)']}%</div></div>
        <div><div style="color:#888;font-size:0.75rem;">CPC</div><div style="font-weight:600;">{row['CPC']:,.0f}원</div></div>
        <div><div style="color:#888;font-size:0.75rem;">노출수</div><div style="font-weight:600;">{row['노출수']:,}</div></div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    render_ads(df_sorted)

    st.markdown("---")
    st.subheader("🏆 베스트 소재 TOP 5 (ROAS 기준)")
    render_ads(df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True))

    csv = df.drop(columns=["썸네일", "영상URL", "영상여부"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "ad_performance.csv", "text/csv")
