import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from crypto_portfolio_v2 import CryptoPortfolio
from transaction_manager import TransactionManager
import pandas as pd
from datetime import datetime
import time
import asyncio
import streamlit.components.v1 as components

# Add this function after the imports
def display_tradingview_widget():
    tradingview_widget = """
    <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright">
            <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
                <span class="blue-text">Track all markets on TradingView</span>
            </a>
        </div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
        {
            "feedMode": "all_symbols",
            "isTransparent": false,
            "displayMode": "regular",
            "width": "100%",
            "height": 550,
            "colorTheme": "dark",
            "locale": "en"
        }
        </script>
    </div>
    """
    components.html(tradingview_widget, height=600)

def display_market_quotes_widget():
    market_quotes_widget = """
    <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright">
            <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
                <span class="blue-text">Track all markets on TradingView</span>
            </a>
        </div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
        {
            "width": "100%",
            "height": 550,
            "symbolsGroups": [
                {
                    "name": "Cryptocurrencies",
                    "originalName": "Cryptocurrencies",
                    "symbols": [
                        {
                            "name": "BINANCE:BTCUSDT",
                            "displayName": "Bitcoin USD"
                        },
                        {
                            "name": "BINANCE:BTCBRL",
                            "displayName": "Bitcoin BRL"
                        },
                        {
                            "name": "BINANCE:UNIUSDT",
                            "displayName": "Uniswap"
                        },
                        {
                            "name": "BINANCE:LINKUSDT",
                            "displayName": "Chainlink"
                        },
                        {
                            "name": "BINANCE:ETHUSDT",
                            "displayName": "Ethereum"
                        },
                        {
                            "name": "BINANCE:LTCUSDT",
                            "displayName": "Litecoin"
                        }
                    ]
                },
                {
                    "name": "Indices",
                    "originalName": "Indices",
                    "symbols": [
                        {
                            "name": "FOREXCOM:SPXUSD",
                            "displayName": "S&P 500 Index"
                        },
                        {
                            "name": "FOREXCOM:NSXUSD",
                            "displayName": "US 100 Cash CFD"
                        },
                        {
                            "name": "FOREXCOM:DJI",
                            "displayName": "Dow Jones Industrial Average Index"
                        },
                        {
                            "name": "INDEX:NKY",
                            "displayName": "Japan 225"
                        },
                        {
                            "name": "INDEX:DEU40",
                            "displayName": "DAX Index"
                        },
                        {
                            "name": "FOREXCOM:UKXGBP",
                            "displayName": "FTSE 100 Index"
                        }
                    ]
                },
                {
                    "name": "Futures",
                    "originalName": "Futures",
                    "symbols": [
                        {
                            "name": "CME_MINI:ES1!",
                            "displayName": "S&P 500"
                        },
                        {
                            "name": "CME:6E1!",
                            "displayName": "Euro"
                        },
                        {
                            "name": "COMEX:GC1!",
                            "displayName": "Gold"
                        },
                        {
                            "name": "NYMEX:CL1!",
                            "displayName": "WTI Crude Oil"
                        },
                        {
                            "name": "NYMEX:NG1!",
                            "displayName": "Gas"
                        },
                        {
                            "name": "CBOT:ZC1!",
                            "displayName": "Corn"
                        }
                    ]
                },
                {
                    "name": "Bonds",
                    "originalName": "Bonds",
                    "symbols": [
                        {
                            "name": "CBOT:ZB1!",
                            "displayName": "T-Bond"
                        },
                        {
                            "name": "CBOT:UB1!",
                            "displayName": "Ultra T-Bond"
                        },
                        {
                            "name": "EUREX:FGBL1!",
                            "displayName": "Euro Bund"
                        },
                        {
                            "name": "EUREX:FBTP1!",
                            "displayName": "Euro BTP"
                        },
                        {
                            "name": "EUREX:FGBM1!",
                            "displayName": "Euro BOBL"
                        }
                    ]
                }
            ],
            "showSymbolLogo": true,
            "isTransparent": false,
            "colorTheme": "dark",
            "locale": "en",
            "backgroundColor": "#131722"
        }
        </script>
    </div>
    """
    components.html(market_quotes_widget, height=600)

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
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'transaction_manager' not in st.session_state:
    st.session_state.transaction_manager = TransactionManager()
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = CryptoPortfolio()

# Header
st.title("📈 Crypto Portfolio Tracker")

def update_portfolio_data():
    """Update portfolio data and last update time"""
    with st.spinner('Updating portfolio data...'):
        st.session_state.last_update = datetime.now()
        return asyncio.run(st.session_state.portfolio.get_portfolio_data())

def display_portfolio_overview():
    st.title("Portfolio Overview")
    
    # Get portfolio data
    portfolio_data = update_portfolio_data()
    
    if portfolio_data['holdings']:
        # Display portfolio metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Balance", f"R$ {portfolio_data['total_value_brl']:,.2f}")
        with col2:
            st.metric("24h Change", f"{portfolio_data['weighted_24h_change']:.2f}%")
        with col3:
            st.metric("7d Change", f"{portfolio_data['weighted_7d_change']:.2f}%")
        
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
        st.subheader("Holdings")
        df = pd.DataFrame([{
            'Symbol': h['symbol'],
            'Amount': h['amount'],
            'Price (BRL)': h['price_brl'],
            'Total Value (BRL)': h['value_brl'],
            '24h Change (%)': h['percent_change_24h'] / 100,
            '7d Change (%)': h['percent_change_7d'] / 100,
            'Portfolio %': h['portfolio_percentage']
        } for h in portfolio_data['holdings']]).set_index('Symbol')
        
        st.dataframe(
            df.style.format({
                'Amount': '{:.8f}',
                'Price (BRL)': 'R$ {:,.2f}',
                'Total Value (BRL)': 'R$ {:,.2f}',
                '24h Change (%)': '{:.2%}',
                '7d Change (%)': '{:.2%}',
                'Portfolio %': '{:.2f}%'
            }).background_gradient(
                subset=['24h Change (%)'],
                cmap='RdYlGn',
                vmin=-10,
                vmax=10,
                text_color_threshold=0.5
            ).set_properties(**{
                'background-color': 'rgb(17, 17, 17)',
                'color': 'white'
            }),
            use_container_width=True
        )
        
        # Display market quotes widget below holdings
        st.subheader("Global Market Overview")
        display_market_quotes_widget()
    else:
        st.info("No holdings in portfolio yet. Add some transactions to get started!")

def display_earnings():
    st.title("Earnings")
    
    # Get portfolio data
    portfolio = CryptoPortfolio()
    earnings_data = asyncio.run(portfolio.get_earnings_data())
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Balance", f"R$ {earnings_data['total_balance']:,.2f}")
    with col2:
        st.metric("Today's Earnings", f"R$ {earnings_data['total_daily']:,.2f}")
    with col3:
        st.metric("Total Accumulated", f"R$ {earnings_data['total_accumulated']:,.2f}")
    
    # Create two columns for earnings tables
    col_daily, col_accumulated = st.columns(2)
    
    # Display daily earnings
    with col_daily:
        st.subheader("Today's Earnings")
        daily_data = []
        for earning in earnings_data['daily_earnings']:
            daily_data.append({
                'Symbol': earning['symbol'],
                'Value': f"R$ {earning['value']:,.2f}"
            })
        
        # Create DataFrame for daily earnings
        df_daily = pd.DataFrame(daily_data)
        
        # Apply color formatting
        def color_value(val):
            color = 'green' if float(val.replace('R$ ', '').replace(',', '')) >= 0 else 'red'
            return f'color: {color}'
        
        st.dataframe(df_daily.style.map(color_value, subset=['Value']))
    
    # Display accumulated earnings
    with col_accumulated:
        st.subheader("Accumulated Earnings")
        accumulated_data = []
        for earning in earnings_data['accumulated_earnings']:
            accumulated_data.append({
                'Symbol': earning['symbol'],
                'Value': f"R$ {earning['value']:,.2f}"
            })
        
        # Create DataFrame for accumulated earnings
        df_accumulated = pd.DataFrame(accumulated_data)
        st.dataframe(df_accumulated.style.map(color_value, subset=['Value']))

def display_transaction_history():
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

def add_transaction():
    st.header("Add Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell"])
        
        # Get current holdings for symbol selection
        portfolio = CryptoPortfolio()
        portfolio_data = asyncio.run(portfolio.get_portfolio_data())
        
        # Create list of symbols from holdings
        symbols = [h['symbol'] for h in portfolio_data['holdings']]
        
        if transaction_type == "Sell":
            symbol = st.selectbox("Select Cryptocurrency", symbols) if symbols else st.text_input("Cryptocurrency Symbol").upper()
        else:
            symbol = st.text_input("Cryptocurrency Symbol").upper()
            
        # Get current price for selected crypto
        current_price = None
        for holding in portfolio_data['holdings']:
            if holding['symbol'] == symbol:
                current_price = holding['price_brl']
                break
        
        # Input value in BRL
        value_brl = st.number_input("Value (BRL)", min_value=0.0, format="%.2f")
        
        # Calculate amount based on current price
        amount = value_brl / current_price if current_price and value_brl > 0 else 0.0
        
        # Display calculated amount
        st.text(f"Amount to receive: {amount:.8f} {symbol}")
    
    with col2:
        notes = st.text_area("Notes (optional)")
    
    if st.button("Record Transaction"):
        if symbol and value_brl > 0:
            transaction = st.session_state.transaction_manager.add_transaction(
                symbol=symbol,
                amount=amount,
                price_brl=current_price,
                transaction_type=transaction_type.lower(),
                notes=notes
            )
            
            # Update portfolio
            current_amount = st.session_state.portfolio.portfolio.get(symbol, 0)
            new_amount = current_amount + amount if transaction_type == "Buy" else current_amount - amount
            st.session_state.portfolio.update_holdings(symbol, new_amount)
            
            # Force portfolio save
            st.session_state.portfolio._save_portfolio()
            
            st.success("Transaction recorded successfully!")
            st.session_state.last_update = datetime.now()
            
            # Force refresh
            st.rerun()
        else:
            st.error("Please fill in all required fields.")

def edit_holdings():
    st.header("Edit Holdings")
    
    # Create a form for editing holdings
    portfolio = CryptoPortfolio()
    portfolio_data = asyncio.run(portfolio.get_portfolio_data())
    
    if portfolio_data['holdings']:
        with st.form("edit_holdings_form"):
            edited_holdings = {}
            
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
                
                # Force portfolio save
                st.session_state.portfolio._save_portfolio()
                
                st.success("Holdings updated successfully!")
                # Force a rerun to update all displays
                st.rerun()
    else:
        st.info("No holdings to edit. Add some transactions first!")

def display_market_analysis():
    st.title("Market Analysis")
    
    # Get portfolio data and analysis
    portfolio = CryptoPortfolio()
    portfolio_data = asyncio.run(portfolio.get_portfolio_data())
    analysis = portfolio.get_market_analysis(portfolio_data)
    
    # Display the analysis
    st.markdown(analysis)
    
    # Add refresh button
    if st.button("Refresh Analysis"):
        st.session_state.last_analysis = analysis
        st.session_state.last_analysis_time = datetime.now()
        st.rerun()

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Portfolio Overview",
    "Transaction History",
    "Add Transaction",
    "Edit Holdings",
    "Earnings",
    "AI Analysis",
    "TradingView Widget"
])

with tab1:
    display_portfolio_overview()

with tab2:
    display_transaction_history()

with tab3:
    add_transaction()

with tab4:
    edit_holdings()

with tab5:
    display_earnings()

with tab6:
    display_market_analysis()

with tab7:
    display_tradingview_widget()

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    if st.button("🔄 Update Data"):
        st.rerun()

    if st.session_state.last_update:
        st.write(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit by FSTech | Data from CoinMarketCap | Analysis by OpenAI"
)
