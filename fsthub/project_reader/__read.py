from pathlib import Path
from typing import List, Union
from django.conf import settings

assert(isinstance(settings.HFST_CONTENT_ROOT, Path))
assert(settings.HFST_CONTENT_ROOT.is_dir())

def _get_project_paths() -> List[Path]:
    return [d
            for d in settings.HFST_CONTENT_ROOT.iterdir()
            if d.is_dir()]

def get_projects() -> List[str]:
    return [str(d.relative_to(settings.HFST_CONTENT_ROOT))
            for d in _get_project_paths()]

def get_fsts(project: Union[str, Path]) -> List[str]:
    if isinstance(project, str):
        project = Path(project)
    project = settings.HFST_CONTENT_ROOT.joinpath(project)
    fsts = []
    for f in project.iterdir():
        if not f.suffix in settings.HFST_FORMATS:
            continue
        fsts.append(str(f.relative_to(settings.HFST_CONTENT_ROOT)))
    return fsts

def get_all_fsts() -> List[str]:
    fsts = []
    for p in _get_project_paths():
        for f in p.iterdir():
            if not f.suffix in settings.HFST_FORMATS:
                continue
            fsts.append(str(f.relative_to(settings.HFST_CONTENT_ROOT)))
    return fsts

def path_exists(path: Union[str, Path]) -> bool:
    if isinstance(path, str):
        path = Path(path)
    path = settings.HFST_CONTENT_ROOT.joinpath(path)
    return path.exists()
