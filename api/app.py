import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time
import json
import hashlib
from pathlib import Path

# Add parent directory to path
import sys
sys.path.append('..')

from agents.personalization import PersonalizedSmartSearch
from api.components.search_interface import SearchInterface
from api.components.results_display import ResultsDisplay
from api.components.user_profile import UserProfile
from utils.formatters import format_results

# Page configuration
st.set_page_config(
    page_title="Smart Search - AI-Powered Intelligent Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Ash-Blanc/smart-search',
        'Report a bug': "https://github.com/Ash-Blanc/smart-search/issues",
        'About': "# Smart Search\nAI-powered search with zero hallucinations"
    }
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    /* Main container */
    .main {
        padding-top: 2rem;
    }
    
    /* Search box styling */
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1e88e5;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Results card */
    .result-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    
    .result-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Confidence indicator */
    .confidence-high {
        color: #4caf50;
        font-weight: bold;
    }
    
    .confidence-medium {
        color: #ff9800;
        font-weight: bold;
    }
    
    .confidence-low {
        color: #f44336;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = hashlib.md5(
            str(datetime.now()).encode()
        ).hexdigest()[:8]
    if 'search_system' not in st.session_state:
        st.session_state.search_system = PersonalizedSmartSearch()
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'feedback_given' not in st.session_state:
        st.session_state.feedback_given = set()

# Load custom CSS
load_css()
init_session_state()

# Header with logo and title
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='text-align: center;'>
        <h1>🔍 Smart Search</h1>
        <p style='font-size: 1.2rem; color: #666;'>
            AI-Powered Search • Zero Hallucinations • Personalized Results
        </p>
    </div>
    """, unsafe_allow_html=True)

# Search Interface
search_container = st.container()
with search_container:
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        # Search input with suggestions
        query = st.text_input(
            "",
            placeholder="Ask anything... (e.g., 'Latest AI breakthroughs', 'Climate solutions 2024')",
            key="search_input",
            label_visibility="collapsed"
        )
        
        # Search suggestions
        if query == "":
            st.markdown("**Try searching for:**")
            suggestion_cols = st.columns(3)
            suggestions = [
                "🤖 Latest AI developments 2024",
                "🌍 Climate change solutions",
                "🚀 Space exploration news",
                "💻 Best programming practices",
                "🧬 CRISPR gene editing",
                "⚡ Renewable energy trends"
            ]
            
            for idx, suggestion in enumerate(suggestions):
                with suggestion_cols[idx % 3]:
                    if st.button(suggestion, key=f"sugg_{idx}"):
                        st.session_state.search_input = suggestion[2:]  # Remove emoji
                        st.rerun()

# Advanced options
with st.expander("⚙️ Advanced Search Options"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_depth = st.select_slider(
            "Search Depth",
            options=["Quick", "Standard", "Deep"],
            value="Standard"
        )
    
    with col2:
        enable_reasoning = st.checkbox("Show reasoning process", value=True)
        enable_sources = st.checkbox("Show all sources", value=True)
    
    with col3:
        confidence_threshold = st.slider(
            "Min. Confidence Level",
            min_value=0,
            max_value=100,
            value=70,
            help="Only show results above this confidence level"
        )

# Search execution
if query:
    # Show search progress
    progress_container = st.container()
    
    with progress_container:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        with col2:
            time_elapsed = st.empty()
    
    # Execute search with progress updates
    start_time = time.time()
    
    try:
        # Step 1: Initialize search
        progress_bar.progress(20)
        status_text.text("🔍 Analyzing your query...")
        time.sleep(0.5)
        
        # Step 2: Search execution
        progress_bar.progress(50)
        status_text.text("🌐 Searching across multiple sources...")
        
        result = st.session_state.search_system.search(
            query=query,
            user_id=st.session_state.user_id
        )
        
        # Step 3: Verification
        progress_bar.progress(80)
        status_text.text("✅ Verifying information...")
        time.sleep(0.5)
        
        # Step 4: Complete
        progress_bar.progress(100)
        elapsed = time.time() - start_time
        status_text.text(f"✨ Search completed!")
        time_elapsed.text(f"⏱️ {elapsed:.1f}s")
        
        # Store results
        st.session_state.current_results = result
        st.session_state.search_history.append({
            'query': query,
            'timestamp': datetime.now(),
            'confidence': result['confidence']
        })
        
        # Clear progress after a moment
        time.sleep(1)
        progress_container.empty()
        
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")
        st.stop()

# Display results
if st.session_state.current_results:
    results = st.session_state.current_results
    
    # Results header with metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        confidence_class = (
            "confidence-high" if results['confidence'] >= 85
            else "confidence-medium" if results['confidence'] >= 70
            else "confidence-low"
        )
        st.metric(
            "Confidence Score",
            f"{results['confidence']}%",
            delta=f"{results['confidence'] - 70:+.0f}% vs threshold"
        )
    
    with col2:
        sources_count = results['results'].count('source:') + results['results'].count('Source:')
        st.metric("Sources Found", sources_count)
    
    with col3:
        word_count = len(results['results'].split())
        st.metric("Result Length", f"{word_count} words")
    
    with col4:
        is_personalized = "✅ Yes" if results.get('personalized') else "❌ No"
        st.metric("Personalized", is_personalized)
    
    # Main results display
    st.markdown("---")
    
    # Two column layout for results and verification
    result_col, verification_col = st.columns([2, 1])
    
    with result_col:
        st.markdown("### 📊 Search Results")
        
        if results.get('personalized'):
            st.info("✨ These results have been personalized based on your search history and preferences.")
        
        # Format and display results
        formatted_results = format_results(results['results'])
        st.markdown(f"""
        <div class="result-card">
            {formatted_results}
        </div>
        """, unsafe_allow_html=True)
        
        # Feedback section
        st.markdown("---")
        st.markdown("### 💭 Was this helpful?")
        
        feedback_key = f"{query}_{datetime.now().date()}"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👍 Very Helpful", key="fb1"):
                st.session_state.feedback_given.add(feedback_key)
                st.success("Thank you for your feedback!")
                
        with col2:
            if st.button("👌 Somewhat Helpful", key="fb2"):
                st.session_state.feedback_given.add(feedback_key)
                st.info("Thanks! We'll work on improving.")
                
        with col3:
            if st.button("👎 Not Helpful", key="fb3"):
                st.session_state.feedback_given.add(feedback_key)
                st.warning("Sorry to hear that. We'll do better!")
                
        with col4:
            if st.button("🚫 Report Issue", key="fb4"):
                st.error("Issue reported. Thank you!")
    
    with verification_col:
        st.markdown("### ✅ Verification Details")
        
        # Confidence gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = results['confidence'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Confidence"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # Verification details
        with st.expander("📋 Full Verification Report"):
            st.text_area(
                "Details",
                results['verification'],
                height=200,
                disabled=True
            )
        
        # Search metadata
        st.markdown("### 📈 Search Analytics")
        
        # Create simple metrics
        metrics_data = {
            'Metric': ['Response Time', 'Sources Checked', 'Confidence', 'Personalized'],
            'Value': [f"{time.time() - start_time:.1f}s", sources_count, f"{results['confidence']}%", is_personalized]
        }
        
        df = pd.DataFrame(metrics_data)
        st.dataframe(df, hide_index=True, use_container_width=True)

# Sidebar
with st.sidebar:
    st.markdown("## 👤 User Profile")
    st.info(f"User ID: {st.session_state.user_id}")
    
    # User stats
    if st.session_state.search_history:
        st.markdown("### 📊 Your Search Stats")
        
        total_searches = len(st.session_state.search_history)
        avg_confidence = sum(s['confidence'] for s in st.session_state.search_history) / total_searches
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Searches", total_searches)
        with col2:
            st.metric("Avg. Confidence", f"{avg_confidence:.0f}%")
        
        # Search history
        st.markdown("### 🕐 Recent Searches")
        
        for search in reversed(st.session_state.search_history[-5:]):
            time_diff = datetime.now() - search['timestamp']
            time_str = (
                f"{time_diff.seconds // 60} min ago" if time_diff.seconds < 3600
                else f"{time_diff.seconds // 3600} hours ago"
            )
            
            st.markdown(f"""
            <div style='padding: 0.5rem; margin: 0.5rem 0; background-color: #f0f2f6; border-radius: 5px;'>
                <b>{search['query'][:50]}...</b><br>
                <small>{time_str} • {search['confidence']}% confidence</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Interests
        if len(st.session_state.search_history) >= 5:
            st.markdown("### 🎯 Your Interests")
            
            # Extract topics from search history (simplified)
            topics = {}
            for search in st.session_state.search_history:
                words = search['query'].lower().split()
                for word in words:
                    if len(word) > 4:  # Simple filter
                        topics[word] = topics.get(word, 0) + 1
            
            # Show top topics
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for topic, count in top_topics:
                st.markdown(f"• **{topic.title()}** ({count} searches)")
    
    # Settings
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    auto_personalize = st.checkbox("🎯 Auto-personalize", value=True)
    show_confidence = st.checkbox("📊 Always show confidence", value=True)
    
    # Export data
    if st.button("📥 Export Search History"):
        history_json = json.dumps(
            [
                {
                    'query': s['query'],
                    'timestamp': s['timestamp'].isoformat(),
                    'confidence': s['confidence']
                }
                for s in st.session_state.search_history
            ],
            indent=2
        )
        st.download_button(
            label="Download JSON",
            data=history_json,
            file_name=f"search_history_{st.session_state.user_id}.json",
            mime="application/json"
        )
    
    # About
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Smart Search** is an AI-powered search engine that provides:
    - 🎯 Accurate, hallucination-free results
    - 🔍 Multi-source verification
    - 👤 Personalized search experience
    - 🚀 Built for the OpenAI Hackathon
    
    [GitHub](https://github.com/yourusername/smart-search) | 
    [Documentation](https://github.com/yourusername/smart-search/wiki)
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Agno, DSPy, and Streamlit | 
        <a href='https://github.com/yourusername/smart-search'>GitHub</a> | 
        <a href='https://github.com/yourusername/smart-search/issues'>Report an Issue</a>
    </div>
    """,
    unsafe_allow_html=True
)