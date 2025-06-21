from typing import List, Set
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from api.models import ProjectMetadata, FstType, FstTypeRelation
from project_reader import ProjectReader

class Command(BaseCommand):
    help = "Read projects from HFST_CONTENT_ROOT and init missing ones in the DB"
    type_markers = {
        'transliterator': ['2', '_to_'],
        'generator': ['gen_', '_gen', 'generator'],
        'analyzer': ['ana_', '_ana', 'anal_', '_anal', 'analyzer'],
    }

    def detect_autotypes(self, file_name: str) -> List[str]:
        types = []
        for k, markers in self.type_markers.items():
            for m in markers:
                if m in file_name:
                    types.append(k)
                    break
        return types
    
    def add_type_relation(self, type_name: str, file_name: str) -> None:
        type_obj, type_created = FstType.objects.get_or_create(name=type_name)
        if type_created:
            self.stdout.write(
                self.style.SUCCESS(f"Created `{type_name}` type")
            )
        _, relation_created = FstTypeRelation.objects.get_or_create(fst_file=file_name, type=type_obj)
        if relation_created:
            self.stdout.write(
                self.style.SUCCESS(f"`{file_name}` marked as `{type_name}`")
            )

    def init_projects(self):
        filesystem_projects = set(ProjectReader.get_projects())
        db_projects = (x.directory for x in ProjectMetadata.objects.only('directory').all())
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
            ProjectMetadata.objects.create(directory=proj)
            self.stdout.write(
                self.style.SUCCESS(f"Added '{proj}'")
            )

    def init_transducers(self):
        filesystem_transducers = set(ProjectReader.get_all_fsts())
        for fst in filesystem_transducers:
            for t in self.detect_autotypes(fst):
                self.add_type_relation(t, fst)

    def handle(self, *args, **options):
        self.init_projects()
        self.init_transducers()
        
        

