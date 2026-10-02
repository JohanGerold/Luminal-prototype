from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from waitress import serve
from aap.runs import recover_interrupted


class Command(BaseCommand):
    help = "Start the single local AAP process; mark unfinished historical runs interrupted."

    def handle(self, *args, **options):
        recover_interrupted()
        self.stdout.write("AAP ready at http://127.0.0.1:8001 (single process)")
        serve(get_wsgi_application(), host="127.0.0.1", port=8001, threads=6)
