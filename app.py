"""
Streamlit App for LLM Negotiation Simulation
Main entry point for the interactive website
"""

import streamlit as st
from datetime import datetime
from utils.scenario_loader import ScenarioLoader
from personas.persona_configs import PersonaConfigs
from utils.mongodb_client import get_mongodb_client

# Custom CSS for better UI
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-blue: #2563EB;
        --primary-green: #059669;
        --bg-light: #F8FAFC;
        --bg-dark: #1E293B;
        --text-light: #0F172A;
        --text-dark: #F1F5F9;
    }
    
    /* Fix message text font and styling */
    .stAlert p {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        font-size: 16px !important;
        line-height: 1.7 !important;
        color: #1E293B !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    
    /* Agent A (info boxes) - Professional blue with light background */
    .stAlert[data-baseweb="notification"] {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%) !important;
        border: 2px solid #3B82F6 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Make info and success boxes prettier */
    .stAlert > div {
        padding: 1.25rem 1.5rem !important;
        border-radius: 0.75rem !important;
    }
    
    /* Success boxes (Agent B) - Professional green with light background */
    div[data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%) !important;
        border: 2px solid #10B981 !important;
    }
    
    /* Warning boxes */
    div[data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%) !important;
        border: none !important;
    }
    
    /* Error boxes */
    div[data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%) !important;
        border: none !important;
    }
    
    /* Primary Buttons (default) */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Test list buttons - clean flat design */
    button[key^="test_btn_"] {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%) !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 0.75rem !important;
        padding: 1rem 1.5rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    button[key^="test_btn_"]:hover {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border-color: #3B82F6 !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0 !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #2563EB !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 50%, #10B981 100%) !important;
    }
    
    /* Better spacing */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


def display_chat_messages(messages):
    """Display messages in a chat bubble format with prompt viewer"""
    for idx, msg in enumerate(messages):
        agent = msg.get('agent', 'Unknown')
        persona = msg.get('persona', '')
        message = msg.get('message', '')
        round_num = msg.get('round', 0)
        msg_type = msg.get('type', 'message')
        prompt = msg.get('prompt', None)
        
        # Determine avatar and styling
        if agent == "Agent A":
            avatar = "👤"
            is_agent_a = True
        else:
            avatar = "🤖"
            is_agent_a = False
        
        # Create chat bubble using Streamlit components
        if msg_type == "error":
            st.error(f"**{agent} ({persona})** - Round {round_num}: {message}")
        else:
            # Create a container for each message
            with st.container():
                # Use columns for layout
                if is_agent_a:
                    # Agent A messages on the right
                    col1, col2 = st.columns([2, 5])
                    with col1:
                        st.write("")  # Spacer
                    with col2:
                        # Header
                        st.markdown(f"**{avatar} {agent}** ({persona}) • Round {round_num}")
                        
                        # Message bubble
                        st.info(message)
                        
                        # Show prompt in collapsed expander (no button needed!)
                        if prompt:
                            with st.expander("🔍 View Prompt", expanded=False):
                                st.code(prompt, language=None)
                else:
                    # Agent B messages on the left
                    col1, col2 = st.columns([5, 2])
                    with col1:
                        # Header
                        st.markdown(f"**{avatar} {agent}** ({persona}) • Round {round_num}")
                        
                        # Message bubble
                        st.success(message)
                        
                        # Show prompt in collapsed expander (no button needed!)
                        if prompt:
                            with st.expander("🔍 View Prompt", expanded=False):
                                st.code(prompt, language=None)
                    with col2:
                        st.write("")  # Spacer
                
                st.markdown("")  # Spacing between messages

# Page configuration
st.set_page_config(
    page_title="LLM Negotiation Arena",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'negotiation_results' not in st.session_state:
    st.session_state.negotiation_results = None
if 'negotiation_running' not in st.session_state:
    st.session_state.negotiation_running = False
if 'messages_display' not in st.session_state:
    st.session_state.messages_display = []

# Title and header
st.title("🤝 LLM Negotiation Arena")
st.markdown("### Multi-Agent Negotiation Simulation")

# Main tabs at the top level
tab1, tab2, tab3 = st.tabs(["🎮 Interactive Negotiation", "📊 Batch Testing", "📈 Test Results"])

# TAB 1: Interactive Negotiation
with tab1:
    # Sidebar for Interactive Negotiation configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("Configure your negotiation scenario and agents")
        st.markdown("---")
        
        # MongoDB status
        try:
            mongo_client = get_mongodb_client()
            stats = mongo_client.get_statistics()
            
            with st.expander("💾 Database Stats", expanded=False):
                if stats:
                    st.metric("Total Negotiations", stats.get("total_negotiations", 0))
                    st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
                    st.metric("Avg Rounds", f"{stats.get('average_rounds', 0):.1f}")
                else:
                    st.caption("No data yet")
        except Exception as e:
            with st.expander("💾 Database Stats", expanded=False):
                st.error(f"Database unavailable: {str(e)[:50]}...")
        
        st.markdown("---")
        
        # Load scenarios and personas
        try:
            scenario_loader = ScenarioLoader()
            scenarios = scenario_loader.list_scenarios()
            personas = PersonaConfigs.list_personas()
        except Exception as e:
            st.error(f"Error loading scenarios/personas: {e}")
            scenarios = []
            personas = []
        
        # Scenario selector
        st.subheader("📋 Scenario")
        selected_scenario = st.selectbox(
            "Choose a negotiation scenario:",
            scenarios,
            help="Select the scenario that defines what the agents will negotiate about"
        )
        
        # Display scenario info if selected
        if selected_scenario:
            scenario_data = scenario_loader.get_scenario(selected_scenario)
            if scenario_data:
                st.caption(f"**Type:** {scenario_data.get('type', 'Unknown')}")
                st.caption(f"**Description:** {scenario_data.get('description', 'No description')}")
        
        st.markdown("---")
        
        # Agent A configuration
        st.subheader("👤 Agent A")
        agent_a_persona = st.selectbox(
            "Persona:",
            personas,
            key="agent_a_persona",
            help="Select the personality type for Agent A"
        )
        
        # Show Agent A role if scenario is selected
        if selected_scenario:
            agent_a_secrets = scenario_loader.get_agent_secrets(selected_scenario, "agent_a")
            agent_a_role = agent_a_secrets.get("role", "Unknown")
            st.caption(f"**Role:** {agent_a_role}")
        
        st.markdown("---")
        
        # Agent B configuration
        st.subheader("👤 Agent B")
        agent_b_persona = st.selectbox(
            "Persona:",
            personas,
            index=1 if len(personas) > 1 else 0,
            key="agent_b_persona",
            help="Select the personality type for Agent B"
        )
        
        # Show Agent B role if scenario is selected
        if selected_scenario:
            agent_b_secrets = scenario_loader.get_agent_secrets(selected_scenario, "agent_b")
            agent_b_role = agent_b_secrets.get("role", "Unknown")
            st.caption(f"**Role:** {agent_b_role}")
        
        st.markdown("---")
        
        # Advanced settings (collapsible)
        with st.expander("⚙️ Advanced Settings"):
            max_rounds = st.slider(
                "Maximum Rounds:",
                min_value=5,
                max_value=20,
                value=10,
                help="Maximum number of negotiation rounds"
            )
        
        st.markdown("---")

    # Start Negotiation button
    start_button = st.button(
        "🚀 Start Negotiation",
        type="primary",
        use_container_width=True,
        disabled=not scenarios or not personas or st.session_state.negotiation_running,
        key="start_interactive"
    )
    
    if not scenarios or not personas:
        st.warning("⚠️ No scenarios or personas found. Please check your configuration files.")
    elif start_button:
        # Clear previous results
        st.session_state.negotiation_results = None
        st.session_state.messages_display = []
        st.session_state.negotiation_running = True
        
        # Create chat container
        chat_container = st.container()
        
        with chat_container:
            st.header("💬 Live Negotiation")
            st.markdown("---")
            
            # Create placeholder for chat messages
            chat_placeholder = st.empty()
            
            # Initialize agents
            try:
                from simulation import NegotiationEngine, run_negotiation_realtime
                
                engine = NegotiationEngine(max_rounds=max_rounds)
                agent_a, agent_b = engine.create_agents(
                    scenario_name=selected_scenario,
                    agent_a_persona=agent_a_persona,
                    agent_b_persona=agent_b_persona
                )
                
                # Get scenario type
                scenario = engine.scenario_loader.get_scenario(selected_scenario)
                scenario_type = scenario.get("type", "price_negotiation") if scenario else "price_negotiation"
                
                # Run negotiation with real-time updates
                messages_list = []
                loading_placeholder = st.empty()
                
                for update in run_negotiation_realtime(agent_a, agent_b, max_rounds, scenario_type):
                    if update.get("type") == "message":
                        messages_list.append(update)
                        st.session_state.messages_display = messages_list
                        
                        # Display chat messages
                        with chat_placeholder.container():
                            display_chat_messages(messages_list)
                        
                        # Show loading indicator
                        with loading_placeholder:
                            st.caption("⏳ Generating next message...")
                        
                    elif update.get("type") == "status":
                        with loading_placeholder:
                            st.info(update.get("message", "Processing..."))
                    
                    elif update.get("type") == "complete":
                        # Final results
                        st.session_state.negotiation_results = update
                        st.session_state.negotiation_running = False
                        loading_placeholder.empty()
                        break
                    
                    elif update.get("type") == "error":
                        messages_list.append(update)
                        st.session_state.messages_display = messages_list
                        st.session_state.negotiation_running = False
                        st.error("❌ Error occurred during negotiation")
                        break
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error running negotiation: {e}")
                st.session_state.negotiation_running = False
                import traceback
                st.code(traceback.format_exc())

# Display results if available
if st.session_state.negotiation_results:
    st.markdown("---")
    st.header("📊 Negotiation Results")
    
    results = st.session_state.negotiation_results
    
    # Results summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Agreement Reached", "✅ Yes" if results['agreement_reached'] else "❌ No")
    
    with col2:
        st.metric("Rounds", f"{results['rounds']}/{results['max_rounds']}")
    
    with col3:
        if results['agreement_terms'] and 'price' in results['agreement_terms']:
            st.metric("Final Price", f"${results['agreement_terms']['price']:.2f}")
        else:
            st.metric("Final Price", "N/A")
    
    # Show messages with chat interface
    st.subheader("💬 Negotiation Dialogue")
    display_chat_messages(results['messages'])
    
    # Academic Analysis (Calculated Metrics)
    st.subheader("📊 Objective Analysis")
    
    # Utility scores (calculated from value functions)
    col1, col2, col3 = st.columns(3)
    with col1:
        if results.get('utility_a') is not None:
            st.metric("Agent A Utility", f"{results['utility_a']:.3f}")
            st.caption("(0.0 = min acceptable, 1.0 = ideal price)")
        else:
            st.metric("Agent A Utility", "N/A")
    
    with col2:
        if results.get('utility_b') is not None:
            st.metric("Agent B Utility", f"{results['utility_b']:.3f}")
            st.caption("(0.0 = max budget, 1.0 = ideal price)")
        else:
            st.metric("Agent B Utility", "N/A")
    
    with col3:
        # Determine winner objectively from utility scores
        if results.get('utility_a') is not None and results.get('utility_b') is not None:
            util_a = results['utility_a']
            util_b = results['utility_b']
            if abs(util_a - util_b) < 0.05:
                winner = "Both (Fair)"
            elif util_a > util_b:
                winner = "Agent A"
            else:
                winner = "Agent B"
            st.metric("Winner", winner)
            st.caption("(Based on utility scores)")
        else:
            st.metric("Winner", "N/A")
    
    # Judge's factual analysis
    if 'judge_analysis' in results:
        judge = results['judge_analysis']
        if judge.get('explanation'):
            st.write("**Judge's Analysis:**")
            st.info(judge['explanation'])
    
    # MongoDB save status
    if 'negotiation_id' in results:
        st.success(f"💾 Saved to database (ID: `{results['negotiation_id']}`)")
    
    # Reset button
    if st.button("🔄 Run New Negotiation"):
        st.session_state.negotiation_results = None
        st.rerun()

else:
    # Show instructions when no negotiation has run
    st.info("👈 Configure your negotiation in the sidebar and click 'Start Negotiation' to begin!")
    
    # Show example configuration
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Step 1: Select Scenario
        Choose a negotiation scenario from the dropdown. Each scenario defines:
        - What is being negotiated
        - Public information both agents know
        - Private information for each agent
        
        ### Step 2: Choose Personas
        Select personality types for each agent:
        - **Aggressive**: Assertive, pushes hard
        - **Fair**: Cooperative, seeks mutual benefit
        - **Liar**: Deceptive, misrepresents information
        - **Logical**: Analytical, data-driven
        - **Cooperative**: Friendly, accommodating
        - **Stubborn**: Inflexible, sticks to position
        - **Desperate**: Urgent, quick to concede
        - **Strategic**: Calculated, tactical
        
        ### Step 3: Start Negotiation
        Click the "Start Negotiation" button to run the simulation.
        The agents will negotiate in real-time, and you'll see the results!
        """)

# TAB 2: Batch Testing
with tab2:
    st.header("📊 Batch Testing & Analysis")
    st.markdown("Run multiple negotiations automatically and analyze the results")
    st.markdown("---")
    
    # Batch testing configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Test Configuration")
        
        # Persona selection for Agent A
        agent_a_persona = st.selectbox(
            "Agent A Persona:",
            personas,
            index=0 if personas else 0,
            help="Select a persona for Agent A (including 'None' for no persona)",
            key="batch_agent_a_persona"
        )
        
        # Persona selection for Agent B
        agent_b_persona = st.selectbox(
            "Agent B Persona:",
            personas,
            index=1 if len(personas) > 1 else 0,
            help="Select a persona for Agent B (including 'None' for no persona)",
            key="batch_agent_b_persona"
        )
        
        # Test name
        test_name = st.text_input(
            "Test Name:",
            value=f"{agent_a_persona} vs {agent_b_persona} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            help="Give your test a descriptive name",
            key="test_name_input"
        )
        
        # Number of negotiations
        num_negotiations = st.number_input(
            "Number of Negotiations:",
            min_value=1,
            max_value=50,
            value=10,
            help="How many negotiations to run for this persona pair"
        )
        
        # Display total
        st.metric("Total Negotiations", num_negotiations)
        st.caption(f"{agent_a_persona} vs {agent_b_persona} × {num_negotiations} runs")
    
    with col2:
        st.subheader("🎯 Scenario & Settings")
        
        # Scenario selection
        try:
            scenario_loader = ScenarioLoader()
            scenarios = scenario_loader.list_scenarios()
        except:
            scenarios = []
        
        batch_scenario = st.selectbox(
            "Scenario:",
            scenarios,
            index=0 if scenarios else 0,
            help="Choose a negotiation scenario",
            key="batch_scenario"
        )
        
        # Display scenario info
        if batch_scenario:
            scenario_data = scenario_loader.get_scenario(batch_scenario)
            if scenario_data:
                st.caption(f"**Type:** {scenario_data.get('type', 'Unknown')}")
                st.caption(f"{scenario_data.get('description', '')}")
        
        # Max rounds
        batch_max_rounds = st.slider(
            "Maximum Rounds:",
            min_value=5,
            max_value=20,
            value=10,
            help="Maximum number of negotiation rounds",
            key="batch_max_rounds"
        )
    
    st.markdown("---")
    
    # Run batch testing button
    run_batch_button = st.button(
        "▶️ Run Batch Testing",
        type="primary",
        use_container_width=True,
        disabled=not agent_a_persona or not agent_b_persona or not batch_scenario or not test_name,
        key="run_batch_testing"
    )
    
    # Run batch testing
    if run_batch_button:
        st.session_state.batch_results = []
        st.session_state.batch_running = True
        
        # Import batch testing function
        from simulation.realtime_negotiation import run_single_negotiation
        import statistics
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text(f"🔄 Running test: {test_name}")
        
        # Store document IDs
        document_ids = []
        
        # Run negotiations
        for run in range(num_negotiations):
            # Update progress
            progress = (run + 1) / num_negotiations
            progress_bar.progress(progress)
            status_text.text(f"🔄 Running negotiation {run + 1}/{num_negotiations} - {agent_a_persona} vs {agent_b_persona}")
            
            # Run negotiation
            try:
                results = run_single_negotiation(
                    scenario_name=batch_scenario,
                    agent_a_persona=agent_a_persona,
                    agent_b_persona=agent_b_persona,
                    max_rounds=batch_max_rounds
                )
                
                # Extract document ID (already saved by run_single_negotiation)
                if results:
                    doc_id = results.get("negotiation_id")
                    if doc_id:
                        document_ids.append({
                            "id": doc_id,
                            "agent_a": agent_a_persona,
                            "agent_b": agent_b_persona,
                            "run": run + 1,
                            "agreement": results.get("agreement_reached", False),
                            "rounds": results.get("total_rounds", 0),
                            "utility_a": results.get("utility_a"),
                            "utility_b": results.get("utility_b")
                        })
                    else:
                        st.warning(f"⚠️ Negotiation {run + 1} was not saved to database")
            
            except Exception as e:
                st.error(f"Error in negotiation {run + 1}: {str(e)[:100]}")
        
        # Complete - Calculate metrics
        progress_bar.progress(1.0)
        status_text.text(f"📊 Calculating comprehensive metrics...")
        
        # Calculate ALL academic metrics using MetricsCalculator
        if document_ids:
            from analysis.calculate_metrics import MetricsCalculator
            from utils.mongodb_client import get_mongodb_client
            
            # Get MongoDB client and fetch the negotiation data
            mongo_client_for_metrics = get_mongodb_client()
            negotiation_ids = [doc["id"] for doc in document_ids]
            negotiations = []
            for neg_id in negotiation_ids:
                neg = mongo_client_for_metrics.get_negotiation_by_id(neg_id)
                if neg:
                    negotiations.append(neg)
            
            # Calculate comprehensive metrics
            calculator = MetricsCalculator()
            
            # Basic metrics
            agreements = [doc["agreement"] for doc in document_ids]
            agreement_rate = sum(agreements) / len(agreements) * 100 if agreements else 0
            
            rounds_list = [doc["rounds"] for doc in document_ids if doc["agreement"]]
            avg_rounds = statistics.mean(rounds_list) if rounds_list else 0
            median_rounds = statistics.median(rounds_list) if rounds_list else 0
            
            utility_a_list = [doc["utility_a"] for doc in document_ids if doc.get("utility_a") is not None]
            utility_b_list = [doc["utility_b"] for doc in document_ids if doc.get("utility_b") is not None]
            avg_utility_a = statistics.mean(utility_a_list) if utility_a_list else 0
            avg_utility_b = statistics.mean(utility_b_list) if utility_b_list else 0
            
            # Language complexity metrics
            lang_metrics = calculator._calculate_language_metrics(negotiations) if negotiations else {"agent_a": {}, "agent_b": {}}
            
            # Build comprehensive metrics dictionary
            metrics = {
                # Agreement metrics
                "agreement_rate": agreement_rate,
                "total_agreements": sum(agreements),
                
                # Rounds metrics
                "avg_rounds_to_convergence": avg_rounds,
                "median_rounds_to_convergence": median_rounds,
                
                # Utility metrics
                "avg_utility_a": avg_utility_a,
                "avg_utility_b": avg_utility_b,
                
                # Language complexity metrics
                "language_metrics": lang_metrics
            }
            
            # Save test document to MongoDB
            try:
                status_text.text(f"💾 Saving test to database...")
                mongo_client = get_mongodb_client()
                test_id = mongo_client.save_test(
                    test_name=test_name,
                    scenario_name=batch_scenario,
                    agent_a_persona=agent_a_persona,
                    agent_b_persona=agent_b_persona,
                    negotiation_ids=[doc["id"] for doc in document_ids],
                    metrics=metrics
                )
                st.session_state.current_test_id = test_id
                status_text.text(f"✅ Test saved! (ID: {test_id})")
            except Exception as e:
                st.error(f"Failed to save test document: {str(e)}")
                st.session_state.current_test_id = None
        
        st.session_state.batch_results = document_ids
        st.session_state.batch_metrics = metrics if document_ids else {}
        st.session_state.batch_running = False
        st.success(f"🎉 Batch testing complete! {len(document_ids)} negotiations saved to database.")
        st.balloons()
    
    # Display results if batch testing has been run
    if 'batch_results' in st.session_state and st.session_state.batch_results:
        st.markdown("---")
        st.subheader("📋 Results Summary")
        
        results = st.session_state.batch_results
        
        # Display document IDs
        with st.expander("🔑 Document IDs", expanded=False):
            st.caption(f"Total documents: {len(results)}")
            for idx, doc in enumerate(results, 1):
                agreement_emoji = "✅" if doc.get("agreement") else "❌"
                st.text(f"{idx}. {agreement_emoji} {doc['id']} - {doc['agent_a']} vs {doc['agent_b']} (Run {doc['run']}) - {doc['rounds']} rounds")
        
        # Display ALL metrics
        st.markdown("---")
        st.subheader("📊 Quantitative Metrics")
        
        # Use metrics from session state (already calculated)
        if 'batch_metrics' in st.session_state and st.session_state.batch_metrics:
            metrics = st.session_state.batch_metrics
            
            # ===== 1. AGREEMENT & ROUNDS METRICS =====
            st.markdown("### 📈 Agreement & Convergence")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Agreement Rate", f"{metrics.get('agreement_rate', 0):.1f}%")
                st.caption(f"{metrics.get('total_agreements', 0)} agreements")
            
            with col2:
                st.metric("Avg Rounds", f"{metrics.get('avg_rounds_to_convergence', 0):.1f}")
                st.caption("(when agreement reached)")
            
            with col3:
                st.metric("Median Rounds", f"{metrics.get('median_rounds_to_convergence', 0):.1f}")
                st.caption("(when agreement reached)")
            
            with col4:
                st.metric("Total Tests", f"{len(results)}")
                st.caption("negotiations run")
            
            # ===== 2. UTILITY METRICS =====
            st.markdown("---")
            st.markdown("### 💰 Utility Scores")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Agent A Utility", f"{metrics.get('avg_utility_a', 0):.3f}")
                st.caption("Average utility score (0=worst, 1=best)")
            
            with col2:
                st.metric("Agent B Utility", f"{metrics.get('avg_utility_b', 0):.3f}")
                st.caption("Average utility score (0=worst, 1=best)")
            
            # ===== 3. LANGUAGE COMPLEXITY METRICS =====
            lang_metrics = metrics.get('language_metrics', {})
            if lang_metrics and (lang_metrics.get('agent_a') or lang_metrics.get('agent_b')):
                st.markdown("---")
                st.markdown("### 📝 Language Complexity Metrics")
                
                agent_a_lang = lang_metrics.get('agent_a', {})
                agent_b_lang = lang_metrics.get('agent_b', {})
                
                # Basic language metrics
                st.markdown("#### 🔤 Basic Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Agent A: Avg Words/Msg", f"{agent_a_lang.get('avg_words_per_message', 0):.1f}")
                    st.caption("Average message length")
                
                with col2:
                    st.metric("Agent B: Avg Words/Msg", f"{agent_b_lang.get('avg_words_per_message', 0):.1f}")
                    st.caption("Average message length")
                
                with col3:
                    st.metric("Agent A: Avg Word Length", f"{agent_a_lang.get('avg_word_length', 0):.2f}")
                    st.caption("Characters per word")
                
                with col4:
                    st.metric("Agent B: Avg Word Length", f"{agent_b_lang.get('avg_word_length', 0):.2f}")
                    st.caption("Characters per word")
                
                # Vocabulary richness (TTR)
                st.markdown("#### 🎨 Vocabulary Richness (Type-Token Ratio)")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.metric("Agent A: TTR", f"{agent_a_lang.get('avg_vocabulary_richness', 0):.3f}")
                    st.caption("Basic TTR")
                
                with col2:
                    st.metric("Agent B: TTR", f"{agent_b_lang.get('avg_vocabulary_richness', 0):.3f}")
                    st.caption("Basic TTR")
                
                with col3:
                    st.metric("Agent A: Root TTR", f"{agent_a_lang.get('avg_root_ttr', 0):.3f}")
                    st.caption("RTTR (normalized)")
                
                with col4:
                    st.metric("Agent B: Root TTR", f"{agent_b_lang.get('avg_root_ttr', 0):.3f}")
                    st.caption("RTTR (normalized)")
                
                with col5:
                    st.metric("Agent A: Corrected TTR", f"{agent_a_lang.get('avg_corrected_ttr', 0):.3f}")
                    st.caption("CTTR (corrected)")
                
                with col6:
                    st.metric("Agent B: Corrected TTR", f"{agent_b_lang.get('avg_corrected_ttr', 0):.3f}")
                    st.caption("CTTR (corrected)")
                
                # Readability (Flesch metrics)
                st.markdown("#### 📖 Readability (Flesch Metrics)")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Agent A: Flesch Reading Ease", f"{agent_a_lang.get('avg_flesch_reading_ease', 0):.1f}")
                    st.caption("0-100 (higher = easier)")
                
                with col2:
                    st.metric("Agent B: Flesch Reading Ease", f"{agent_b_lang.get('avg_flesch_reading_ease', 0):.1f}")
                    st.caption("0-100 (higher = easier)")
                
                with col3:
                    st.metric("Agent A: F-K Grade", f"{agent_a_lang.get('avg_flesch_kincaid_grade', 0):.1f}")
                    st.caption("US grade level")
                
                with col4:
                    st.metric("Agent B: F-K Grade", f"{agent_b_lang.get('avg_flesch_kincaid_grade', 0):.1f}")
                    st.caption("US grade level")
                
                # Linguistic features
                st.markdown("#### 💬 Linguistic Features")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Agent A: Questions", f"{agent_a_lang.get('total_questions', 0)}")
                    st.caption("Total question marks")
                
                with col2:
                    st.metric("Agent B: Questions", f"{agent_b_lang.get('total_questions', 0)}")
                    st.caption("Total question marks")
                
                with col3:
                    st.metric("Total $ Mentions", f"{agent_a_lang.get('total_dollar_mentions', 0) + agent_b_lang.get('total_dollar_mentions', 0)}")
                    st.caption("Price discussions")
        
        else:
            st.info("💡 Run a batch test to see metrics!")
    
    # Instructions when no batch testing has run
    else:
        st.info("👆 Configure your batch test above and click 'Run Batch Testing' to start!")
        
        with st.expander("📖 How Batch Testing Works"):
            st.markdown("""
            ### Batch Testing Process
            
            1. **Select Personas**: Choose multiple personas for both agents
               - Select "None" for pure emergent behavior without persona influence
               
            2. **Set Runs per Pair**: Decide how many times to test each combination
               - More runs = more reliable statistics
               
            3. **Run Tests**: All negotiations run automatically
               - Progress bar shows completion percentage
               - Each negotiation is saved to MongoDB
               
            4. **Analyze Results**: View comprehensive metrics
               - Agreement rates
               - Average rounds to convergence
               - Utility scores
               - Language complexity
               - Visualizations and charts
            
            ### What You Get
            
            - **Document IDs**: MongoDB document IDs for all negotiations
            - **Quantitative Metrics**: Statistical analysis of all results
            - **Visualizations**: Charts showing patterns and trends
            - **Raw Data**: Downloadable table with all results
            """)

# TAB 3: Test Results
with tab3:
    st.header("📈 Test Results")
    st.markdown("View and analyze your saved batch tests")
    st.markdown("---")
    
    # Load all tests from database
    try:
        mongo_client = get_mongodb_client()
        all_tests = mongo_client.get_all_tests()
        
        if all_tests:
            # Display tests as buttons
            st.subheader("📋 Saved Tests")
            st.caption(f"Total tests: {len(all_tests)} • Click on a test to view details")
            
            # Initialize selected_test in session state if not exists
            if 'selected_test_id' not in st.session_state:
                st.session_state.selected_test_id = None
            
            # Create buttons for each test (grid layout)
            st.markdown("<br>", unsafe_allow_html=True)
            
            for idx, test in enumerate(all_tests):
                test_name = test.get('test_name', 'Unnamed Test')
                created_at = test.get('timestamp', test.get('created_at', 'Unknown date'))
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d %H:%M')
                
                scenario = test.get('scenario_name', test.get('scenario', 'N/A'))
                agent_a = test.get('agent_a_persona', 'N/A')
                agent_b = test.get('agent_b_persona', 'N/A')
                total_negs = len(test.get('negotiation_ids', []))
                metrics = test.get('metrics', {})
                agreement_rate = metrics.get('agreement_rate', 0)
                
                # Create a styled container for each test
                cols = st.columns([1, 3, 2, 2, 2, 2])
                
                with cols[0]:
                    st.markdown(f"<h3 style='margin:0; padding-top:10px;'>#{idx+1}</h3>", unsafe_allow_html=True)
                
                with cols[1]:
                    if st.button(
                        f"📊 {test_name}",
                        key=f"test_btn_{test['_id']}",
                        use_container_width=True,
                        help=f"Click to view detailed results"
                    ):
                        st.session_state.selected_test_id = test['_id']
                        st.rerun()
                
                with cols[2]:
                    st.markdown(f"**Scenario:**<br>{scenario}", unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"**Personas:**<br>{agent_a} vs {agent_b}", unsafe_allow_html=True)
                
                with cols[4]:
                    st.markdown(f"**Negotiations:**<br>{total_negs}", unsafe_allow_html=True)
                
                with cols[5]:
                    st.markdown(f"**Agreement Rate:**<br>{agreement_rate:.1f}%", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'>", unsafe_allow_html=True)
            
            # Display selected test results
            if st.session_state.selected_test_id:
                selected_test_id = st.session_state.selected_test_id
                
                # Load test details
                test_data = mongo_client.get_test_by_id(selected_test_id)
                
                if test_data:
                    st.markdown("---")
                    
                    # Back button
                    if st.button("← Back to Test List", key="back_to_list"):
                        st.session_state.selected_test_id = None
                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Test header with key info
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Test Name", test_data.get('test_name', 'N/A'))
                    with col2:
                        st.metric("Scenario", test_data.get('scenario', 'N/A'))
                    with col3:
                        st.metric("Personas", f"{test_data.get('agent_a_persona')} vs {test_data.get('agent_b_persona')}")
                    with col4:
                        st.metric("Total Negotiations", test_data.get('total_negotiations', 0))
                    
                    st.markdown("---")
                    
                    # Display ALL metrics (same layout as Batch Testing tab)
                    st.subheader("📊 Quantitative Metrics")
                    
                    metrics = test_data.get('metrics', {})
                    negotiation_ids = test_data.get('negotiation_ids', [])
                    
                    # ===== 1. AGREEMENT & ROUNDS METRICS =====
                    st.markdown("### 📈 Agreement & Convergence")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Agreement Rate", f"{metrics.get('agreement_rate', 0):.1f}%")
                        st.caption(f"{metrics.get('total_agreements', 0)} agreements")
                    
                    with col2:
                        st.metric("Avg Rounds", f"{metrics.get('avg_rounds_to_convergence', 0):.1f}")
                        st.caption("(when agreement reached)")
                    
                    with col3:
                        st.metric("Median Rounds", f"{metrics.get('median_rounds_to_convergence', 0):.1f}")
                        st.caption("(when agreement reached)")
                    
                    with col4:
                        st.metric("Total Tests", f"{len(negotiation_ids)}")
                        st.caption("negotiations run")
                    
                    # ===== 2. UTILITY METRICS =====
                    st.markdown("---")
                    st.markdown("### 💰 Utility Scores")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Agent A Utility", f"{metrics.get('avg_utility_a', 0):.3f}")
                        st.caption("Average utility score (0=worst, 1=best)")
                    
                    with col2:
                        st.metric("Agent B Utility", f"{metrics.get('avg_utility_b', 0):.3f}")
                        st.caption("Average utility score (0=worst, 1=best)")
                    
                    # ===== 3. LANGUAGE COMPLEXITY METRICS =====
                    lang_metrics = metrics.get('language_metrics', {})
                    if lang_metrics and (lang_metrics.get('agent_a') or lang_metrics.get('agent_b')):
                        st.markdown("---")
                        st.markdown("### 📝 Language Complexity Metrics")
                        
                        agent_a_lang = lang_metrics.get('agent_a', {})
                        agent_b_lang = lang_metrics.get('agent_b', {})
                        
                        # Basic language metrics
                        st.markdown("#### 🔤 Basic Metrics")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Agent A: Avg Words/Msg", f"{agent_a_lang.get('avg_words_per_message', 0):.1f}")
                            st.caption("Average message length")
                        
                        with col2:
                            st.metric("Agent B: Avg Words/Msg", f"{agent_b_lang.get('avg_words_per_message', 0):.1f}")
                            st.caption("Average message length")
                        
                        with col3:
                            st.metric("Agent A: Avg Word Length", f"{agent_a_lang.get('avg_word_length', 0):.2f}")
                            st.caption("Characters per word")
                        
                        with col4:
                            st.metric("Agent B: Avg Word Length", f"{agent_b_lang.get('avg_word_length', 0):.2f}")
                            st.caption("Characters per word")
                        
                        # Vocabulary richness (TTR)
                        st.markdown("#### 🎨 Vocabulary Richness (Type-Token Ratio)")
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        
                        with col1:
                            st.metric("Agent A: TTR", f"{agent_a_lang.get('avg_vocabulary_richness', 0):.3f}")
                            st.caption("Basic TTR")
                        
                        with col2:
                            st.metric("Agent B: TTR", f"{agent_b_lang.get('avg_vocabulary_richness', 0):.3f}")
                            st.caption("Basic TTR")
                        
                        with col3:
                            st.metric("Agent A: Root TTR", f"{agent_a_lang.get('avg_root_ttr', 0):.3f}")
                            st.caption("RTTR (normalized)")
                        
                        with col4:
                            st.metric("Agent B: Root TTR", f"{agent_b_lang.get('avg_root_ttr', 0):.3f}")
                            st.caption("RTTR (normalized)")
                        
                        with col5:
                            st.metric("Agent A: Corrected TTR", f"{agent_a_lang.get('avg_corrected_ttr', 0):.3f}")
                            st.caption("CTTR (corrected)")
                        
                        with col6:
                            st.metric("Agent B: Corrected TTR", f"{agent_b_lang.get('avg_corrected_ttr', 0):.3f}")
                            st.caption("CTTR (corrected)")
                        
                        # Readability (Flesch metrics)
                        st.markdown("#### 📖 Readability (Flesch Metrics)")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Agent A: Flesch Reading Ease", f"{agent_a_lang.get('avg_flesch_reading_ease', 0):.1f}")
                            st.caption("0-100 (higher = easier)")
                        
                        with col2:
                            st.metric("Agent B: Flesch Reading Ease", f"{agent_b_lang.get('avg_flesch_reading_ease', 0):.1f}")
                            st.caption("0-100 (higher = easier)")
                        
                        with col3:
                            st.metric("Agent A: F-K Grade", f"{agent_a_lang.get('avg_flesch_kincaid_grade', 0):.1f}")
                            st.caption("US grade level")
                        
                        with col4:
                            st.metric("Agent B: F-K Grade", f"{agent_b_lang.get('avg_flesch_kincaid_grade', 0):.1f}")
                            st.caption("US grade level")
                        
                        # Linguistic features
                        st.markdown("#### 💬 Linguistic Features")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Agent A: Questions", f"{agent_a_lang.get('total_questions', 0)}")
                            st.caption("Total question marks")
                        
                        with col2:
                            st.metric("Agent B: Questions", f"{agent_b_lang.get('total_questions', 0)}")
                            st.caption("Total question marks")
                        
                        with col3:
                            st.metric("Total $ Mentions", f"{agent_a_lang.get('total_dollar_mentions', 0) + agent_b_lang.get('total_dollar_mentions', 0)}")
                            st.caption("Price discussions")
                    
                    st.markdown("---")
                    
                    # Display negotiation IDs
                    with st.expander("🔑 Negotiation Document IDs", expanded=False):
                        st.caption(f"Total negotiations: {len(negotiation_ids)}")
                        
                        # Load negotiation details for this test
                        negotiations = mongo_client.get_test_negotiations(negotiation_ids)
                        
                        for idx, neg in enumerate(negotiations, 1):
                            agreement_emoji = "✅" if neg.get("agreement_reached") else "❌"
                            st.text(f"{idx}. {agreement_emoji} {neg['_id']} - {neg.get('total_rounds', 0)} rounds")
                
                else:
                    st.error("❌ Could not load test data")
        
        else:
            st.info("📭 No saved tests found. Run a batch test first!")
            st.caption("Go to the 'Batch Testing' tab to create your first test.")
    
    except Exception as e:
        st.error(f"❌ Error loading tests: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
