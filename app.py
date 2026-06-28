import streamlit as st
import plotly.graph_objects as go
from src.data_loader import fetch_and_clean_data
from src.analytics import compute_funnel_metrics

# 1. Platform Canvas Config
st.set_page_config(page_title="FunnelFlux Analytics", layout="wide")

# Adaptive UI overrides for crisp dark/light mode compatibility
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; }
    .report-card { 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        margin-bottom: 15px;
        background-color: rgba(128, 128, 128, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Application Header
st.write("### FunnelFlux Platform | Optimization and Segment Drift Engine")
st.caption("Production Instance - Connected to Live Event Log Matrix")
st.markdown("---")

# 2. Data Pull
df_events = fetch_and_clean_data()

# 3. Sidebar Filter Logic
st.sidebar.markdown("### Cohort Filtering Controls")
selected_device = st.sidebar.multiselect("Device Viewport", options=list(df_events['device'].unique()), default=list(df_events['device'].unique()))
selected_source = st.sidebar.multiselect("Acquisition Source", options=list(df_events['traffic_source'].unique()), default=list(df_events['traffic_source'].unique()))
selected_location = st.sidebar.multiselect("Regional Matrix", options=list(df_events['location'].unique()), default=list(df_events['location'].unique()))

# Split-Testing Configuration
st.sidebar.markdown("---")
st.sidebar.markdown("### Split-Testing Engine")
enable_split = st.sidebar.checkbox("Enable Segment A/B Comparison", value=False)

split_variable = None
cohort_a_val = None
cohort_b_val = None

if enable_split:
    split_variable = st.sidebar.selectbox("Split Matrix By", options=['device', 'traffic_source', 'location'])
    unique_vals = list(df_events[split_variable].unique())
    if len(unique_vals) >= 2:
        cohort_a_val = st.sidebar.selectbox("Cohort A Target", options=unique_vals, index=0)
        cohort_b_val = st.sidebar.selectbox("Cohort B Target", options=unique_vals, index=1)

# Helper processing engine
def isolate_df(device_f, source_f, loc_f):
    return df_events[
        (df_events['device'].isin(device_f)) &
        (df_events['traffic_source'].isin(source_f)) &
        (df_events['location'].isin(loc_f))
    ]

# High-contrast professional chart color definitions
single_funnel_colors = ["#1E3A8A", "#0D9488", "#D97706", "#DC2626"] 
cohort_a_colors = ["#334155", "#475569", "#64748B", "#94A3B8"]     
cohort_b_colors = ["#1D4ED8", "#3B82F6", "#60A5FA", "#93C5FD"]     

# 4. Interface Rendering Pipeline
if not enable_split:
    filtered_df = isolate_df(selected_device, selected_source, selected_location)
    metrics = compute_funnel_metrics(filtered_df)
    
    if not metrics.empty:
        c1, c2, c3 = st.columns(3)
        total_s = metrics['Unique_Users'].iloc[0]
        total_p = metrics['Unique_Users'].iloc[-1] if len(metrics) >= 2 else 0
        cr_macro = (total_p / total_s * 100) if total_s > 0 else 0
        
        c1.metric("Gross Logged Sessions", f"{total_s:,}")
        c2.metric("Attributed Sales Orders", f"{total_p:,}")
        c3.metric("Macro Pipeline CR", f"{cr_macro:.2f}%")
        
        st.markdown("---")
        
        l_col, r_col = st.columns([5, 3])
        with l_col:
            st.markdown("#### User Conversion Flow Analysis")
            fig = go.Figure(go.Funnel(
                x=metrics['Unique_Users'], y=metrics['Stage'],
                textinfo="value+percent initial",
                marker=dict(color=single_funnel_colors),
                connector=dict(fillcolor="rgba(128,128,128,0.1)")
            ))
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with r_col:
            st.markdown("#### Core Operational Matrix")
            st.dataframe(metrics, hide_index=True, use_container_width=True)

else:
    st.markdown("#### Comparative Segment Performance Review")
    
    base_filtered = isolate_df(selected_device, selected_source, selected_location)
    df_a = base_filtered[base_filtered[split_variable] == cohort_a_val]
    df_b = base_filtered[base_filtered[split_variable] == cohort_b_val]
    
    metrics_a = compute_funnel_metrics(df_a)
    metrics_b = compute_funnel_metrics(df_b)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"<div class='report-card'><b>Cohort A: {cohort_a_val}</b></div>", unsafe_allow_html=True)
        if not metrics_a.empty:
            cr_a = (metrics_a['Unique_Users'].iloc[-1] / metrics_a['Unique_Users'].iloc[0] * 100) if len(metrics_a) >= 2 else 0
            st.metric("Conversion Rate", f"{cr_a:.2f}%")
            fig_a = go.Figure(go.Funnel(
                x=metrics_a['Unique_Users'], y=metrics_a['Stage'], 
                textinfo="value+percent initial", 
                marker=dict(color=cohort_a_colors)
            ))
            fig_a.update_layout(margin=dict(l=5, r=5, t=5, b=5), height=250, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})
            
    with col_b:
        st.markdown(f"<div class='report-card'><b>Cohort B: {cohort_b_val}</b></div>", unsafe_allow_html=True)
        if not metrics_b.empty:
            cr_b = (metrics_b['Unique_Users'].iloc[-1] / metrics_b['Unique_Users'].iloc[0] * 100) if len(metrics_b) >= 2 else 0
            st.metric("Conversion Rate", f"{cr_b:.2f}%", delta=f"{cr_b - cr_a:.2f}% relative to A")
            fig_b = go.Figure(go.Funnel(
                x=metrics_b['Unique_Users'], y=metrics_b['Stage'], 
                textinfo="value+percent initial", 
                marker=dict(color=cohort_b_colors)
            ))
            fig_b.update_layout(margin=dict(l=5, r=5, t=5, b=5), height=250, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_b, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# 5. Financial Risk Analysis Simulator
st.markdown("#### Financial Pipeline Risk Simulator")
st.caption("Calculate potential upside revenue saved by patching leakages at specific stages of the user journey.")

sim_col1, sim_col2 = st.columns([1, 2])
with sim_col1:
    avg_contract_value = st.number_input("Average Order Value ($)", min_value=1, value=75, step=5)
    target_recovery = st.slider("Target Bottleneck Optimization (%)", min_value=1, max_value=50, value=15)

with sim_col2:
    active_metrics = metrics_a if enable_split else (metrics if 'metrics' in locals() and not metrics.empty else None)
    
    if active_metrics is not None and not active_metrics.empty and len(active_metrics) >= 2:
        dropped_users = active_metrics['Unique_Users'].iloc[0] - active_metrics['Unique_Users'].iloc[-1]
        potential_salvage = int(dropped_users * (target_recovery / 100))
        projected_revenue = potential_salvage * avg_contract_value
        
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        st.info(f"Growth Impact Prediction: Recovering just {target_recovery}% of your total dropped-off traffic ({potential_salvage} users) would inject an estimated ${projected_revenue:,} back into the revenue pipeline.")
    else:
        st.text("Adjust filtering selections to compute simulation models.")