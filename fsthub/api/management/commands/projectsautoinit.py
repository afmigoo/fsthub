from typing import List, Set
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.conf import settings
from api.models import ProjectMetadata, FstType, FstTypeRelation, FstLanguage, FstLanguageRelation

from project_reader import get_all_fsts, get_projects
from hfst_adaptor.call import call_metadata_extractor
from hfst_adaptor.parse import parse_metadata
from hfst_adaptor.exceptions import HfstException

class Command(BaseCommand):
    help = "Read projects from HFST_CONTENT_ROOT and init missing ones in the DB"
    type_markers = {
        'transliterator': ['2', '_to_'],
        'generator': ['gen_', '_gen', 'generator'],
        'analyzer': ['ana_', '_ana', 'anal_', '_anal', 'analyzer'],
    }

    def detect_autotypes(self, file_path: str) -> List[str]:
        types = []
        file_name = Path(file_path).name
        for k, markers in self.type_markers.items():
            for m in markers:
                if m in file_name and not k in types:
                    types.append(k)
                    break
        return types
    
    def detect_language(self, file_name: str) -> str:
        try:
            metadata = call_metadata_extractor(settings.HFST_CONTENT_ROOT / file_name)
        except HfstException as e:
            self.stdout.write(
                self.style.WARNING(f"Failed to read metadata: `{file_name}`: {e}")
            )
            return
        parsed = parse_metadata(metadata, lower_keys=True)
        language = None
        for lang_key in settings.HFST_METADATA_LANG_KEYS:
            if lang_key in parsed:
                language = parsed[lang_key]
                break
        return language
    
    def add_lang_relation(self, lang_name: str, file_name: str) -> None:
        lang_name = lang_name.lower()
        lang_obj, lang_created = FstLanguage.objects.get_or_create(name=lang_name)
        if lang_created:
            self.stdout.write(
                self.style.SUCCESS(f"[CREATED] language `{lang_name}`")
            )
        _, relation_created = FstLanguageRelation.objects.get_or_create(fst_file=file_name, language=lang_obj)
        if relation_created:
            self.stdout.write(
                self.style.SUCCESS(f"[CREATED] lang relation `{file_name}` -> `{lang_name}`")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"[ALREADY EXISTS] lang relation `{file_name}` -> `{lang_name}`")
            )
    
    def add_type_relation(self, type_name: str, file_name: str) -> None:
        type_obj, type_created = FstType.objects.get_or_create(name=type_name)
        if type_created:
            self.stdout.write(
                self.style.SUCCESS(f"[CREATED] type `{type_name}`")
            )
        _, relation_created = FstTypeRelation.objects.get_or_create(fst_file=file_name, type=type_obj)
        if relation_created:
            self.stdout.write(
                self.style.SUCCESS(f"[CREATED] type relation `{file_name}` -> `{type_name}`")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"[ALREADY EXISTS] type relation `{file_name}` -> `{type_name}`")
            )

    def init_projects(self):
        filesystem_projects = set(get_projects())
        db_projects = (x.directory for x in ProjectMetadata.objects.only('directory').all())
        db_missing = filesystem_projects.difference(db_projects)
        if len(db_missing) == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No new projects found')
            )
            return
        for proj in db_missing:
            ProjectMetadata.objects.create(directory=proj)
            self.stdout.write(
                self.style.SUCCESS(f"[CREATED] project '{proj}'")
            )

    def init_transducers(self):
        filesystem_transducers = get_all_fsts()
        if len(filesystem_transducers) == 0:
            self.stdout.write(
                self.style.NOTICE(f'No transducers found')
            )
            return
        for fst in filesystem_transducers:
            for t in self.detect_autotypes(fst):
                self.add_type_relation(t, fst)
            lang = self.detect_language(fst)
            if lang:
                self.add_lang_relation(lang, fst)

    def handle(self, *args, **options):
        self.init_projects()
        self.init_transducers()
