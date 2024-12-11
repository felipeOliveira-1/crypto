import os
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
import asyncio

from services import CoinMarketCapService, FinancialService, OpenAIService, EarningsService

# Load environment variables
load_dotenv()

class CryptoPortfolio:
    def __init__(self, portfolio=None):
        # Initialize services
        self.cmc_service = CoinMarketCapService()
        self.financial_service = FinancialService()
        self.openai_service = OpenAIService()
        self.earnings_service = EarningsService()
        
        # Portfolio file paths
        self.portfolio_file = os.path.join(os.path.dirname(__file__), 'portfolio.json')
        self.daily_values_file = os.path.join(os.path.dirname(__file__), 'daily_values.json')
        
        # Load portfolio and daily values
        self.portfolio = self._load_portfolio() if portfolio is None else portfolio
        self.daily_values = self._load_daily_values()
        
        # Load templates
        self.templates = self._load_templates()

    def _load_portfolio(self) -> Dict:
        """Load portfolio from file or return default values"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
        
        return {
            'MUSD': 8.61847767,
            'UNI': 0.31159027,
            'ETH': 0.00124575,
            'BTC': 0.00004615,
            'LINK': 0.20556793,
            'LTC': 0.03921850
        }

    def _save_portfolio(self):
        """Save portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=4)
        except Exception as e:
            print(f"Error saving portfolio: {e}")

    def _load_templates(self) -> Dict:
        """Load analysis templates from JSON file"""
        template_path = os.path.join(os.path.dirname(__file__), 'config', 'templates.json')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {
                "system_template": "",
                "user_template": ""
            }

    def _load_daily_values(self) -> Dict:
        """Load daily portfolio values from file"""
        try:
            if os.path.exists(self.daily_values_file):
                with open(self.daily_values_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading daily values: {e}")
        return {'last_update': None, 'values': {}}

    def _save_daily_values(self):
        """Save daily portfolio values to file"""
        try:
            with open(self.daily_values_file, 'w') as f:
                json.dump(self.daily_values, f, indent=4)
        except Exception as e:
            print(f"Error saving daily values: {e}")

    def add_holding(self, symbol: str, amount: float) -> None:
        """Add a new cryptocurrency holding"""
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")
        
        symbol = symbol.strip().upper()
        if symbol in self.portfolio:
            raise ValueError(f"Symbol {symbol} already exists in portfolio")
            
        self.portfolio[symbol] = float(amount)
        self._save_portfolio()

    def update_holdings(self, symbol: str, amount: float) -> None:
        """Update or add a new cryptocurrency holding"""
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")
            
        symbol = symbol.strip().upper()
        if symbol not in self.portfolio:
            raise ValueError(f"Symbol {symbol} not found in portfolio")
            
        if amount <= 0:
            del self.portfolio[symbol]
        else:
            self.portfolio[symbol] = float(amount)
        self._save_portfolio()

    def remove_holding(self, symbol: str) -> None:
        """Remove a cryptocurrency holding"""
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
            
        symbol = symbol.strip().upper()
        if symbol not in self.portfolio:
            raise ValueError(f"Symbol {symbol} not found in portfolio")
            
        del self.portfolio[symbol]
        self._save_portfolio()

    async def get_portfolio_data(self) -> Dict:
        """Get current portfolio data with market information"""
        # Get market data for all portfolio symbols
        market_data = await self.cmc_service.get_market_data(list(self.portfolio.keys()))
        
        # Calculate holdings values and metrics
        holdings_summary = self.financial_service.calculate_holdings_value(
            self.portfolio, 
            market_data
        )
        
        # Calculate overall portfolio metrics
        portfolio_metrics = self.financial_service.calculate_portfolio_metrics(holdings_summary)
        
        # Add timestamp
        portfolio_metrics['timestamp'] = datetime.now().isoformat()
        
        return portfolio_metrics

    async def get_earnings_data(self) -> Dict:
        """Get earnings data for the portfolio"""
        portfolio_data = await self.get_portfolio_data()
        return self.earnings_service.calculate_earnings(portfolio_data)

    def get_market_analysis(self, portfolio_data: Dict) -> str:
        """Generate market analysis for the current portfolio"""
        return self.openai_service.generate_market_analysis(
            portfolio_data,
            self.templates
        )

    async def close(self):
        """Close all service connections"""
        await self.cmc_service.close()

    def __del__(self):
        """Cleanup on object destruction"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                asyncio.run(self.close())
        except Exception:
            pass  # Suppress cleanup errors during shutdown

    def display_portfolio(self):
        """Display portfolio information and AI analysis"""
        portfolio_data = asyncio.run(self.get_portfolio_data())
        analysis = self.get_market_analysis(portfolio_data)
        
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
        print(analysis)


if __name__ == "__main__":
    portfolio = CryptoPortfolio()
    portfolio.display_portfolio()
