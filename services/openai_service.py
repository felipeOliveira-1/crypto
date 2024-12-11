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
            # Calculate rebalancing data
            total_value = portfolio_data['total_value_brl']
            current_usd = sum(h['value_brl'] for h in portfolio_data['holdings'] if h['symbol'] in ['USDT', 'MUSD'])
            current_crypto = total_value - current_usd
            
            # Format holdings data with allocation percentages
            holdings_text = "DETALHAMENTO DOS ATIVOS:\n"
            for holding in portfolio_data['holdings']:
                allocation_pct = (holding['value_brl'] / total_value) * 100
                holdings_text += f"- {holding['symbol']}:\n"
                holdings_text += f"  * Quantidade: {holding['amount']:.8f}\n"
                holdings_text += f"  * Valor: R$ {holding['value_brl']:.2f}\n"
                holdings_text += f"  * Alocação: {allocation_pct:.1f}%\n"
                holdings_text += f"  * Variação 24h: {holding['percent_change_24h']:.2f}%\n"
                holdings_text += f"  * Variação 7d: {holding['percent_change_7d']:.2f}%\n\n"

            # Add rebalancing status
            holdings_text += f"\nSTATUS DO REBALANCEAMENTO 70-30:\n"
            crypto_allocation = (current_crypto/total_value)*100
            usd_allocation = (current_usd/total_value)*100
            
            holdings_text += f"- Valor Total do Portfólio: R$ {total_value:.2f}\n"
            holdings_text += f"- Alocação Atual em Crypto: R$ {current_crypto:.2f} ({crypto_allocation:.1f}%)\n"
            holdings_text += f"- Alocação Atual em USD: R$ {current_usd:.2f} ({usd_allocation:.1f}%)\n\n"
            
            # Calculate rebalancing needs
            target_usd = total_value * 0.30
            target_crypto = total_value * 0.70
            usd_difference = target_usd - current_usd
            
            holdings_text += f"AJUSTES NECESSÁRIOS:\n"
            if abs(usd_difference) > 1:  # Using 1 BRL threshold
                if usd_difference > 0:
                    holdings_text += f"- Necessário vender R$ {abs(usd_difference):.2f} em crypto e comprar USD\n"
                else:
                    holdings_text += f"- Necessário vender R$ {abs(usd_difference):.2f} em USD e comprar crypto\n"
            else:
                holdings_text += "- Portfólio está bem balanceado (dentro da margem de R$ 1,00)\n"
            
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
