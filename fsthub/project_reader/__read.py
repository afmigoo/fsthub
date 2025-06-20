from pathlib import Path
from typing import List, Union, Set, Generator, FrozenSet
from django.conf import settings
from itertools import chain
from time import time

assert(isinstance(settings.HFST_CONTENT_ROOT, Path))
assert(settings.HFST_CONTENT_ROOT.is_dir())

class ProjectReader():
    root: Path = settings.HFST_CONTENT_ROOT
    __cached_projects: FrozenSet[str] = None
    __cached_fsts: FrozenSet[str] = None
    __last_updated: float = None
    update_interval: int = 60

    @classmethod
    def get_projects(cls) -> Generator[str, None, None]:
        cls._update_if_time()
        return (x for x in cls.__cached_projects)
    
    @classmethod
    def get_fsts(cls) -> Generator[str, None, None]:
        cls._update_if_time()
        return (x for x in cls.__cached_fsts)

    @classmethod
    def get_project_count(cls) -> int:
        cls._update_if_time()
        if cls.__cached_projects is None:
            return 0
        return len(cls.__cached_projects)
    
    @classmethod
    def get_fst_count(cls) -> int:
        cls._update_if_time()
        if cls.__cached_fsts is None:
            return 0
        return len(cls.__cached_fsts)

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
        new_cache = frozenset(
            str(path.relative_to(cls.root))
            for path in cls.root.iterdir()
            if path.is_dir()
        )
        cls.__cached_projects = new_cache

    @classmethod
    def _read_fsts(cls) -> None:
        # This function will be called quite often, every `cls.update_interval`
        # And amount of fsts may be huge
        # I wanted to avoid unnesesary contaiter convertisation like frozenset(set)
        # This code simply chains generators, its like `cls._read_projects` but it
        # gathers folder contents instead of folders
        project_paths = (cls.root.joinpath(p) for p in cls.__cached_projects)
        new_cache = frozenset(chain.from_iterable(
            (str(f.relative_to(cls.root)) 
             for f in p.iterdir() if f.is_file())
            for p in project_paths
        ))
        cls.__cached_fsts = new_cache
