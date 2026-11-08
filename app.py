"""
Operation Shield — 電商營運利潤止血與退貨風控中心
Streamlit Cloud 輕量雲端部署版 (極速 0.2 秒啟動，記憶體 < 60MB)
數據來源：預聚合之 data/ 輕量維度表 (1.6MB，取代 90MB 原始檔)
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------------------------------------------------------
# 1. 頁面配置 (Page Configuration)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Operation Shield — 電商營運利潤止血與退貨風控中心",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #475569;
    }
    .alert-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pill-red { background-color: #fee2e2; color: #991b1b; }
    .pill-green { background-color: #dcfce7; color: #166534; }
    .pill-blue { background-color: #dbeafe; color: #1e40af; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path(__file__).resolve().parent / "data"

# -----------------------------------------------------------------------------
# 2. 輕量數據加載 (Lightweight Data Loading)
# -----------------------------------------------------------------------------
@st.cache_data
def load_cloud_data():
    daily_cube = pd.read_csv(DATA_DIR / "daily_cube.csv", encoding="utf-8-sig")
    daily_cube["Date"] = pd.to_datetime(daily_cube["Date"]).dt.date
    
    sku_df = pd.read_csv(DATA_DIR / "sku_profiles.csv", encoding="utf-8-sig")
    cust_df = pd.read_csv(DATA_DIR / "customer_profiles.csv", encoding="utf-8-sig")
    cust_df["CustomerID"] = cust_df["CustomerID"].astype(str)
    
    country_df = pd.read_csv(DATA_DIR / "country_summary.csv", encoding="utf-8-sig")
    mat_df = pd.read_csv(DATA_DIR / "material_summary.csv", encoding="utf-8-sig")
    
    return daily_cube, sku_df, cust_df, country_df, mat_df


# -----------------------------------------------------------------------------
# 3. 視圖與圖表組件
# -----------------------------------------------------------------------------
def render_kpi_cards(total_sales, total_returns, parasite_loss, star_net_sales, star_return_rate):
    value_return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0.0
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="kpi-title">⭐ 北極星指標：全站金額退貨率</div>
            <div class="kpi-value" style="color: {'#dc2626' if value_return_rate > 4.5 else '#16a34a'};">
                {value_return_rate:.2f}%
            </div>
            <div class="kpi-sub">
                <span class="alert-pill pill-red">警戒：現況 7.14%</span> 目標 ≤ 4.50%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="kpi-title">📉 累積退貨損失金額</div>
            <div class="kpi-value" style="color: #1e293b;">
                £{total_returns:,.2f}
            </div>
            <div class="kpi-sub">
                佔總出貨 (£{total_sales:,.0f}) 之 <b>{value_return_rate:.2f}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        pct_parasite = (parasite_loss / total_returns * 100) if total_returns > 0 else 0.0
        st.markdown(f"""
        <div class="metric-card">
            <div class="kpi-title">🚨 惡意奧客吞噬損失</div>
            <div class="kpi-value" style="color: #dc2626;">
                £{parasite_loss:,.2f}
            </div>
            <div class="kpi-sub">
                <span class="alert-pill pill-red">{pct_parasite:.1f}% 損失</span> 僅 56 位倒貼奧客
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="kpi-title">💎 核心爆品 22423 淨營收</div>
            <div class="kpi-value" style="color: #2563eb;">
                £{star_net_sales:,.2f}
            </div>
            <div class="kpi-sub">
                <span class="alert-pill pill-green">退貨率 {star_return_rate:.2f}%</span> 全站第一金雞母
            </div>
        </div>
        """, unsafe_allow_html=True)


def plot_pareto_chart(sku_df, exclude_non_goods=True, top_n=20):
    plot_df = sku_df[~sku_df["IsNonGoods"]].copy() if exclude_non_goods else sku_df.copy()
    top_sku = plot_df.head(top_n).copy()
    top_sku["ShortDesc"] = top_sku["Description"].fillna("未知商品").str.slice(0, 16)
    top_sku["X_Label"] = top_sku["StockCode"] + " " + top_sku["ShortDesc"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=top_sku["X_Label"],
            y=top_sku["TotalReturnLoss"],
            name="退貨損失金額 (£)",
            marker_color="#ef4444",
            customdata=top_sku["Description"].fillna(""),
            hovertemplate="<b>%{x}</b><br>完整品名: %{customdata}<br>退貨損失: <b>£%{y:,.2f}</b><extra></extra>"
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=top_sku["X_Label"],
            y=top_sku["CumPct"],
            name="累計損失佔比 (%)",
            mode="lines+markers",
            line=dict(color="#2563eb", width=2.5),
            marker=dict(size=6),
            hovertemplate="累計損失佔比: <b>%{y:.1f}%</b><extra></extra>"
        ),
        secondary_y=True
    )
    fig.add_trace(
        go.Scatter(
            x=top_sku["X_Label"],
            y=[80.0] * len(top_sku),
            name="80% 損失警戒線",
            mode="lines",
            line=dict(color="#d97706", width=2, dash="dash"),
            hoverinfo="skip"
        ),
        secondary_y=True
    )
    fig.update_layout(
        title=dict(text=f"<b>商品端帕累托雙軸分析 (Top {top_n} 毒瘤商品)</b>", y=0.98, x=0.02, xanchor="left", font=dict(size=15)),
        margin=dict(l=45, r=45, t=50, b=100),
        legend=dict(orientation="h", yanchor="top", y=-0.32, xanchor="center", x=0.5, font=dict(size=11)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        hovermode="x unified",
        height=470
    )
    fig.update_yaxes(title_text="退貨損失金額 (£)", secondary_y=False, title_font=dict(size=11))
    fig.update_yaxes(title_text="累計損失佔比 (%)", range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix="%", secondary_y=True, title_font=dict(size=11))
    return fig


def plot_rfmr_scatter(cust_df):
    plot_data = cust_df[
        (cust_df["NetSales"] >= -15000) & (cust_df["NetSales"] <= 75000) & (cust_df["TotalReturnLoss"] > 0)
    ].copy()

    color_map = {
        "惡意刷退奧客 (Parasites)": "#dc2626",
        "B2B批發大戶 (Whales)": "#16a34a",
        "核心VIP金雞母 (Champions)": "#2563eb",
        "一般零售買家 (General)": "#94a3b8"
    }

    fig = px.scatter(
        plot_data,
        x="NetSales",
        y="ReturnRate",
        size="TotalReturnLoss",
        color="Segment",
        color_discrete_map=color_map,
        hover_name="CustomerID",
        hover_data={
            "TotalSales": ":,.2f",
            "TotalReturnLoss": ":,.2f",
            "NetSales": ":,.2f",
            "ReturnRate": ":.1f%",
            "Country": True,
            "Segment": False
        },
        labels={
            "NetSales": "客戶累積淨銷售額 (Net Sales £)",
            "ReturnRate": "金額退貨率 (%)",
            "TotalReturnLoss": "退貨損失 (£)"
        },
        height=470
    )
    fig.add_vline(x=0, line_dash="solid", line_color="#cbd5e1", line_width=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#dc2626", annotation_text="50% 極高退貨警戒", annotation_position="bottom right")
    fig.add_vline(x=3000, line_dash="dot", line_color="#16a34a", annotation_text="£3,000 大戶門檻", annotation_position="top right")

    fig.update_layout(
        title=dict(text="<b>客戶端 RFM-R 客戶價值與退貨風險矩陣</b>", y=0.98, x=0.02, xanchor="left", font=dict(size=15)),
        margin=dict(l=45, r=45, t=50, b=100),
        legend=dict(orientation="h", yanchor="top", y=-0.32, xanchor="center", x=0.5, title_text="", font=dict(size=11)),
        xaxis=dict(title_font=dict(size=11)),
        yaxis=dict(title_font=dict(size=11), range=[-5, 115])
    )
    return fig


def plot_country_returns(country_df):
    top_c = country_df[country_df["OrderCount"] >= 30].sort_values("ReturnRate", ascending=False).head(10).copy()
    colors = ["#dc2626" if r > 15 else "#f97316" if r > 10 else "#3b82f6" for r in top_c["ReturnRate"]]

    fig = go.Figure(go.Bar(
        x=top_c["ReturnRate"],
        y=top_c["Country"],
        orientation="h",
        marker_color=colors,
        text=top_c["ReturnRate"].apply(lambda x: f"{x:.1f}%"),
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>退貨率: %{x:.2f}%<br>總損失: £" + top_c["TotalReturnLoss"].apply(lambda x: f"{x:,.0f}") + "<extra></extra>"
    ))
    fig.add_vline(x=7.27, line_dash="dash", line_color="#64748b", annotation_text="英國本土 7.3%")
    fig.update_layout(
        title=dict(text="<b>跨境物流航線金額退貨率排行 (Top 10)</b>", font=dict(size=14)),
        margin=dict(l=30, r=30, t=40, b=30),
        xaxis_title="金額退貨率 (%)",
        yaxis=dict(autorange="reversed"),
        height=360
    )
    return fig


def plot_material_benchmark(mat_df):
    fig = go.Figure(go.Bar(
        x=mat_df["Category"],
        y=mat_df["UnitReturnRate"],
        marker_color=mat_df["Color"],
        text=mat_df["UnitReturnRate"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>件數退貨率: %{y:.2f}%<extra></extra>"
    ))
    fig.add_hline(y=4.26, line_dash="dash", line_color="#64748b", annotation_text="大盤基準線 4.26%")
    fig.update_layout(
        title=dict(text="<b>易碎陶瓷材質 vs 全站件數退貨率對比</b>", font=dict(size=14)),
        margin=dict(l=30, r=30, t=40, b=30),
        yaxis_title="件數退貨率 (%)",
        yaxis=dict(range=[0, 32]),
        height=360
    )
    return fig


# -----------------------------------------------------------------------------
# 4. 主程式流程 (Main Execution)
# -----------------------------------------------------------------------------
def main():
    st.title("🛡️ Operation Shield 電商營運利潤止血與退貨風控監控中心")
    st.caption("高階管理層決策儀表板 ｜ 即時掌握退貨漏斗、毒瘤商品、攔截惡意奧客與保障 B2B 金雞母 (Streamlit Cloud 極速版)")

    daily_cube, sku_df, cust_df, country_df, mat_df = load_cloud_data()

    # 側邊欄篩選器
    st.sidebar.header("🔍 全局監控篩選器")

    exclude_non_goods = st.sidebar.checkbox(
        "🚫 排除非商品費用條目 (M/手續費/郵資/折扣)",
        value=True,
        help="勾選後將剔除 Manual、Amazon Fee、Bank Charges、Postage 等記帳代碼，精確聚焦實體零售商品。"
    )

    min_date = daily_cube["Date"].min()
    max_date = daily_cube["Date"].max()
    date_range = st.sidebar.date_input("交易日期區間", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    all_countries = sorted(daily_cube["Country"].unique().tolist())
    selected_countries = st.sidebar.multiselect("國家/跨國航線", options=all_countries, default=[])

    segment_options = ["全部客群"] + sorted(cust_df["Segment"].unique().tolist())
    selected_segment = st.sidebar.selectbox("客戶價值分群 (RFM-R)", options=segment_options)

    material_filter = st.sidebar.radio("商品材質屬性", ["全部商品", "僅看陶瓷/瓷器 (易碎品)", "非陶瓷商品"])

    st.sidebar.divider()
    st.sidebar.markdown("""
    **💡 商業決策核心指引**：
    - **毒瘤商品**：`23843`（紙藝小鳥，100%全退）、`23166`（陶瓷罐，95%退貨）
    - **惡意奧客**：56 位刷退買家吞噬 £53 萬（淨利潤為負數）
    - **B2B 大戶**：54 位批發商貢獻 £78.2 萬純利，切勿誤殺！
    """)

    # 動態篩選 Cube
    cube_filtered = daily_cube.copy()
    if exclude_non_goods:
        cube_filtered = cube_filtered[~cube_filtered["IsNonGoods"]]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range
        cube_filtered = cube_filtered[(cube_filtered["Date"] >= start_d) & (cube_filtered["Date"] <= end_d)]

    if selected_countries:
        cube_filtered = cube_filtered[cube_filtered["Country"].isin(selected_countries)]

    if material_filter == "僅看陶瓷/瓷器 (易碎品)":
        cube_filtered = cube_filtered[cube_filtered["IsCeramic"]]
    elif material_filter == "非陶瓷商品":
        cube_filtered = cube_filtered[~cube_filtered["IsCeramic"]]

    if selected_segment != "全部客群":
        cube_filtered = cube_filtered[cube_filtered["Segment"] == selected_segment]

    # 計算當前動態 KPI
    curr_total_sales = cube_filtered["SalesAmount"].sum()
    curr_total_returns = cube_filtered["ReturnAmount"].sum()
    curr_parasite_loss = cube_filtered[cube_filtered["Segment"] == "惡意刷退奧客 (Parasites)"]["ReturnAmount"].sum()

    # 明星商品 22423 固定指標
    sku_22423 = sku_df[sku_df["StockCode"] == "22423"]
    star_net = sku_22423["NetSales"].iloc[0] if len(sku_22423) > 0 else 314045.02
    star_rate = sku_22423["ValueReturnRate"].iloc[0] if len(sku_22423) > 0 else 5.00

    # 1. 核心指標卡片
    render_kpi_cards(curr_total_sales, curr_total_returns, curr_parasite_loss, star_net, star_rate)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 2. 主分析雙欄
    col_left, col_right = st.columns([1, 1])
    with col_left:
        fig_pareto = plot_pareto_chart(sku_df, exclude_non_goods=exclude_non_goods, top_n=20)
        st.plotly_chart(fig_pareto, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        fig_rfmr = plot_rfmr_scatter(cust_df)
        st.plotly_chart(fig_rfmr, use_container_width=True, config={"displayModeBar": False})

    # 3. 下鑽分析雙欄
    col_geo, col_mat = st.columns([1, 1])
    with col_geo:
        fig_geo = plot_country_returns(country_df)
        st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})

    with col_mat:
        fig_mat = plot_material_benchmark(mat_df)
        st.plotly_chart(fig_mat, use_container_width=True, config={"displayModeBar": False})

    # 4. 即時行動看板
    st.subheader("📋 營運止血即時行動處方看板")
    tab1, tab2, tab3 = st.tabs([
        "🛑 核心毒瘤 SKU 處置名單",
        "🚨 56 位惡意刷退奧客風控黑名單",
        "💎 54 位高價值 B2B 批發大戶白名單"
    ])

    with tab1:
        st.markdown("**行動建議**：針對吞噬 80% 損失的毒瘤商品，全面啟動品質抽檢、下架淘汰或修訂尺寸規格。")
        active_sku = sku_df[~sku_df["IsNonGoods"]].copy() if exclude_non_goods else sku_df.copy()
        toxic_sku = active_sku[active_sku["CumPct"] <= 80.5].copy()
        toxic_sku["建議處置"] = np.where(
            toxic_sku["ValueReturnRate"] >= 90.0, "🚫 立即下架 / 停售",
            np.where(toxic_sku["ValueReturnRate"] >= 30.0, "⚠️ 尺寸規格修訂 / 深度檢品", "📦 包材強化升級")
        )
        display_sku = toxic_sku[[
            "StockCode", "Description", "TotalSales", "TotalReturnLoss", "ValueReturnRate", "UnitReturnRate", "CumPct", "建議處置"
        ]].copy()
        display_sku.columns = ["商品代碼 (SKU)", "商品品名", "出貨金額 (£)", "退貨損失 (£)", "金額退貨率 (%)", "件數退貨率 (%)", "累計損失佔比 (%)", "處置處方"]
        st.dataframe(
            display_sku.style.format({
                "出貨金額 (£)": "£{:,.2f}",
                "退貨損失 (£)": "£{:,.2f}",
                "金額退貨率 (%)": "{:.2f}%",
                "件數退貨率 (%)": "{:.2f}%",
                "累計損失佔比 (%)": "{:.2f}%"
            }),
            use_container_width=True,
            height=320
        )
        st.download_button(
            label="📥 匯出毒瘤 SKU 處置清單 (CSV)",
            data=display_sku.to_csv(index=False).encode('utf-8-sig'),
            file_name="toxic_sku_action_list.csv",
            mime="text/csv"
        )

    with tab2:
        st.markdown("**行動建議**：對 56 位倒貼奧客取消「無條件免運」，並依國際電商慣例加收 15% 退貨整新費。")
        parasites = cust_df[cust_df["Segment"] == "惡意刷退奧客 (Parasites)"].sort_values("TotalReturnLoss", ascending=False).copy()
        parasites["建議管制"] = np.where(
            parasites["ReturnRate"] >= 90.0, "🚫 凍結帳戶 / 限制下單",
            "⚠️ 取消免運 / 加收 15% 退貨整新費"
        )
        display_para = parasites[[
            "CustomerID", "Country", "TotalSales", "TotalReturnLoss", "NetSales", "ReturnRate", "OrderCount", "建議管制"
        ]].copy()
        display_para.columns = ["客戶編號 (CustomerID)", "所屬國家", "總下單額 (£)", "退貨損失 (£)", "淨貢獻額 (£)", "金額退貨率 (%)", "總訂單數", "風控處置"]
        st.dataframe(
            display_para.style.format({
                "總下單額 (£)": "£{:,.2f}",
                "退貨損失 (£)": "£{:,.2f}",
                "淨貢獻額 (£)": "£{:,.2f}",
                "金額退貨率 (%)": "{:.2f}%"
            }),
            use_container_width=True,
            height=320
        )
        st.download_button(
            label="📥 匯出 56 位惡意奧客風控黑名單 (CSV)",
            data=display_para.to_csv(index=False).encode('utf-8-sig'),
            file_name="parasite_customers_blacklist.csv",
            mime="text/csv"
        )

    with tab3:
        st.markdown("**行動建議**：54 位 B2B 大戶平均淨利潤極高，退貨屬於商業週轉正當損耗，切勿實施懲罰性政策，應指派專屬客戶經理！")
        whales = cust_df[cust_df["Segment"] == "B2B批發大戶 (Whales)"].sort_values("NetSales", ascending=False).copy()
        whales["VIP服務"] = "🌟 指派 Key Account 專屬經理 / 提供整箱直運通道"
        display_whales = whales[[
            "CustomerID", "Country", "TotalSales", "TotalReturnLoss", "NetSales", "ReturnRate", "OrderCount", "VIP服務"
        ]].copy()
        display_whales.columns = ["客戶編號 (CustomerID)", "所屬國家", "總下單額 (£)", "退貨損失 (£)", "淨利潤貢獻 (£)", "金額退貨率 (%)", "總訂單數", "維護策略"]
        st.dataframe(
            display_whales.style.format({
                "總下單額 (£)": "£{:,.2f}",
                "退貨損失 (£)": "£{:,.2f}",
                "淨利潤貢獻 (£)": "£{:,.2f}",
                "金額退貨率 (%)": "{:.2f}%"
            }),
            use_container_width=True,
            height=320
        )
        st.download_button(
            label="📥 匯出 54 位 B2B 批發大戶白名單 (CSV)",
            data=display_whales.to_csv(index=False).encode('utf-8-sig'),
            file_name="b2b_whales_whitelist.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()

