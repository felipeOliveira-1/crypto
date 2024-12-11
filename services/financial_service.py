from typing import Dict, List
from decimal import Decimal

class FinancialService:
    @staticmethod
    def calculate_holdings_value(holdings: Dict[str, float], market_data: Dict) -> List[Dict]:
        """Calculate value and metrics for each holding"""
        holdings_summary = []
        
        for symbol, amount in holdings.items():
            if symbol == 'MUSD':  # Special handling for MUSD stablecoin
                usd_brl_rate = market_data.get('USDT', {}).get('price_brl', 5.0)
                holding = {
                    'symbol': symbol,
                    'amount': amount,
                    'price_brl': usd_brl_rate,
                    'value_brl': amount * usd_brl_rate,
                    'percent_change_24h': 0,
                    'percent_change_7d': 0,
                    'volume_24h': 0,
                    'market_cap': 0
                }
            elif symbol in market_data:
                crypto_data = market_data[symbol]
                price_brl = crypto_data['price_brl']
                holding = {
                    'symbol': symbol,
                    'amount': amount,
                    'price_brl': price_brl,
                    'value_brl': amount * price_brl,
                    'percent_change_24h': crypto_data['percent_change_24h'],
                    'percent_change_7d': crypto_data['percent_change_7d'],
                    'volume_24h': 0,  # These metrics are not critical for now
                    'market_cap': 0
                }
            else:
                print(f"Warning: No market data available for {symbol}")
                continue
                
            holdings_summary.append(holding)
            
        return holdings_summary

    @staticmethod
    def calculate_portfolio_metrics(holdings_summary: List[Dict]) -> Dict:
        """Calculate overall portfolio metrics"""
        total_value = sum(h['value_brl'] for h in holdings_summary)
        
        # Calculate portfolio composition percentages
        for holding in holdings_summary:
            holding['portfolio_percentage'] = (holding['value_brl'] / total_value * 100) if total_value > 0 else 0
            
        # Calculate weighted average changes
        if total_value > 0:
            weighted_24h_change = sum(
                h['percent_change_24h'] * (h['value_brl'] / total_value) 
                for h in holdings_summary
            )
            weighted_7d_change = sum(
                h['percent_change_7d'] * (h['value_brl'] / total_value) 
                for h in holdings_summary
            )
        else:
            weighted_24h_change = 0
            weighted_7d_change = 0
            
        return {
            'total_value_brl': total_value,
            'weighted_24h_change': weighted_24h_change,
            'weighted_7d_change': weighted_7d_change,
            'holdings': holdings_summary
        }
