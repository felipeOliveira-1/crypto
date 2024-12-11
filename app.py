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
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = CryptoPortfolio()

# Header
st.title("📈 Crypto Portfolio Tracker")

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
    
    return asyncio.run(coroutine)

def update_portfolio_data():
    """Update portfolio data and last update time"""
    with st.spinner('Updating portfolio data...'):
        st.session_state.last_update = datetime.now()
        return run_async(get_portfolio_data())

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
        
        # Check if rebalancing is needed (using 1% threshold)
        current_stable_pct = allocations['current_percentages']['stable']
        if abs(current_stable_pct - 30) <= 1:
            st.info("Portfolio is already well balanced!")
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
            st.session_state.portfolio.update_holdings(symbol, new_amount)
        
        st.success(f"Portfolio successfully rebalanced from {current_stable_pct:.1f}% stablecoins to target 30% allocation.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during rebalancing: {str(e)}")

def display_portfolio_overview():
    st.header("Portfolio Overview")
    portfolio_data = update_portfolio_data()
    
    if not portfolio_data['holdings']:
        st.info("No holdings found. Please add some holdings in the Edit Holdings tab.")
        return
    
    # Display total value and 24h change centered
    st.metric(
        "Total Portfolio Value",
        f"R$ {portfolio_data['total_value_brl']:,.2f}",
        f"{portfolio_data['weighted_24h_change']:+.2f}%",
        help="Total value of all holdings in Brazilian Real"
    )
    
    # Create pie chart of portfolio composition
    fig = go.Figure(data=[go.Pie(
        labels=[h['symbol'] for h in portfolio_data['holdings']],
        values=[h['value_brl'] for h in portfolio_data['holdings']],
        hole=.3
    )])
    fig.update_layout(title="Portfolio Composition")
    st.plotly_chart(fig)
    
    # Display holdings table
    holdings_df = pd.DataFrame(portfolio_data['holdings'])
    holdings_df = holdings_df[[
        'symbol', 'amount', 'price_brl', 'value_brl',
        'percent_change_24h', 'percent_change_7d'
    ]]
    holdings_df.columns = [
        'Symbol', 'Amount', 'Price (R$)', 'Value (R$)',
        '24h Change (%)', '7d Change (%)'
    ]
    
    # Format the dataframe using string formatting
    holdings_df = holdings_df.assign(**{
        'Price (R$)': [f'R$ {x:,.2f}' for x in holdings_df['Price (R$)']],
        'Value (R$)': [f'R$ {x:,.2f}' for x in holdings_df['Value (R$)']],
        '24h Change (%)': [f'{x:+.2f}%' for x in holdings_df['24h Change (%)']],
        '7d Change (%)': [f'{x:+.2f}%' for x in holdings_df['7d Change (%)']],
    })
    
    st.dataframe(
        holdings_df.style.apply(lambda x: ['background-color: #0f1117'] * len(x)),
        hide_index=True
    )

def edit_holdings():
    st.header("Edit Holdings")
    
    # Create a form for editing holdings
    portfolio = CryptoPortfolio()
    portfolio_data = run_async(portfolio.get_portfolio_data())
    
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
    st.header("Settings")
    
    if st.button("🔄 Update Values"):
        st.rerun()
    
    if st.session_state.last_update:
        st.write(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit by FSTech | Data from CoinMarketCap | Analysis by OpenAI"
)
