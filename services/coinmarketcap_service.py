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
        self.CACHE_DURATION = timedelta(minutes=5)  # Reduced cache time for more frequent updates

    async def _ensure_session(self):
        """Ensure we have an active session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)  # 10 seconds timeout
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if available and not expired"""
        if cache_key in self._cache:
            last_update = self._cache_time.get(cache_key)
            if last_update and datetime.now() - last_update < self.CACHE_DURATION:
                return self._cache[cache_key]
        return None

    async def _set_cached_data(self, cache_key: str, data: Dict):
        """Cache data with timestamp"""
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now()

    async def get_market_data(self, symbols: list) -> Dict:
        """
        Fetch market data for given symbols including USD/BRL rate
        Basic plan limitations:
        - 10,000 monthly call credits
        - 333 daily credits
        - 30 calls per minute
        - 1 convert option per call
        """
        try:
            # Check cache first
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
            
            # Basic plan only allows one convert option
            params = {
                'symbol': symbols_str,
                'convert': 'BRL',
                'skip_invalid': 'true'  # Skip invalid symbols instead of erroring
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data:
                        result = {}
                        for symbol in symbols:
                            if symbol in data['data']:
                                try:
                                    coin_data = data['data'][symbol]['quote']['BRL']
                                    result[symbol] = {
                                        'price_brl': coin_data['price'],
                                        'percent_change_24h': coin_data.get('percent_change_24h', 0),
                                        'percent_change_7d': coin_data.get('percent_change_7d', 0)
                                    }
                                except (KeyError, TypeError) as e:
                                    print(f"Error processing data for {symbol}: {e}")
                                    continue
                        
                        if result:
                            await self._set_cached_data(cache_key, result)
                            return result
                        else:
                            raise Exception("No valid data returned from API")
                    else:
                        raise Exception("Invalid API response format")
                elif response.status == 429:
                    raise Exception("Rate limit exceeded. Please try again later.")
                else:
                    error_msg = await response.text()
                    raise Exception(f"API Error: {response.status} - {error_msg}")
                    
        except asyncio.TimeoutError:
            print("Timeout while fetching market data")
            if cache_key in self._cache:
                return self._cache[cache_key]
            raise Exception("Timeout fetching market data and no cache available")
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            if cache_key in self._cache:
                return self._cache[cache_key]
            raise Exception(f"Failed to fetch market data: {str(e)}")

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

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
