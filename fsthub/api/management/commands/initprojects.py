from django.core.management.base import BaseCommand, CommandError
from api.models import FstProject
from project_reader import list_project_names

class Command(BaseCommand):
    help = "Read projects from HFST_CONTENT_ROOT and init missing ones in the DB"

    def handle(self, *args, **options):
        filesystem_projects = set(list_project_names())
        db_projects = (x.directory for x in FstProject.objects.only('directory').all())
        db_missing = filesystem_projects.difference(db_projects)
        if len(db_missing) == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No new projects found')
            )
            return
        self.stdout.write(
            self.style.SUCCESS(f'New projects found: {list(db_missing)}')
        )
        for proj in db_missing:
            FstProject.objects.create(directory=proj)
            self.stdout.write(
                self.style.SUCCESS(f'Added {proj}')
            )
