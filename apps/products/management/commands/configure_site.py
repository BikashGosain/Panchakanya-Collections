from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configure the production Django Site."

    def handle(self, *args, **options):
        domain = "panchakanya-collections.onrender.com"
        name = "Panchakanya Collections"

        site, created = Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={
                "domain": domain,
                "name": name,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created site: {site.domain}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated site: {site.domain}"))
