import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

class CoinMarketCapService:
    def __init__(self):
        api_key = os.getenv('CMC_API_KEY')
        if not api_key:
            raise ValueError("CMC_API_KEY environment variable is required")
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self.CACHE_DURATION = timedelta(minutes=5)

    async def _ensure_session(self):
        """Ensure we have an active session"""
        try:
            if self.session is None or self.session.closed:
                timeout = aiohttp.ClientTimeout(total=10)
                self.session = aiohttp.ClientSession(timeout=timeout)
        except Exception:
            # If there's any issue with the session, create a new one
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if available and not expired"""
        current_time = datetime.now()
        if cache_key in self._cache and cache_key in self._cache_time:
            last_update = self._cache_time[cache_key]
            if current_time - last_update < self.CACHE_DURATION:
                return self._cache[cache_key]
        return None

    async def get_market_data(self, symbols: list, force_refresh: bool = False) -> Dict:
        """
        Fetch market data for given symbols including USD/BRL rate
        
        Args:
            symbols: List of cryptocurrency symbols
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dict containing market data for requested symbols
            
        Raises:
            Exception: If API request fails or data is invalid
        """
        cache_key = f"market_data_{','.join(sorted(symbols))}"
        
        try:
            # Check cache first if not forcing refresh
            if not force_refresh:
                cached_data = await self._get_cached_data(cache_key)
                if cached_data is not None:
                    return cached_data

            await self._ensure_session()
            if self.session is None:
                raise RuntimeError("Failed to create session")
            
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
                'convert': 'BRL',
                'skip_invalid': 'true'
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' not in data:
                        raise ValueError("Invalid API response format")
                        
                    result = {}
                    for symbol in symbols:
                        symbol_data = data['data'].get(symbol)
                        if symbol_data:
                            try:
                                quote_data = symbol_data['quote']['BRL']
                                result[symbol] = {
                                    'price_brl': quote_data['price'],
                                    'percent_change_24h': quote_data.get('percent_change_24h', 0),
                                    'percent_change_7d': quote_data.get('percent_change_7d', 0)
                                }
                            except (KeyError, TypeError) as e:
                                print(f"Error processing data for {symbol}: {e}")
                                continue
                    
                    if not result:
                        raise ValueError("No valid data returned from API")
                        
                    # Only cache if not forcing refresh
                    if not force_refresh:
                        self._cache[cache_key] = result
                        self._cache_time[cache_key] = datetime.now()
                    return result
                    
                elif response.status == 429:
                    raise RuntimeError("Rate limit exceeded. Please try again later.")
                else:
                    error_msg = await response.text()
                    raise RuntimeError(f"API Error: {response.status} - {error_msg}")
                    
        except asyncio.TimeoutError:
            print("Timeout while fetching market data")
            if not force_refresh:
                cached_data = self._cache.get(cache_key)
                if cached_data is not None:
                    return cached_data
            raise TimeoutError("Timeout fetching market data and no cache available")
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            if not force_refresh:
                cached_data = self._cache.get(cache_key)
                if cached_data is not None:
                    return cached_data
            raise

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def cleanup(self):
        """Async cleanup method"""
        await self.close()

    def __del__(self):
        """Cleanup on object destruction"""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_running_loop()
                if not loop.is_closed():
                    loop.create_task(self.cleanup())
            except RuntimeError:
                # If no event loop is running, we can't do async cleanup
                pass
