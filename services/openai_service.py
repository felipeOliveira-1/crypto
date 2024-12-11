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
            # Format the analysis request using template data
            system_content = template_data['system_template'].format(
                current_time=portfolio_data.get('timestamp', 'N/A')
            )
            
            user_content = template_data['user_template'].format(
                portfolio_value=portfolio_data.get('total_value_brl', 0),
                holdings=portfolio_data.get('holdings', []),
                changes_24h=portfolio_data.get('weighted_24h_change', 0),
                changes_7d=portfolio_data.get('weighted_7d_change', 0)
            )

            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating market analysis: {e}")
            return "Unable to generate market analysis at this time."
