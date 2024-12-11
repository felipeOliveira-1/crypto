# Crypto Portfolio Tracker with AI Analysis

An advanced cryptocurrency portfolio tracking system built with Streamlit that combines real-time market data from CoinMarketCap with AI-powered analysis using OpenAI's GPT-4 model. The system provides detailed portfolio management, transaction tracking, and market analysis in Brazilian Real (BRL).

## Features

### Portfolio Management
- Real-time cryptocurrency price tracking in BRL
- Interactive portfolio composition donut chart
- Detailed holdings table with 24h and 7d changes
- Total portfolio value with dynamic color indicators
- Smart holdings management with existing/new crypto selection
- Automatic portfolio value updates

### Market Data
- Live cryptocurrency market data
- Price changes (24h and 7d)
- Volume and market cap information
- TradingView widgets integration
- Real-time market quotes

### AI Analysis
- GPT-4 powered market analysis
- Portfolio composition insights
- Market trends and recommendations
- Risk assessment and opportunities
- Automatic analysis refresh

### User Interface
- Modern dark theme design
- Responsive and interactive components
- Real-time data updates
- Improved error handling and feedback
- Streamlined editing interface

## Project Structure

```
crypto/
├── app.py                     # Main Streamlit application
├── crypto_portfolio_v2.py     # Portfolio management logic
├── services/                  # Service modules
│   ├── coinmarketcap_service.py  # CoinMarketCap API integration
│   ├── financial_service.py      # Financial calculations
│   ├── openai_service.py         # AI analysis
│   └── earnings_service.py       # Earnings calculations
├── config/                    # Configuration files
│   └── templates.json         # Analysis templates
├── .env                       # Environment configuration
└── requirements.txt           # Python dependencies
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd crypto
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   env\Scripts\activate     # Windows
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure API keys:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```env
     CMC_API_KEY=your_coinmarketcap_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Navigate through the tabs:
   - **Portfolio Overview**: View your total portfolio value and composition
   - **Edit Holdings**: Add new or update existing cryptocurrency holdings
   - **Market Analysis**: Get AI-powered insights about your portfolio
   - **Market Data**: View real-time market information
   - **Trading View**: Access TradingView widgets

3. Managing Holdings:
   - Select from existing cryptocurrencies or add new ones
   - Update amounts using precise input controls
   - Remove holdings with confirmation
   - View immediate portfolio updates

## Dependencies

- `streamlit`: Web application framework
- `plotly`: Interactive charts and visualizations
- `pandas`: Data manipulation and analysis
- `openai`: AI analysis integration
- `python-dotenv`: Environment configuration
- `requests`: API communication
- `asyncio`: Asynchronous operations

## Recent Updates

- Added smart holdings management with dropdown selection
- Improved error handling and user feedback
- Enhanced UI with dark theme and responsive components
- Added TradingView widgets integration
- Implemented precise amount controls
- Added confirmation dialogs for critical actions
- Fixed state management and refresh issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.