# Crypto Portfolio Tracker with AI Analysis

An advanced cryptocurrency portfolio tracking system built with Streamlit that combines real-time market data from CoinMarketCap with AI-powered analysis using OpenAI's GPT-4o model. The system provides detailed portfolio management, transaction tracking, and market analysis in Brazilian Real (BRL).

## Features

### Portfolio Management
- Real-time cryptocurrency price tracking in BRL
- Interactive portfolio composition pie chart
- Detailed holdings table with 24h changes
- Total portfolio value and performance metrics
- Edit holdings through a user-friendly interface

### Transaction Management
- Record buy/sell transactions
- Filter transaction history by cryptocurrency
- Automatic portfolio updates based on transactions

### AI Analysis
- GPT-4o powered market analysis
- Auto-refresh option for real-time insights
- Comprehensive market trends and recommendations
- Risk assessment and action items

### User Interface
- Clean and modern Streamlit interface
- Responsive design with dark mode
- Interactive charts and tables
- Real-time data updates

## Project Structure

```
crypto/
├── app.py                      # Main Streamlit application
├── crypto_portfolio_v2.py      # Portfolio management logic
├── transaction_manager.py      # Transaction handling
├── prompts/
│   ├── system_prompt.xml      # System role definition
│   └── user_prompt_template.xml # Analysis request template
├── .env                       # API key configuration
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

2. Use the interface to:
   - View your portfolio overview
   - Add new transactions
   - Edit cryptocurrency holdings
   - Generate AI analysis
   - Track transaction history

## Dependencies

- `streamlit==1.29.0`: Web application framework
- `plotly==5.18.0`: Interactive charts
- `pandas==2.1.3`: Data manipulation
- `openai==1.3.7`: AI analysis capabilities
- `python-dotenv==1.0.0`: Environment configuration
- `requests`: API communication
- `matplotlib`: Dataframe styling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only. Cryptocurrency investments carry high risk. Always do your own research before making investment decisions.

## Acknowledgments

- CoinMarketCap API for real-time cryptocurrency data
- OpenAI for GPT-4o powered analysis
- Streamlit for the amazing web framework
