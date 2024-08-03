import django
import os

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brightIDfaucet.settings')
django.setup()


from quiztap.models import Sponsor
from django.core.files import File



sponsor = Sponsor()

sponsor.name = "Optimism 2"
sponsor.link = "#12"
sponsor.image.save(os.path.basename("testasd"), File(open("image.png", "rb")), save=False)

print(sponsor.image.url)
# sponsor.save()