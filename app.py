import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
import pandas as pd
from datetime import date, timedelta

ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
AD_ACCOUNT_ID = st.secrets["AD_ACCOUNT_ID"]
APP_ID = st.secrets["APP_ID"]
APP_SECRET = st.secrets["APP_SECRET"]

st.set_page_config(page_title="LLS AD Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
.ad-img-wrap {
    position: relative;
    display: inline-block;
    width: 150px;
    height: 150px;
    overflow: visible;
    z-index: 1;
}
.ad-img-wrap img {
    width: 150px;
    height: 150px;
    object-fit: cover;
    border-radius: 8px;
    transition: transform 0.25s ease;
    cursor: zoom-in;
    display: block;
}
.ad-img-wrap img:hover {
    transform: scale(2.5);
    z-index: 9999;
    position: relative;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("LLS AD Dashboard")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", date.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("종료일", date.today())

if "df" not in st.session_state:
    st.session_state.df = None
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "ROAS"

if st.button("데이터 불러오기"):
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
                try:
                    ad = Ad(ad_id)
                    ad_data = ad.api_get(fields=["creative{image_url,thumbnail_url,object_story_spec}"])
                    creative = ad_data.get("creative", {})
                    spec = creative.get("object_story_spec", {})
                    thumbnail_url = (
                        (spec.get("link_data") or {}).get("picture") or
                        (spec.get("video_data") or {}).get("image_url") or
                        creative.get("image_url") or
                        creative.get("thumbnail_url", "")
                    )
                except:
                    pass
                rows.append({
                    "썸네일": thumbnail_url,
                    "광고명": data.get("ad_name", ""),
                    "광고세트": data.get("adset_name", ""),
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


def render_ads(df_render):
    for _, row in df_render.iterrows():
        col_img, col_info = st.columns([1, 4])
        with col_img:
            if row["썸네일"]:
                img_url = row["썸네일"]
                st.markdown(
                    f'<div class="ad-img-wrap"><img src="{img_url}" /></div>',
                    unsafe_allow_html=True
                )
            else:
                st.write("이미지 없음")
        with col_info:
            st.markdown(f"**{row['광고명']}**")
            st.markdown(
                f"비용: **{row['비용']:,.0f}** | "
                f"구매전환: **{row['구매전환']}건** | "
                f"구매전환금액: **{row['구매전환금액']:,.0f}** | "
                f"ROAS: **{row['ROAS']}** | "
                f"CTR: **{row['CTR(%)']}%** | "
                f"CPC: **{row['CPC']:,.0f}**"
            )
            st.caption(f"광고세트: {row['광고세트']} | 노출수: {row['노출수']:,}")
        st.divider()


if st.session_state.df is not None:
    df = st.session_state.df
    st.subheader("소재별 성과")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("ROAS 높은순"):
            st.session_state.sort_by = "ROAS"
    with c2:
        if st.button("구매전환 높은순"):
            st.session_state.sort_by = "구매전환"
    with c3:
        if st.button("CPC 낮은순"):
            st.session_state.sort_by = "CPC_asc"
    with c4:
        if st.button("CTR 높은순"):
            st.session_state.sort_by = "CTR(%)"
    st.caption(f"현재 정렬: **{st.session_state.sort_by.replace('_asc', '')}**")
    ascending = st.session_state.sort_by == "CPC_asc"
    sort_col = "CPC" if st.session_state.sort_by == "CPC_asc" else st.session_state.sort_by
    df_sorted = df.sort_values(sort_col, ascending=ascending).reset_index(drop=True)
    render_ads(df_sorted)
    st.subheader("베스트 소재 TOP 5 (ROAS 기준)")
    render_ads(df.sort_values("ROAS", ascending=False).head(5).reset_index(drop=True))
    csv = df.drop(columns=["썸네일"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("CSV 다운로드", csv, "ad_performance.csv", "text/csv")