import streamlit as st
import plotly.graph_objects as go
from crypto_portfolio_v2 import CryptoPortfolio
import pandas as pd
from datetime import datetime
import asyncio
import streamlit.components.v1 as components
import os
import time

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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #0E1117;
    }
    
    /* Card styling */
    .stMetric {
        background-color: #1E2329;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Table styling */
    .dataframe {
        background-color: #1E2329;
        border-radius: 10px;
        border: none !important;
    }
    
    .dataframe th {
        background-color: #262B33;
        color: #B7BDC6 !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px !important;
    }
    
    .dataframe td {
        color: #E6E8EA !important;
        padding: 12px !important;
        border-bottom: 1px solid #2B3139 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E2329;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2B3139;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #2B3139;
        color: #E6E8EA;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #3B4149;
        transform: translateY(-1px);
    }
    
    /* Chart styling */
    .js-plotly-plot {
        background-color: #1E2329;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Positive/Negative values */
    .positive {
        color: #00C087 !important;
    }
    
    .negative {
        color: #F6465D !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = CryptoPortfolio()
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

async def get_portfolio_data():
    """Async function to get portfolio data"""
    portfolio = CryptoPortfolio()
    return await portfolio.get_portfolio_data()

def run_async(coroutine):
    """Helper function to run async code"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coroutine)
    except RuntimeError:
        # If the loop is closed, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)

def update_portfolio_data():
    """Update portfolio data and last update time"""
    try:
        # Create a new portfolio instance for each update
        portfolio = CryptoPortfolio()
        portfolio_data = run_async(portfolio.get_portfolio_data(force_refresh=True))
        st.session_state.portfolio_data = portfolio_data
        st.session_state.last_update = datetime.now()
        return portfolio_data
    except Exception as e:
        st.error(f"Failed to update portfolio: {str(e)}")
        return st.session_state.portfolio_data

def auto_update_portfolio():
    """Auto-update portfolio data every 5 minutes"""
    if 'last_auto_update' not in st.session_state:
        st.session_state.last_auto_update = datetime.min
    
    current_time = datetime.now()
    if (current_time - st.session_state.last_auto_update).total_seconds() >= 300:  # 5 minutes
        try:
            # Create a new portfolio instance for auto-update
            portfolio_data = update_portfolio_data()
            st.session_state.last_auto_update = current_time
            return portfolio_data
        except Exception as e:
            st.error(f"Failed to auto-update portfolio: {str(e)}")
            return st.session_state.portfolio_data
    return st.session_state.portfolio_data

def display_portfolio_overview():
    """Display the portfolio overview section"""
    st.markdown("# Portfolio Overview")
    
    # Add update button in the sidebar with last update time
    last_update = st.session_state.portfolio_data.get('timestamp', 'Never') if st.session_state.portfolio_data else 'Never'
    last_update_dt = datetime.fromisoformat(last_update) if last_update != 'Never' else None
    last_update_str = last_update_dt.strftime("%Y-%m-%d %H:%M:%S") if last_update_dt else 'Never'
    
    st.sidebar.markdown("### Portfolio Updates")
    st.sidebar.text(f"Last Update: {last_update_str}")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Update Now", key="update_portfolio"):
            with st.spinner('Updating portfolio data...'):
                try:
                    # Create a new portfolio instance for manual update
                    st.session_state.portfolio_data = update_portfolio_data()
                    st.success('Portfolio updated successfully!')
                    time.sleep(0.5)  # Add a small delay before rerun
                    st.rerun()
                except Exception as e:
                    st.error(f'Failed to update portfolio: {str(e)}')
                    return
    
    with col2:
        auto_update = st.checkbox("Auto Update", value=True, key="auto_update")
    
    if auto_update:
        portfolio_data = auto_update_portfolio()
    else:
        portfolio_data = st.session_state.portfolio_data
    
    if portfolio_data is None:
        with st.spinner('Loading portfolio data...'):
            portfolio_data = update_portfolio_data()
            st.rerun()

    # Portfolio Value Card
    total_value = portfolio_data.get('total_value_brl', 0)
    change_24h = portfolio_data.get('weighted_24h_change', 0)
    
    value_color = "positive" if change_24h >= 0 else "negative"
    change_symbol = "↑" if change_24h >= 0 else "↓"
    
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h3 style='color: #B7BDC6; margin-bottom: 5px;'>Total Portfolio Value</h3>
            <h1 style='font-size: 2.5em; margin: 0;'>R$ {total_value:.2f}</h1>
            <p class='{value_color}' style='font-size: 1.2em; margin-top: 5px;'>
                {change_symbol} {abs(change_24h):.2f}%
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Portfolio Composition
    st.markdown("### Portfolio Composition")
    
    # Create donut chart with Plotly
    holdings = portfolio_data.get('holdings', [])
    
    # Sort holdings by value
    holdings = sorted(holdings, key=lambda x: x['value_brl'], reverse=True)
    
    labels = [h['symbol'] for h in holdings]
    values = [h['value_brl'] for h in holdings]
    colors = ['#1E88E5', '#FFC107', '#E53935', '#43A047', '#5E35B1', '#FB8C00']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=14, color='#E6E8EA'),
    )])
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#E6E8EA')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, l=0, r=0, b=0),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Holdings Table
    st.markdown("### Holdings Details")
    
    # Create DataFrame
    df = pd.DataFrame(holdings)
    df['price_brl'] = df['price_brl'].map('R$ {:.2f}'.format)
    df['value_brl'] = df['value_brl'].map('R$ {:.2f}'.format)
    df['percent_change_24h'] = df['percent_change_24h'].map('{:+.2f}%'.format)
    df['percent_change_7d'] = df['percent_change_7d'].map('{:+.2f}%'.format)
    
    # Rename columns
    df = df.rename(columns={
        'symbol': 'Symbol',
        'amount': 'Amount',
        'price_brl': 'Price (BRL)',
        'value_brl': 'Value (BRL)',
        'percent_change_24h': '24h Change',
        'percent_change_7d': '7d Change'
    })
    
    # Apply conditional styling
    def style_negative_positive(val):
        try:
            value = float(val.strip('%'))
            color = '#00C087' if value >= 0 else '#F6465D'
            return f'color: {color}'
        except:
            return ''

    # Style the dataframe
    styled_df = df.style.map(
        style_negative_positive,
        subset=['24h Change', '7d Change']
    )
    
    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True
    )

def edit_holdings():
    """Edit portfolio holdings"""
    st.markdown("# Edit Holdings")
    
    portfolio = st.session_state.portfolio
    
    # Form for adding new holdings
    with st.form("add_holding"):
        st.markdown("### Add New Holding")
        col1, col2 = st.columns(2)
        
        with col1:
            # Get list of current symbols from portfolio
            current_symbols = list(portfolio.portfolio.keys())
            # Add an option for new symbol
            symbol_options = ["New Symbol"] + current_symbols
            symbol_choice = st.selectbox("Select Symbol", symbol_options)
            
            if symbol_choice == "New Symbol":
                symbol = st.text_input("Enter Symbol (e.g., BTC)", "").strip().upper()
            else:
                symbol = symbol_choice
                
        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=0.0,
                step=0.00000001,
                format="%f"
            )
        
        submitted = st.form_submit_button("Add Holding")
        if submitted:
            if symbol_choice == "New Symbol" and not symbol:
                st.error("Please enter a symbol")
            elif amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                try:
                    if symbol_choice == "New Symbol":
                        portfolio.add_holding(symbol, amount)
                        st.success(f"Added {amount} {symbol} to portfolio")
                    else:
                        portfolio.update_holdings(symbol, amount)
                        st.success(f"Updated {symbol} amount to {amount}")
                    # Update portfolio data with force_refresh=True
                    portfolio_data = run_async(portfolio.get_portfolio_data(force_refresh=True))
                    st.session_state.portfolio_data = portfolio_data
                    time.sleep(0.5)  # Add a small delay before rerun
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    
    # Display current holdings with edit/delete options
    st.markdown("### Current Holdings")
    holdings = [{"symbol": symbol, "amount": amount} for symbol, amount in portfolio.portfolio.items()]
    
    if not holdings:
        st.info("No holdings in portfolio. Add some above!")
        return
    
    for holding in holdings:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{holding['symbol']}**")
            with col2:
                new_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(holding['amount']),
                    step=0.00000001,
                    key=f"amount_{holding['symbol']}",
                    format="%f"
                )
                if new_amount != float(holding['amount']):
                    try:
                        portfolio.update_holdings(holding['symbol'], new_amount)
                        st.success(f"Updated {holding['symbol']} amount to {new_amount}")
                        # Update portfolio data with force_refresh=True
                        portfolio_data = run_async(portfolio.get_portfolio_data(force_refresh=True))
                        st.session_state.portfolio_data = portfolio_data
                        time.sleep(0.5)  # Add a small delay before rerun
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            
            with col3:
                if st.button("🗑️", key=f"delete_{holding['symbol']}"):
                    if st.button(f"Confirm delete {holding['symbol']}?", key=f"confirm_delete_{holding['symbol']}"):
                        try:
                            portfolio.remove_holding(holding['symbol'])
                            st.success(f"Removed {holding['symbol']} from portfolio")
                            # Update portfolio data with force_refresh=True
                            portfolio_data = run_async(portfolio.get_portfolio_data(force_refresh=True))
                            st.session_state.portfolio_data = portfolio_data
                            time.sleep(0.5)  # Add a small delay before rerun
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            
            st.markdown("---")

def display_market_analysis():
    st.title("Market Analysis")
    
    try:
        # Get portfolio data and analysis
        portfolio = CryptoPortfolio()
        portfolio_data = run_async(get_portfolio_data())
        
        if not portfolio_data:
            st.error("Failed to fetch portfolio data. Please try again.")
            return
            
        analysis = portfolio.get_market_analysis(portfolio_data)
        
        # Display the analysis
        st.markdown(analysis)
        
        # Add rebalancing button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Execute Rebalancing", help="Automatically create transactions to achieve 70-30 allocation"):
                auto_rebalance(portfolio_data)
    
    except Exception as e:
        st.error(f"Error in market analysis: {str(e)}")
        return

def calculate_target_allocations(portfolio_data: dict) -> dict:
    """Calculate target allocations for each asset based on the 70-30 strategy"""
    total_value = portfolio_data['total_value_brl']
    holdings = portfolio_data['holdings']
    
    # Separate stablecoins and crypto
    stablecoins = [h for h in holdings if h['symbol'] in ['USDT', 'MUSD']]
    cryptos = [h for h in holdings if h['symbol'] not in ['USDT', 'MUSD']]
    
    # Calculate current values
    current_stable_value = sum(h['value_brl'] for h in stablecoins)
    current_crypto_value = sum(h['value_brl'] for h in cryptos)
    
    # Target values (70-30 split)
    target_crypto_value = total_value * 0.70
    target_stable_value = total_value * 0.30
    
    # Calculate target allocations for individual cryptos
    # Maintain relative proportions within crypto allocation
    crypto_allocations = {}
    if current_crypto_value > 0:
        for crypto in cryptos:
            current_weight = crypto['value_brl'] / current_crypto_value
            target_value = target_crypto_value * current_weight
            crypto_allocations[crypto['symbol']] = {
                'current_value': crypto['value_brl'],
                'target_value': target_value,
                'difference': target_value - crypto['value_brl'],
                'price_brl': crypto['price_brl']
            }
    
    # Stablecoin allocation
    stable_allocations = {}
    for stable in stablecoins:
        stable_allocations[stable['symbol']] = {
            'current_value': stable['value_brl'],
            'target_value': target_stable_value,
            'difference': target_stable_value - stable['value_brl'],
            'price_brl': stable['price_brl']
        }
    
    return {
        'total_value': total_value,
        'crypto_allocations': crypto_allocations,
        'stable_allocations': stable_allocations,
        'current_percentages': {
            'crypto': (current_crypto_value / total_value) * 100,
            'stable': (current_stable_value / total_value) * 100
        }
    }

def auto_rebalance(portfolio_data: dict):
    """Execute portfolio rebalancing based on the 70-30 strategy by directly updating holdings"""
    try:
        # Calculate target allocations
        allocations = calculate_target_allocations(portfolio_data)
        
        # Check if rebalancing is needed (using 2.5% threshold)
        current_stable_pct = allocations['current_percentages']['stable']
        if abs(current_stable_pct - 30) <= 2.5:
            st.info(f"Portfolio is already well balanced! Current allocation: {current_stable_pct:.1f}% stablecoins")
            return
        
        # Get stablecoin info (using USDT)
        stable_symbol = 'USDT'
        stable_info = next(
            (h for h in portfolio_data['holdings'] if h['symbol'] == stable_symbol),
            None
        )
        if not stable_info:
            st.error(f"No {stable_symbol} holdings found! Cannot rebalance without {stable_symbol}.")
            return

        total_value = portfolio_data['total_value_brl']
        target_stable_value = total_value * 0.30  # 30% in stablecoins
        target_crypto_value = total_value * 0.70  # 70% in crypto

        # Create a new portfolio instance for rebalancing
        portfolio = CryptoPortfolio()
        
        # Calculate and update new holdings
        for holding in portfolio_data['holdings']:
            symbol = holding['symbol']
            price_brl = holding['price_brl']
            
            if symbol == stable_symbol:
                # Calculate new stablecoin amount
                new_amount = target_stable_value / price_brl
            else:
                # Calculate new crypto amount maintaining relative proportions
                current_crypto_value = sum(h['value_brl'] for h in portfolio_data['holdings'] if h['symbol'] != stable_symbol)
                if current_crypto_value > 0:
                    crypto_weight = holding['value_brl'] / current_crypto_value
                    target_value = target_crypto_value * crypto_weight
                    new_amount = target_value / price_brl
                else:
                    new_amount = 0

            # Update holding with new amount
            portfolio.update_holdings(symbol, new_amount)
        
        # Update portfolio data after rebalancing
        st.session_state.portfolio = portfolio
        st.session_state.portfolio_data = run_async(portfolio.get_portfolio_data(force_refresh=True))
        
        st.success(f"Portfolio successfully rebalanced from {current_stable_pct:.1f}% stablecoins to target 30% allocation.")
        time.sleep(0.5)  # Add a small delay before rerun
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during rebalancing: {str(e)}")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portfolio Overview",
    "Edit Holdings",
    "Market Analysis",
    "Market News",
    "Rebalancing"
])

with tab1:
    display_portfolio_overview()

with tab2:
    edit_holdings()

with tab3:
    display_market_analysis()

with tab4:
    display_tradingview_widget()

with tab5:
    auto_rebalance(update_portfolio_data())

# Sidebar
with st.sidebar:
    st.title("Controls")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit by FSTech | Data from CoinMarketCap | Analysis by OpenAI"
)
