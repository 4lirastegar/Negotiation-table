"""
Streamlit App for LLM Negotiation Simulation
Main entry point for the interactive website
"""

import streamlit as st
from utils.scenario_loader import ScenarioLoader
from personas.persona_configs import PersonaConfigs
from utils.mongodb_client import get_mongodb_client

# Custom CSS for chat bubbles
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #E3F2FD;
        margin-left: 20%;
    }
    .chat-message.assistant {
        background-color: #F1F8E9;
        margin-right: 20%;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .message-content {
        flex: 1;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .message-text {
        font-size: 1rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


def display_chat_messages(messages):
    """Display messages in a chat bubble format"""
    for msg in messages:
        agent = msg.get('agent', 'Unknown')
        persona = msg.get('persona', '')
        message = msg.get('message', '')
        round_num = msg.get('round', 0)
        msg_type = msg.get('type', 'message')
        
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
                else:
                    # Agent B messages on the left
                    col1, col2 = st.columns([5, 2])
                    with col1:
                        # Header
                        st.markdown(f"**{avatar} {agent}** ({persona}) • Round {round_num}")
                        # Message bubble
                        st.success(message)
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
st.markdown("---")

# Sidebar for configuration
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
        disabled=not scenarios or not personas or st.session_state.negotiation_running
    )

# Main content area
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
    
    # Judge analysis
    if 'judge_analysis' in results:
        st.subheader("⚖️ Judge Analysis")
        judge = results['judge_analysis']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Winner:** {judge.get('winner', 'Unknown')}")
            st.write(f"**Agent A Satisfaction:** {judge.get('agent_a_satisfaction', 'Unknown')}")
        with col2:
            st.write(f"**Agent B Satisfaction:** {judge.get('agent_b_satisfaction', 'Unknown')}")
        
        if judge.get('reasoning'):
            st.write("**Reasoning:**")
            st.write(judge['reasoning'])
    
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
