from pathlib import Path
from typing import List, Union, Set
from django.conf import settings
from time import time

assert(isinstance(settings.HFST_CONTENT_ROOT, Path))
assert(settings.HFST_CONTENT_ROOT.is_dir())

class ProjectReader():
    root: Path = settings.HFST_CONTENT_ROOT
    __cached_projects: Set[str] = None
    __cached_fsts: Set[str] = None
    __last_updated: float = None
    update_interval: int = 60

    @classmethod
    def get_projects(cls) -> List[str]:
        cls._update_if_time()
        return list(cls.__cached_projects)
    
    @classmethod
    def get_fsts(cls) -> List[str]:
        cls._update_if_time()
        return list(cls.__cached_fsts)

    @classmethod
    def project_exists(cls, project: Union[str, Path]) -> bool:
        cls._update_if_time()
        if isinstance(project, str):
            return project in cls.__cached_projects
        else:
            return str(project) in cls.__cached_projects

    
    @classmethod
    def fst_exists(cls, transducer: Union[str, Path]) -> bool:
        cls._update_if_time()
        if isinstance(transducer, str):
            return transducer in cls.__cached_fsts
        else:
            return str(transducer) in cls.__cached_fsts
    
    @classmethod
    def _update_if_time(cls) -> None:
        now = time()
        if (cls.__last_updated is None or \
            now - cls.__last_updated > cls.update_interval):
            cls._read_projects()
            cls._read_fsts()
            cls.__last_updated = now
    
    @classmethod
    def _read_projects(cls) -> None:
        new_cache = set()
        for path in cls.root.iterdir():
            if path.is_dir():
                new_cache.add(str(path.relative_to(cls.root)))
        cls.__cached_projects = new_cache

    @classmethod
    def _read_fsts(cls) -> None:
        new_cache = set()
        for proj in cls.__cached_projects:
            proj_path = cls.root / proj
            if not proj_path.is_dir():
                continue
            for path in proj_path.iterdir():
                if path.is_file():
                    new_cache.add(str(path.relative_to(cls.root)))
        cls.__cached_fsts = new_cache
