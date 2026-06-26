import time
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Real-Time Demo", layout="wide")

# ---------- Helpers ----------
def next_value(prev: int) -> int:
    """Random-walk step bounded to 0..100."""
    step = random.randint(-20, 20)
    return max(0, min(100, prev + step))

def append_point(df: pd.DataFrame, prev_val: int) -> tuple[pd.DataFrame, int]:
    """Append one (timestamp, value) row and return updated df and last value."""
    ts = pd.Timestamp(datetime.now())
    val = next_value(prev_val)
    # store as integer series with timestamp index
    df.loc[ts] = val
    return df, val

# ---------- Session init ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["value"])
    st.session_state.data.index.name = "timestamp"
    st.session_state.last_val = random.randint(20, 80)

# ---------- UI ----------
st.title("Real-Time Line Chart")
left, right = st.columns([3, 1])

with right:
    run = st.toggle("Auto-refresh", value=True, help="Toggle live updates")
    max_points = st.slider("Points to keep", min_value=20, max_value=1000, value=200, step=20)
    if st.button("Reset series"):
        st.session_state.data = pd.DataFrame(columns=["value"])
        st.session_state.data.index.name = "timestamp"
        st.session_state.last_val = random.randint(20, 80)

# ---------- Update data once per run ----------
# Each rerun appends exactly one new point (when run==True).
if run:
    st.session_state.data, st.session_state.last_val = append_point(
        st.session_state.data, st.session_state.last_val
    )
    # keep only tail
    if len(st.session_state.data) > max_points:
        st.session_state.data = st.session_state.data.tail(max_points)

# ---------- Display ----------
with left:
    st.subheader("Simulated CPU Load")
    st.line_chart(st.session_state.data, y="value", height=380, use_container_width=True)
    latest = int(st.session_state.last_val)
    st.metric("Latest value", f"{latest}")

# ---------- Auto refresh every 5 seconds ----------
# Only refresh when the toggle is on, to avoid infinite reruns.
if run:
    time.sleep(0.5)
    st.rerun()
