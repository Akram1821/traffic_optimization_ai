import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from simulation.traffic_sim import Intersection
from ai.traffic_controller import AdaptiveTrafficController
from baseline.fixed_cycle import FixedCycleController
import time
from datetime import datetime

st.set_page_config(page_title="Traffic Optimization AI", layout="wide")

st.title("🚦 Intelligent Traffic Control System")
st.markdown("Real-time traffic optimization using AI")

# Initialize session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = None
if 'running' not in st.session_state:
    st.session_state.running = False
if 'use_ai' not in st.session_state:
    st.session_state.use_ai = True
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    st.session_state.use_ai = st.toggle("🤖 Enable AI Control", value=st.session_state.use_ai)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.running = True
            if not st.session_state.simulation:
                st.session_state.simulation = Intersection()
            st.session_state.metrics_history = []
    with col2:
        if st.button("⏹️ Reset", use_container_width=True):
            st.session_state.running = False
            st.session_state.simulation = None
            st.session_state.metrics_history = []
    
    st.divider()
    st.header("📊 Metrics")
    metrics_placeholder = st.empty()

# Main display
col1, col2, col3, col4 = st.columns(4)

if st.session_state.simulation:
    # Run simulation
    if st.session_state.running:
        dt = 0.1
        metrics = st.session_state.simulation.update(dt, ai_control=st.session_state.use_ai)
        st.session_state.metrics_history.append(metrics)
        
        # Keep last 1000 steps
        if len(st.session_state.metrics_history) > 1000:
            st.session_state.metrics_history = st.session_state.metrics_history[-1000:]
        
        # Display current metrics
        with col1:
            st.metric("🚗 Queue Length", f"{metrics['queue_length']:.0f}")
        with col2:
            st.metric("⏱️ Avg Wait Time", f"{metrics['avg_wait_time']:.1f}s")
        with col3:
            st.metric("✅ Cars Processed", f"{metrics['cars_processed']}")
        with col4:
            status = "🟢" if metrics['light_state'] == 'NS' else "🔴"
            st.metric("Traffic Light", f"{status} {metrics['light_state']}")
        
        # Queue visualization
        st.subheader("📈 Queue Length Evolution")
        fig, ax = plt.subplots(figsize=(10, 4))
        history_df = pd.DataFrame(st.session_state.metrics_history)
        if len(history_df) > 0:
            ax.plot(history_df['time'], history_df['queue_length'], linewidth=2, color='blue')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Queue Length (cars)')
            ax.set_title('Real-time Queue Monitoring')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        plt.close()
        
        # Comparison chart
        st.subheader("📊 Performance Comparison")
        if len(st.session_state.metrics_history) > 10:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(history_df['time'], history_df['avg_wait_time'], linewidth=2, color='green', label='Avg Wait Time')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Wait Time (s)')
            ax2.set_title('Waiting Time Evolution')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            st.pyplot(fig2)
            plt.close()
        
        # Auto-refresh
        time.sleep(0.05)
        st.rerun()
    else:
        st.info("Click 'Start' to begin simulation")
else:
    st.info("Click 'Start' to initialize the traffic simulation")

# Display stats in sidebar
if st.session_state.metrics_history:
    avg_wait = np.mean([m['avg_wait_time'] for m in st.session_state.metrics_history[-100:]])
    avg_queue = np.mean([m['queue_length'] for m in st.session_state.metrics_history[-100:]])
    st.session_state.sidebar_metrics = metrics_placeholder.metric("Avg Wait Time (last 100s)", f"{avg_wait:.1f}s")
    st.sidebar.metric("📊 Avg Queue Length", f"{avg_queue:.1f} cars")
    st.sidebar.metric("🎯 Total Processed", f"{st.session_state.simulation.cars_processed}")

st.divider()
st.caption("🎓 Academic Project - Traffic Optimization using AI | Real-time Adaptive Control")
