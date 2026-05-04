import pandas as pd
import scipy.stats
import streamlit as st
import plotly.graph_objects as go
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Law of Large Numbers",
    page_icon="🪙",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #0d0f1a;
        color: #e8eaf0;
    }

    .stApp {
        background: linear-gradient(135deg, #0d0f1a 0%, #111827 100%);
    }

    h1, h2, h3 {
        font-family: 'Space Mono', monospace !important;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
        font-family: 'Space Mono', monospace;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
        color: #f0f4ff;
    }
    .metric-value.green { color: #34d399; }
    .metric-value.yellow { color: #fbbf24; }
    .metric-value.red { color: #f87171; }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 40px 20px 20px;
    }
    .hero h1 {
        font-size: 2.4rem;
        background: linear-gradient(90deg, #818cf8, #38bdf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }
    .hero p {
        color: #9ca3af;
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.7;
    }

    /* Explanation box */
    .info-box {
        background: rgba(99, 102, 241, 0.08);
        border-left: 3px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 16px 0;
        color: #c7d2fe;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    /* Results table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #6366f1, #38bdf8) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #38bdf8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        width: 100%;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .stButton > button:hover {
        opacity: 0.85;
        transform: translateY(-1px);
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06); }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if 'experiment_no' not in st.session_state:
    st.session_state['experiment_no'] = 0
if 'df_results' not in st.session_state:
    st.session_state['df_results'] = pd.DataFrame(columns=['#', 'Flips', 'Final Mean', 'Distance from 0.5'])
if 'history' not in st.session_state:
    st.session_state['history'] = []  # list of (n, means_list, color)

COLORS = ['#818cf8', '#38bdf8', '#34d399', '#fbbf24', '#f472b6',
          '#a78bfa', '#22d3ee', '#4ade80', '#fb923c', '#e879f9']

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🪙 Law of Large Numbers</h1>
    <p>Watch probability converge in real time. The more you flip, the closer the mean gets to <strong style="color:#34d399">0.5</strong> — this is the Law of Large Numbers in action.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>📐 What is the Law of Large Numbers?</strong><br>
    As the number of trials increases, the average result of an experiment converges to its expected value.
    For a fair coin, the expected probability of heads is exactly <strong>0.5</strong>.
    The more flips you run, the closer the running mean gets to that theoretical value.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2 = st.columns([3, 1])

with col_ctrl1:
    number_of_trials = st.slider(
        '🎯 Number of flips',
        min_value=10,
        max_value=2000,
        value=100,
        step=10,
        help="More flips = stronger convergence to 0.5"
    )

with col_ctrl2:
    st.markdown("<br>", unsafe_allow_html=True)
    start_button = st.button('▶ Run Experiment')

col_reset, _ = st.columns([1, 3])
with col_reset:
    reset_button = st.button('🗑 Clear All Experiments')

if reset_button:
    st.session_state['experiment_no'] = 0
    st.session_state['df_results'] = pd.DataFrame(columns=['#', 'Flips', 'Final Mean', 'Distance from 0.5'])
    st.session_state['history'] = []
    st.rerun()

st.markdown("---")

# ── Chart placeholder ─────────────────────────────────────────────────────────
chart_placeholder = st.empty()
metrics_placeholder = st.empty()

def render_chart(history, live_means=None, live_n=None, live_color=None):
    fig = go.Figure()

    # Reference line at 0.5
    max_x = max([len(h[1]) for h in history], default=0)
    if live_means:
        max_x = max(max_x, len(live_means))

    fig.add_hline(
        y=0.5,
        line_dash="dash",
        line_color="rgba(52, 211, 153, 0.5)",
        line_width=1.5,
        annotation_text="Expected: 0.5",
        annotation_position="bottom right",
        annotation_font_color="#34d399",
    )

    # Past experiments (faded)
    for exp_no, means, color in history:
        fig.add_trace(go.Scatter(
            y=means,
            x=list(range(1, len(means)+1)),
            mode='lines',
            name=f'Exp #{exp_no} (n={len(means)})',
            line=dict(color=color, width=1.5),
            opacity=0.4,
        ))

    # Live experiment
    if live_means:
        fig.add_trace(go.Scatter(
            y=live_means,
            x=list(range(1, len(live_means)+1)),
            mode='lines',
            name=f'Exp #{st.session_state["experiment_no"]} — LIVE',
            line=dict(color=live_color, width=3),
            opacity=1.0,
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#9ca3af'),
        xaxis=dict(
            title='Flip #',
            gridcolor='rgba(255,255,255,0.04)',
            zerolinecolor='rgba(255,255,255,0.08)',
            tickfont=dict(color='#6b7280'),
        ),
        yaxis=dict(
            title='Running Mean (Heads)',
            range=[0, 1],
            gridcolor='rgba(255,255,255,0.04)',
            zerolinecolor='rgba(255,255,255,0.08)',
            tickfont=dict(color='#6b7280'),
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.03)',
            bordercolor='rgba(255,255,255,0.06)',
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        height=420,
    )
    return fig

# Initial chart render
chart_placeholder.plotly_chart(
    render_chart(st.session_state['history']),
    use_container_width=True,
    key="initial_chart"
)

# ── Run experiment ────────────────────────────────────────────────────────────
if start_button:
    st.session_state['experiment_no'] += 1
    exp_color = COLORS[(st.session_state['experiment_no'] - 1) % len(COLORS)]

    trial_outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=number_of_trials)

    means = []
    outcome_1_count = 0

    for i, r in enumerate(trial_outcomes):
        if r == 1:
            outcome_1_count += 1
        mean = outcome_1_count / (i + 1)
        means.append(mean)

        if i % 5 == 0 or i == number_of_trials - 1:
            chart_placeholder.plotly_chart(
                render_chart(st.session_state['history'], means, number_of_trials, exp_color),
                use_container_width=True,
                key=f"live_{i}"
            )
            time.sleep(0.02)

    final_mean = means[-1]
    distance = abs(final_mean - 0.5)

    st.session_state['history'].append(
        (st.session_state['experiment_no'], means, exp_color)
    )

    st.session_state['df_results'] = pd.concat([
        st.session_state['df_results'],
        pd.DataFrame([[
            st.session_state['experiment_no'],
            number_of_trials,
            round(final_mean, 4),
            round(distance, 4)
        ]], columns=['#', 'Flips', 'Final Mean', 'Distance from 0.5'])
    ], axis=0).reset_index(drop=True)

    chart_placeholder.plotly_chart(
        render_chart(st.session_state['history']),
        use_container_width=True,
        key="final_chart"
    )

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown("---")

if st.session_state['experiment_no'] > 0:
    df = st.session_state['df_results']
    last_mean = df['Final Mean'].iloc[-1]
    last_dist = df['Distance from 0.5'].iloc[-1]
    total_exps = st.session_state['experiment_no']

    color_class = "green" if last_dist < 0.02 else ("yellow" if last_dist < 0.06 else "red")
    convergence_label = "Strong ✓" if last_dist < 0.02 else ("Moderate ~" if last_dist < 0.06 else "Weak ✗")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Last Mean</div>
            <div class="metric-value {color_class}">{last_mean}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distance from 0.5</div>
            <div class="metric-value {color_class}">{last_dist:.4f}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Convergence</div>
            <div class="metric-value {color_class}">{convergence_label}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Experiments Run</div>
            <div class="metric-value">{total_exps}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### 📋 Experiment History")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "Flips": st.column_config.NumberColumn(width="medium"),
            "Final Mean": st.column_config.NumberColumn(format="%.4f", width="medium"),
            "Distance from 0.5": st.column_config.ProgressColumn(
                format="%.4f",
                min_value=0,
                max_value=0.5,
                width="large"
            ),
        }
    )
else:
    st.markdown("""
    <div style="text-align:center; color:#4b5563; padding: 40px;">
        <div style="font-size: 3rem;">🪙</div>
        <p style="font-family: 'Space Mono', monospace; margin-top: 12px;">
            Run your first experiment to see results
        </p>
    </div>
    """, unsafe_allow_html=True)
