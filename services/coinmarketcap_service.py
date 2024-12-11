import os
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional

class CoinMarketCapService:
    def __init__(self):
        self.api_key = os.getenv('CMC_API_KEY')
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.session = None
        self._cache = {}
        self._cache_time = {}
        self.CACHE_DURATION = timedelta(minutes=10)

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        if cache_key in self._cache:
            last_update = self._cache_time.get(cache_key)
            if last_update and datetime.now() - last_update < self.CACHE_DURATION:
                return self._cache[cache_key]
        return None

    async def _set_cached_data(self, cache_key: str, data: Dict):
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now()

    async def get_market_data(self, symbols: list) -> Dict:
        """Fetch market data for given symbols including USD/BRL rate"""
        cache_key = f"market_data_{','.join(sorted(symbols))}"
        cached_data = await self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        await self._ensure_session()
        
        # Always include USDT for USD/BRL rate if not present
        if 'USDT' not in symbols:
            symbols = symbols + ['USDT']
        
        symbols_str = ','.join(symbols)
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
        params = {
            'symbol': symbols_str,
            'convert': 'BRL'
        }

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._set_cached_data(cache_key, data['data'])
                    return data['data']
                else:
                    print(f"Error fetching market data: {response.status}")
                    return {}
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def __del__(self):
        """Ensure session is closed on object destruction"""
        if self.session and not self.session.closed:
            import asyncio
            asyncio.run(self.close())
