from pathlib import Path
from typing import List, Union, FrozenSet, Generator, Dict
from django.conf import settings
from itertools import chain
from time import time

assert(isinstance(settings.HFST_CONTENT_ROOT, Path))
assert(settings.HFST_CONTENT_ROOT.is_dir())

class ProjectReader():
    """
    TODO: Docs
    """
    root: Path = settings.HFST_CONTENT_ROOT
    __cached_projects: Dict[str, FrozenSet[str]]
    __last_updated: float = None
    update_interval: int = 60

    @classmethod
    def get_projects(cls) -> Generator[str, None, None]:
        cls._update_if_time()
        return (key for key in cls.__cached_projects)
    
    @classmethod
    def get_all_fsts(cls) -> Generator[str, None, None]:
        cls._update_if_time()
        pointer = cls.__cached_projects
        for key in pointer:
            for fst in pointer[key]:
                yield fst

    @classmethod
    def get_fsts(cls, project: str) -> Generator[str, None, None]:
        cls._update_if_time()
        pointer = cls.__cached_projects
        if not project in pointer:
            raise KeyError(f'Project {project} does not exist in cache')
        return (fst for fst in pointer[project])

    @classmethod
    def get_project_count(cls) -> int:
        cls._update_if_time()
        if cls.__cached_projects is None:
            return 0
        return len(cls.__cached_projects)
    
    @classmethod
    def get_fst_count(cls) -> int:
        cls._update_if_time()
        pointer = cls.__cached_projects
        if pointer is None:
            return 0
        return sum(len(pointer[key])
                   for key in pointer)

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
        pointer = cls.__cached_projects
        if isinstance(transducer, Path):
            transducer = str(transducer)
        parts = transducer.split('/', maxsplit=1)
        if len(parts) < 2:
            return False
        return parts[0] in pointer and \
               transducer in pointer[parts[0]]

    @classmethod
    def _update_if_time(cls) -> None:
        now = time()
        if (cls.__last_updated is None or \
            now - cls.__last_updated > cls.update_interval):
            cls._read_projects()
            cls.__last_updated = now
    
    @classmethod
    def _read_projects(cls) -> None:
        new_cache = {}
        for d in cls.root.iterdir():
            if not d.is_dir():
                continue
            new_cache[str(d.relative_to(cls.root))] = frozenset(
                str(f.relative_to(cls.root))
                for f in d.iterdir()
            )
        cls.__cached_projects = new_cache
