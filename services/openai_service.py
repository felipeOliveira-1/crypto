import os
import httpx
from openai import OpenAI
from typing import Dict

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.proxies = os.getenv('PROXIES')
        
        # Initialize OpenAI client with custom httpx client
        transport = httpx.HTTPTransport(proxy=self.proxies)
        http_client = httpx.Client(transport=transport, verify=False)
        self.client = OpenAI(
            api_key=self.api_key,
            http_client=http_client
        )

    def generate_market_analysis(self, portfolio_data: Dict, template_data: Dict) -> str:
        """Generate market analysis using OpenAI"""
        try:
            # Calculate rebalancing data using the new allocation logic
            total_value = portfolio_data['total_value_brl']
            holdings = portfolio_data['holdings']
            
            # Separate stablecoins and crypto
            stablecoins = [h for h in holdings if h['symbol'] in ['USDT', 'MUSD']]
            cryptos = [h for h in holdings if h['symbol'] not in ['USDT', 'MUSD']]
            
            current_stable_value = sum(h['value_brl'] for h in stablecoins)
            current_crypto_value = sum(h['value_brl'] for h in cryptos)
            
            # Calculate target values and deviations
            target_crypto_value = total_value * 0.70
            target_stable_value = total_value * 0.30
            
            # Format holdings data with detailed allocation analysis
            holdings_text = "DETALHAMENTO DOS ATIVOS:\n"
            
            # Group assets by type for better analysis
            holdings_text += "\nCRYPTOCURRENCIES:\n"
            crypto_total = current_crypto_value
            for crypto in sorted(cryptos, key=lambda x: x['value_brl'], reverse=True):
                allocation_pct = (crypto['value_brl'] / total_value) * 100
                relative_crypto_pct = (crypto['value_brl'] / crypto_total * 100) if crypto_total > 0 else 0
                
                holdings_text += f"- {crypto['symbol']}:\n"
                holdings_text += f"  * Quantidade: {crypto['amount']:.8f}\n"
                holdings_text += f"  * Valor: R$ {crypto['value_brl']:.2f}\n"
                holdings_text += f"  * Alocação Total: {allocation_pct:.1f}%\n"
                holdings_text += f"  * Alocação Relativa (dentro dos 70%): {relative_crypto_pct:.1f}%\n"
                holdings_text += f"  * Variação 24h: {crypto['percent_change_24h']:.2f}%\n"
                holdings_text += f"  * Variação 7d: {crypto['percent_change_7d']:.2f}%\n\n"
            
            holdings_text += "\nSTABLECOINS:\n"
            for stable in stablecoins:
                allocation_pct = (stable['value_brl'] / total_value) * 100
                holdings_text += f"- {stable['symbol']}:\n"
                holdings_text += f"  * Quantidade: {stable['amount']:.8f}\n"
                holdings_text += f"  * Valor: R$ {stable['value_brl']:.2f}\n"
                holdings_text += f"  * Alocação: {allocation_pct:.1f}%\n\n"
            
            # Add comprehensive rebalancing analysis
            holdings_text += f"\nANÁLISE DE BALANCEAMENTO (Estratégia 70-30):\n"
            crypto_allocation = (current_crypto_value/total_value)*100
            stable_allocation = (current_stable_value/total_value)*100
            
            holdings_text += f"- Valor Total do Portfólio: R$ {total_value:.2f}\n"
            holdings_text += f"- Alocação Atual em Crypto: R$ {current_crypto_value:.2f} ({crypto_allocation:.1f}%)\n"
            holdings_text += f"- Alocação Atual em Stablecoins: R$ {current_stable_value:.2f} ({stable_allocation:.1f}%)\n\n"
            
            # Calculate detailed rebalancing needs
            crypto_difference = target_crypto_value - current_crypto_value
            stable_difference = target_stable_value - current_stable_value
            
            holdings_text += f"ANÁLISE DE REBALANCEAMENTO:\n"
            
            # Overall portfolio status
            if abs(stable_allocation - 30) <= 1:
                holdings_text += "- STATUS: Portfólio bem balanceado (dentro da margem de 1%)\n"
            else:
                holdings_text += f"- STATUS: Rebalanceamento necessário (desvio de {abs(stable_allocation - 30):.1f}%)\n"
            
            # Detailed adjustments needed
            if abs(crypto_difference) > 1:
                if crypto_difference > 0:
                    holdings_text += f"- Cryptos: Necessário aumentar exposição em R$ {crypto_difference:.2f}\n"
                    
                    # Add relative adjustment suggestions
                    if cryptos:
                        holdings_text += "  Sugestão de distribuição:\n"
                        for crypto in cryptos:
                            weight = crypto['value_brl'] / current_crypto_value if current_crypto_value > 0 else 0
                            suggested_increase = crypto_difference * weight
                            holdings_text += f"  * {crypto['symbol']}: +R$ {suggested_increase:.2f}\n"
                else:
                    holdings_text += f"- Cryptos: Necessário reduzir exposição em R$ {abs(crypto_difference):.2f}\n"
                    
                    # Add relative reduction suggestions
                    if cryptos:
                        holdings_text += "  Sugestão de redução:\n"
                        for crypto in cryptos:
                            weight = crypto['value_brl'] / current_crypto_value
                            suggested_reduction = abs(crypto_difference) * weight
                            holdings_text += f"  * {crypto['symbol']}: -R$ {suggested_reduction:.2f}\n"
            
            if abs(stable_difference) > 1:
                if stable_difference > 0:
                    holdings_text += f"- Stablecoins: Necessário aumentar em R$ {stable_difference:.2f}\n"
                else:
                    holdings_text += f"- Stablecoins: Necessário reduzir em R$ {abs(stable_difference):.2f}\n"
            
            # Format the analysis request using template data
            system_content = template_data['system_template'].format(
                current_time=portfolio_data.get('timestamp', 'N/A')
            )
            
            user_content = template_data['user_template'].format(
                portfolio_value=portfolio_data.get('total_value_brl', 0),
                changes_24h=portfolio_data.get('weighted_24h_change', 0),
                changes_7d=portfolio_data.get('weighted_7d_change', 0),
                holdings=holdings_text
            )

            # Make API call with specific parameters for analysis
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.13,
                max_tokens=1500,
                presence_penalty=0.3,
                frequency_penalty=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating market analysis: {e}")
            return "Unable to generate market analysis at this time. Please try again later."
