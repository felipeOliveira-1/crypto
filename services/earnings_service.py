from typing import Dict, List
from datetime import datetime

class EarningsService:
    @staticmethod
    def calculate_earnings(portfolio_data: Dict) -> Dict:
        """Calculate daily and accumulated earnings"""
        # Initial investment values (based on transaction history)
        initial_values = {
            'LTC': {
                'amount': 0.03922,  # Total amount from transactions
                'value': 10.00 * 4  # Aproximadamente R$10 por transação
            },
            'BTC': {
                'amount': 0.00004615,
                'value': 10.00
            },
            'LINK': {
                'amount': 0.20557,
                'value': 10.00 * 2
            },
            'ETH': {
                'amount': 0.00124575,
                'value': 10.00 * 3
            },
            'UNI': {
                'amount': 0.31159,
                'value': 10.00 * 4
            }
        }
        
        # Initialize result
        result = {
            'total_balance': portfolio_data['total_value_brl'],
            'daily_earnings': [],
            'accumulated_earnings': [],
            'total_daily': 0,
            'total_accumulated': 0
        }
        
        # Calculate earnings for each holding
        for holding in portfolio_data['holdings']:
            symbol = holding['symbol']
            current_value = holding['value_brl']
            price_change_24h = holding['percent_change_24h']
            
            # Calculate daily earnings based on 24h price change
            daily_value = (price_change_24h / 100) * current_value
            
            # Calculate accumulated earnings
            if symbol in initial_values:
                initial_value = initial_values[symbol]['value']
                acc_value = current_value - initial_value
            elif symbol == 'MUSD':  # Manter os valores fixos para MUSD
                acc_value = 0.55
                daily_value = -0.37
            else:
                # Para qualquer outro símbolo não listado
                acc_value = daily_value
            
            result['daily_earnings'].append({
                'symbol': symbol,
                'value': daily_value
            })
            
            result['accumulated_earnings'].append({
                'symbol': symbol,
                'value': acc_value
            })
            
            result['total_daily'] += daily_value
            result['total_accumulated'] += acc_value
        
        return result
