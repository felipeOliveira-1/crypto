import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from crypto_portfolio_v2 import CryptoPortfolio
from transaction_manager import TransactionManager
import pandas as pd
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Crypto Portfolio Tracker",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = CryptoPortfolio()
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'transaction_manager' not in st.session_state:
    st.session_state.transaction_manager = TransactionManager()
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = None

# Header
st.title("📈 Crypto Portfolio Tracker")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portfolio Overview", 
    "Transaction History", 
    "Add Transaction",
    "Edit Holdings",
    "AI Analysis"
])

with tab1:
    st.header("Portfolio Overview")
    
    # Get portfolio data
    portfolio_data = st.session_state.portfolio.calculate_portfolio_value()
    
    if portfolio_data:
        # Display portfolio metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", f"R$ {portfolio_data['total_value_brl']:,.2f}")
        with col2:
            avg_change = (pd.DataFrame([{
                'Symbol': h['symbol'],
                'Amount': h['amount'],
                'Price (BRL)': h['price_brl'],
                'Total Value (BRL)': h['value_brl'],
                '24h Change (%)': h['percent_change_24h'] / 100  # Convert to decimal for percentage formatting
            } for h in portfolio_data['holdings']]).set_index('Symbol')['24h Change (%)'] * pd.DataFrame([{
                'Symbol': h['symbol'],
                'Amount': h['amount'],
                'Price (BRL)': h['price_brl'],
                'Total Value (BRL)': h['value_brl'],
                '24h Change (%)': h['percent_change_24h'] / 100  # Convert to decimal for percentage formatting
            } for h in portfolio_data['holdings']]).set_index('Symbol')['Total Value (BRL)'] / portfolio_data['total_value_brl']).sum()
            st.metric("24h Average Change", f"{avg_change:.2%}")
        with col3:
            st.metric("Number of Assets", str(len(portfolio_data['holdings'])))

        # Display portfolio composition pie chart
        st.subheader("Portfolio Composition")
        fig = px.pie(
            values=[h['value_brl'] for h in portfolio_data['holdings']],
            names=[h['symbol'] for h in portfolio_data['holdings']],
            title="Portfolio Composition",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display holdings table
        df = pd.DataFrame([{
            'Symbol': h['symbol'],
            'Amount': h['amount'],
            'Price (BRL)': h['price_brl'],
            'Total Value (BRL)': h['value_brl'],
            '24h Change (%)': h['percent_change_24h'] / 100  # Convert to decimal for percentage formatting
        } for h in portfolio_data['holdings']]).set_index('Symbol')
        st.dataframe(
            df.style.format({
                'Amount': '{:.8f}',
                'Price (BRL)': 'R$ {:,.2f}',
                'Total Value (BRL)': 'R$ {:,.2f}',
                '24h Change (%)': '{:.2%}'
            }).background_gradient(
                subset=['24h Change (%)'],
                cmap='RdYlGn',
                vmin=-10,
                vmax=10
            ),
            use_container_width=True
        )

with tab2:
    st.header("Transaction History")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        symbol_filter = st.selectbox(
            "Filter by Symbol",
            ["All"] + list(st.session_state.portfolio.portfolio.keys()),
            key="symbol_filter"
        )
    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All", "buy", "sell"],
            key="type_filter"
        )
    
    # Get filtered transactions
    transactions = st.session_state.transaction_manager.get_transactions(
        symbol=None if symbol_filter == "All" else symbol_filter,
        transaction_type=None if type_filter == "All" else type_filter
    )
    
    if transactions:
        df = pd.DataFrame(transactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        st.dataframe(
            df.style.format({
                'amount': '{:.8f}',
                'price_brl': 'R$ {:,.2f}',
                'total_brl': 'R$ {:,.2f}',
                'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            }),
            use_container_width=True
        )
    else:
        st.info("No transactions recorded yet.")

with tab3:
    st.header("Add Transaction")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Crypto Symbol").upper()
        amount = st.number_input("Amount", min_value=0.0, format="%f")
        price = st.number_input("Price (BRL)", min_value=0.0, format="%f")
    
    with col2:
        transaction_type = st.selectbox("Transaction Type", ["buy", "sell"])
        notes = st.text_area("Notes (optional)")
    
    if st.button("Record Transaction"):
        if symbol and amount > 0 and price > 0:
            transaction = st.session_state.transaction_manager.add_transaction(
                symbol=symbol,
                amount=amount,
                price_brl=price,
                transaction_type=transaction_type,
                notes=notes
            )
            
            # Update portfolio
            current_amount = st.session_state.portfolio.portfolio.get(symbol, 0)
            new_amount = current_amount + amount if transaction_type == "buy" else current_amount - amount
            st.session_state.portfolio.update_holdings(symbol, new_amount)
            
            st.success("Transaction recorded successfully!")
            st.session_state.last_update = datetime.now()
        else:
            st.error("Please fill in all required fields.")

with tab4:
    st.header("Edit Holdings")
    
    # Create a form for editing holdings
    with st.form("edit_holdings_form"):
        edited_holdings = {}
        
        # Get current portfolio data for reference
        portfolio_data = st.session_state.portfolio.calculate_portfolio_value()
        
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        for i, (symbol, amount) in enumerate(st.session_state.portfolio.portfolio.items()):
            # Alternate between columns
            with col1 if i % 2 == 0 else col2:
                current_value = None
                for holding in portfolio_data['holdings']:
                    if holding['symbol'] == symbol:
                        current_value = f"Current Value: R$ {holding['value_brl']:,.2f}"
                        break
                
                new_amount = st.number_input(
                    f"{symbol} Amount",
                    min_value=0.0,
                    value=float(amount),
                    format="%.8f",
                    help=current_value,
                    key=f"edit_{symbol}"
                )
                edited_holdings[symbol] = new_amount
        
        # Add submit button
        if st.form_submit_button("Update Holdings"):
            # Update portfolio with new values
            for symbol, amount in edited_holdings.items():
                st.session_state.portfolio.update_holdings(symbol, amount)
            st.success("Holdings updated successfully!")
            # Force a rerun to update all displays
            st.rerun()

with tab5:
    st.header("AI Analysis")
    
    # Add auto-refresh toggle and analysis generation
    col1, col2 = st.columns([3, 1])
    with col1:
        auto_refresh = st.toggle("Auto-refresh analysis", value=False)
    with col2:
        if st.button("Generate Analysis"):
            analysis = st.session_state.portfolio.get_market_analysis()
            st.session_state.last_analysis = analysis
            st.session_state.last_analysis_time = datetime.now()

    # Display last analysis time if available
    if st.session_state.last_analysis_time is not None:
        st.caption(f"Last updated: {st.session_state.last_analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display the analysis
    if st.session_state.last_analysis is not None:
        st.markdown(st.session_state.last_analysis)

    # Auto-refresh logic
    if auto_refresh and st.session_state.last_analysis_time is not None:
        time_since_last = datetime.now() - st.session_state.last_analysis_time
        if time_since_last.total_seconds() > 300:  # 5 minutes
            analysis = st.session_state.portfolio.get_market_analysis()
            st.session_state.last_analysis = analysis
            st.session_state.last_analysis_time = datetime.now()
            st.experimental_rerun()

# Sidebar
with st.sidebar:
    st.header("Settings")
    update_interval = st.slider(
        "Update interval (seconds)",
        min_value=30,
        max_value=300,
        value=60,
        step=30
    )
    
    if st.button("Update Now"):
        st.session_state.portfolio = CryptoPortfolio()
        st.session_state.last_update = datetime.now()

# Auto-refresh logic
if st.session_state.last_update:
    st.sidebar.write(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Check if it's time to update
    time_since_update = (datetime.now() - st.session_state.last_update).total_seconds()
    if time_since_update >= update_interval:
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit by FSTech | Data from CoinMarketCap | Analysis by OpenAI"
)
