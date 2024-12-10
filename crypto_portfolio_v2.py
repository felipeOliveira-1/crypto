import os
import json
from datetime import datetime
from typing import Dict, List
import requests
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Load environment variables
load_dotenv()

class CryptoPortfolio:
    def __init__(self, portfolio=None):
        self.cmc_api_key = os.getenv('CMC_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.proxies = os.getenv('PROXIES')
        
        # Use provided portfolio or default values
        self.portfolio = portfolio or {
            'MUSD': 8.61847767,
            'UNI': 0.31159027,
            'ETH': 0.00124575,
            'BTC': 0.00004615,
            'LINK': 0.20556793,
            'LTC': 0.03921850
        }
        
        self.cmc_base_url = 'https://pro-api.coinmarketcap.com/v1'
        
        # Initialize OpenAI client with custom httpx client
        transport = httpx.HTTPTransport(proxy=self.proxies)
        http_client = httpx.Client(transport=transport, verify=False)
        self.openai_client = OpenAI(
            api_key=self.openai_api_key,
            http_client=http_client
        )
        
        # Load prompt templates
        self.system_prompt_template = self._load_prompt_template('system_prompt.xml')
        self.user_prompt_template = self._load_prompt_template('user_prompt_template.xml')

    def _load_prompt_template(self, filename: str) -> str:
        """Load a prompt template from the prompts directory"""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', filename)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading prompt template {filename}: {e}")
            return ""

    def update_holdings(self, symbol, amount):
        """Update or add a new cryptocurrency holding"""
        if amount <= 0:
            if symbol in self.portfolio:
                del self.portfolio[symbol]
        else:
            self.portfolio[symbol] = amount

    def get_crypto_data(self) -> Dict:
        """Fetch current price data for portfolio cryptocurrencies in BRL"""
        symbols = ','.join(self.portfolio.keys())
        url = f"{self.cmc_base_url}/cryptocurrency/quotes/latest"
        
        headers = {
            'X-CMC_PRO_API_KEY': self.cmc_api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'symbol': symbols,
            'convert': 'BRL'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto data: {e}")
            return {}

    def get_usd_brl_rate(self) -> float:
        """Get current USD/BRL exchange rate from CoinMarketCap"""
        url = f"{self.cmc_base_url}/cryptocurrency/quotes/latest"
        
        headers = {
            'X-CMC_PRO_API_KEY': self.cmc_api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'symbol': 'USDT',  # Using USDT as a proxy for USD
            'convert': 'BRL'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data['data']['USDT']['quote']['BRL']['price']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching USD/BRL rate: {e}")
            return 6.09  # Fallback value if API call fails

    def calculate_portfolio_value(self) -> Dict:
        """Calculate current portfolio value and holdings"""
        crypto_data = self.get_crypto_data()
        usd_brl_rate = self.get_usd_brl_rate()
        portfolio_summary = {
            'total_value_brl': 0,
            'holdings': []
        }

        for symbol, amount in self.portfolio.items():
            if symbol == 'MUSD':  # Special handling for MUSD stablecoin
                price_brl = usd_brl_rate  # Using current USD/BRL rate
                value_brl = amount * price_brl
                holding = {
                    'symbol': symbol,
                    'amount': amount,
                    'price_brl': price_brl,
                    'value_brl': value_brl,
                    'percent_change_24h': 0,  # Stablecoin, so no change
                    'percent_change_7d': 0,
                    'volume_24h': 0,
                    'market_cap': 0
                }
                portfolio_summary['holdings'].append(holding)
                portfolio_summary['total_value_brl'] += value_brl
            elif symbol in crypto_data:
                price_brl = crypto_data[symbol]['quote']['BRL']['price']
                value_brl = amount * price_brl
                
                holding = {
                    'symbol': symbol,
                    'amount': amount,
                    'price_brl': price_brl,
                    'value_brl': value_brl,
                    'percent_change_24h': crypto_data[symbol]['quote']['BRL']['percent_change_24h'],
                    'percent_change_7d': crypto_data[symbol]['quote']['BRL']['percent_change_7d'],
                    'volume_24h': crypto_data[symbol]['quote']['BRL']['volume_24h'],
                    'market_cap': crypto_data[symbol]['quote']['BRL']['market_cap']
                }
                
                portfolio_summary['holdings'].append(holding)
                portfolio_summary['total_value_brl'] += value_brl

        return portfolio_summary

    def get_market_analysis(self) -> str:
        """Get AI-powered market analysis and recommendations using advanced prompt engineering"""
        portfolio_data = self.calculate_portfolio_value()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare the prompts using templates
        system_prompt = {
            "role": "system",
            "content": self.system_prompt_template
        }

        user_prompt = {
            "role": "user",
            "content": self.user_prompt_template.format(
                timestamp=current_time,
                portfolio_data=json.dumps(portfolio_data, indent=2)
            )
        }

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for faster and more affordable analysis
                messages=[system_prompt, user_prompt],
                temperature=0.13,  # Lower temperature for higher precision and consistency
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting AI analysis: {str(e)}\n\nPlease check your OpenAI API key and try again."

    def display_portfolio(self):
        """Display portfolio information and AI analysis"""
        portfolio_data = self.calculate_portfolio_value()
        
        print("\n=== Crypto Portfolio Summary ===")
        print(f"Total Portfolio Value: R$ {portfolio_data['total_value_brl']:,.2f}")
        print("\nHoldings:")
        
        for holding in portfolio_data['holdings']:
            print(f"\n{holding['symbol']}:")
            print(f"  Amount: {holding['amount']}")
            print(f"  Price: R$ {holding['price_brl']:,.2f}")
            print(f"  Value: R$ {holding['value_brl']:,.2f}")
            print(f"  24h Change: {holding['percent_change_24h']:,.2f}%")
            print(f"  7d Change: {holding['percent_change_7d']:,.2f}%")
            print(f"  24h Volume: R$ {holding['volume_24h']:,.2f}")
            print(f"  Market Cap: R$ {holding['market_cap']:,.2f}")

        print("\n=== AI Market Analysis ===")
        analysis = self.get_market_analysis()
        print(analysis)


if __name__ == "__main__":
    portfolio = CryptoPortfolio()
    portfolio.display_portfolio()
