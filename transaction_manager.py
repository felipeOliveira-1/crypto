import json
from datetime import datetime
import os

class TransactionManager:
    def __init__(self, history_file='transaction_history.json'):
        self.history_file = history_file
        self.transactions = self._load_history()

    def _load_history(self):
        """Load transaction history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_history(self):
        """Save transaction history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.transactions, f, indent=4)

    def add_transaction(self, symbol: str, amount: float, price_brl: float, 
                       transaction_type: str, notes: str = ""):
        """Add a new transaction to history"""
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol.upper(),
            'amount': amount,
            'price_brl': price_brl,
            'total_brl': price_brl * amount,
            'type': transaction_type,
            'notes': notes
        }
        self.transactions.append(transaction)
        self._save_history()
        return transaction

    def get_transactions(self, symbol=None, transaction_type=None):
        """Get filtered transactions"""
        filtered = self.transactions
        if symbol:
            filtered = [t for t in filtered if t['symbol'] == symbol.upper()]
        if transaction_type:
            filtered = [t for t in filtered if t['type'] == transaction_type]
        return filtered

    def get_asset_cost_basis(self, symbol):
        """Calculate cost basis for an asset"""
        transactions = self.get_transactions(symbol)
        total_amount = 0
        total_cost = 0
        
        for t in transactions:
            if t['type'] == 'buy':
                total_amount += t['amount']
                total_cost += t['total_brl']
            elif t['type'] == 'sell':
                total_amount -= t['amount']
                total_cost -= (total_cost / (total_amount + t['amount'])) * t['amount']
        
        return total_cost if total_amount > 0 else 0
