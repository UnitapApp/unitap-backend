from django.template import Template, Context
from telegram.bot import BaseTelegramMessageHandler
from telebot import types
from faucet.models import Faucet

gastap_text = """
*Gas Tokens Availability* ⛽

Here are the available chains for claiming gas tokens:

{% for faucet in faucets %}
🔵 *{{ faucet.chain.chain_name }}*  
Max Claim Amount: {{ faucet.max_claim_amount }}  
Available for: {% if faucet.is_one_time_claim %}One Time{% else %}Weekly{% endif %}

{% if faucet.has_enough_funds %}
🟢 *Status:* Available  
Fuel Level: {{ faucet.fuel_level }}%
{% else %}
🔴 *Status:* Out of Balance
{% endif %}

{% endfor %}

Remember: You need BrightID verification to claim your tokens.
"""


class GastapStatsHandler(BaseTelegramMessageHandler):
    message = "Stats of gastap"

    def handler(self, message: types.Message):
        faucets = Faucet.objects.filter(is_active=True, show_in_gastap=True)

        # Prepare the template
        template = Template(gastap_text)
        context = Context({"faucets": faucets})

        rendered_message = template.render(context)

        self.messenger.reply_to(message, text=rendered_message)
