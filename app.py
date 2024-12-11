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
import os

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
    """Execute automatic rebalancing transactions based on the 70-30 strategy"""
    try:
        # Calculate target allocations
        allocations = calculate_target_allocations(portfolio_data)
        
        # Check if rebalancing is needed (using 1% threshold)
        current_stable_pct = allocations['current_percentages']['stable']
        if abs(current_stable_pct - 30) <= 1:
            st.info("Portfolio is already well balanced!")
            return
        
        # Get stablecoin info
        stable_info = next(
            (alloc for symbol, alloc in allocations['stable_allocations'].items()),
            None
        )
        if not stable_info:
            st.error("No stablecoin holdings found! Cannot rebalance without USDT or MUSD.")
            return
        
        # Sort crypto allocations by absolute difference
        crypto_trades = sorted(
            [
                {'symbol': symbol, **alloc}
                for symbol, alloc in allocations['crypto_allocations'].items()
            ],
            key=lambda x: abs(x['difference']),
            reverse=True
        )
        
        if not crypto_trades:
            st.error("No crypto holdings found to rebalance!")
            return
        
        # Execute trades
        for trade in crypto_trades:
            if abs(trade['difference']) <= 1:  # Skip small adjustments
                continue
                
            if trade['difference'] < 0:  # Need to sell crypto
                # Calculate amount to sell
                amount_to_sell = abs(trade['difference']) / trade['price_brl']
                
                # Add sell transaction for crypto
                notes = f"Rebalancing: Selling {trade['symbol']} to adjust portfolio allocation"
                st.session_state.transaction_manager.add_transaction(
                    transaction_type='SELL',
                    symbol=trade['symbol'],
                    amount=amount_to_sell,
                    price_brl=trade['price_brl'],
                    notes=notes
                )
                
                # Add buy transaction for stablecoin
                notes = f"Rebalancing: Buying USDT from {trade['symbol']} sale"
                st.session_state.transaction_manager.add_transaction(
                    transaction_type='BUY',
                    symbol='USDT',
                    amount=abs(trade['difference']) / stable_info['price_brl'],
                    price_brl=stable_info['price_brl'],
                    notes=notes
                )
            else:  # Need to buy crypto
                # Calculate amount to buy
                amount_to_buy = trade['difference'] / trade['price_brl']
                
                # Add sell transaction for stablecoin
                notes = f"Rebalancing: Selling USDT to buy {trade['symbol']}"
                st.session_state.transaction_manager.add_transaction(
                    transaction_type='SELL',
                    symbol='USDT',
                    amount=trade['difference'] / stable_info['price_brl'],
                    price_brl=stable_info['price_brl'],
                    notes=notes
                )
                
                # Add buy transaction for crypto
                notes = f"Rebalancing: Buying {trade['symbol']} to adjust portfolio allocation"
                st.session_state.transaction_manager.add_transaction(
                    transaction_type='BUY',
                    symbol=trade['symbol'],
                    amount=amount_to_buy,
                    price_brl=trade['price_brl'],
                    notes=notes
                )
        
        st.success(f"Rebalancing transactions executed successfully! Portfolio adjusted from {current_stable_pct:.1f}% stablecoins to target 30% allocation.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during rebalancing: {str(e)}")

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
    earnings_data = run_async(portfolio.get_earnings_data())
    
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
        portfolio_data = run_async(portfolio.get_portfolio_data())
        
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

def initialize_portfolio():
    """Create a new portfolio through the UI"""
    st.header("Initialize New Portfolio")
    
    # Warning about existing portfolio
    if os.path.exists('portfolio.json'):
        st.warning("⚠️ You already have an existing portfolio. Creating a new one will replace it.")
    
    # Initialize portfolio assets
    if 'portfolio_assets' not in st.session_state:
        st.session_state.portfolio_assets = []
    
    # Form for adding new assets
    with st.form(key='add_asset_form'):
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Asset Symbol (e.g., BTC, ETH)", key='new_asset_symbol').upper()
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, format="%f", key='new_asset_quantity')
        
        submit_asset = st.form_submit_button("Add Asset")
        
        if submit_asset and symbol and quantity > 0:
            # Validate symbol using CMC API
            portfolio = CryptoPortfolio()
            asyncio.run(portfolio.cmc_service.get_latest_quotes([symbol]))
            
            # Add to session state if valid
            asset = {'symbol': symbol, 'quantity': quantity}
            if asset not in st.session_state.portfolio_assets:
                st.session_state.portfolio_assets.append(asset)
            
            # Clear input fields
            st.session_state.new_asset_symbol = ''
            st.session_state.new_asset_quantity = 0.0
    
    # Display current assets
    if st.session_state.portfolio_assets:
        st.subheader("Current Assets")
        df = pd.DataFrame(st.session_state.portfolio_assets)
        st.dataframe(df)
        
        # Save portfolio button
        if st.button("Save Portfolio"):
            new_portfolio = {asset['symbol']: asset['quantity'] for asset in st.session_state.portfolio_assets}
            
            # Save to file
            portfolio = CryptoPortfolio()
            portfolio.portfolio = new_portfolio
            portfolio._save_portfolio()
            
            # Clear session state
            st.session_state.portfolio_assets = []
            
            st.success("✅ Portfolio saved successfully! Please refresh the page to see your new portfolio.")
    
    # Option to clear all assets
    if st.session_state.portfolio_assets:
        if st.button("Clear All Assets"):
            st.session_state.portfolio_assets = []
            st.experimental_rerun()

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Portfolio Overview",
    "Transaction History",
    "Add Transaction",
    "Edit Holdings",
    "Earnings",
    "AI Analysis",
    "TradingView Widget",
    "Initialize Portfolio"
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

with tab8:
    initialize_portfolio()

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
