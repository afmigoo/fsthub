from unittest import TestCase
from pathlib import Path
from typing import List, Union
from random import getrandbits
from time import sleep
import random
import shutil

from . import ProjectReader as PR

class TestPRViews(TestCase):
    test_root = Path(__file__).parent / 'tmp'

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)
        PR.root = self.test_root
    def tearDown(self):
        # rm all contents
        shutil.rmtree(self.test_root)
        # make sure to clear all cache
        self.test_root.mkdir()
        PR.update_interval = 0.01
        sleep(0.01)
        PR._update_if_time()
        self.test_root.rmdir()

    def create_project(self, name: str, fsts: List[str]):
        d = self.test_root / name
        d.mkdir()
        for fst_name in fsts:
            f = d / fst_name
            f.touch()
    
    def test_spam_empty(self):
        for _ in range(10_000):
            self.assertFalse(PR.fst_exists(str(getrandbits)))
            self.assertFalse(PR.project_exists(str(getrandbits)))
            self.assertEqual(len(list(PR.get_projects())), 0)
            self.assertEqual(len(list(PR.get_all_fsts())), 0)
            self.assertEqual(PR.get_project_count(), 0)
            self.assertEqual(PR.get_fst_count(), 0)

    def test_put_single(self):
        PR.update_interval = 0.5
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        self.create_project('TEST1', [f'fst{i}' for i in range(100)])
        sleep(0.5)

        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 1)
        self.assertEqual(t_count, 100)
    
    def test_put_many(self):
        PR.update_interval = 0.5
        Np, Nfst = 1_000, 10
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])
        sleep(0.5)

        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        prefixes = set(fst.split('/')[-2] for fst in PR.get_all_fsts())
        for pref in prefixes:
            self.assertTrue(PR.project_exists(str(pref)))
            
    def test_put_many_delete_many(self):
        Np, Nfst = 100, 20
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        for p in range(Np):
            self.create_project(f'TEST{p}', [f'fst{i}' for i in range(Nfst)])

        PR.update_interval = 10 ** 10
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

        PR.update_interval = 0.1
        sleep(0.1)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)

        for p in range(Np):
            self.create_project(f'SECOND_TEST{p}', [f'fst{i}' for i in range(Nfst)])
        PR.update_interval = 3
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np)
        self.assertEqual(t_count, Np * Nfst)
        sleep(3)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np * 2)
        self.assertEqual(t_count, Np * Nfst * 2)

        shutil.rmtree(self.test_root)
        self.test_root.mkdir()
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, Np * 2)
        self.assertEqual(t_count, Np * Nfst * 2)

        PR.update_interval = 0.1
        sleep(0.1)
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)

    def test_all_exist(self):
        sleep(0.1)
        Np = 3
        Nfst = 3

        PR.update_interval = 0.1
        p_count = PR.get_project_count()
        t_count = PR.get_fst_count()
        self.assertEqual(p_count, 0)
        self.assertEqual(t_count, 0)
        self.assertFalse(PR.fst_exists('some/thing'))
        self.assertFalse(PR.project_exists('some'))

        all_projects = []
        all_fst = []
        fsts = [f'fst{i}' for i in range(Nfst)]
        for p in range(Np):
            new_p = f'TEST{p}'
            all_projects.append(new_p)
            all_fst.extend(f'{new_p}/{f}' for f in fsts)
            self.create_project(new_p, fsts)
        sleep(0.1)
        for p in all_projects:
            self.assertTrue(PR.project_exists(p), f'{p} does not exist')
            self.assertSetEqual(set(f'{p}/{f}' for f in fsts),
                                set(PR.get_fsts(p)))
        for fst in all_fst:
            self.assertTrue(PR.fst_exists(fst), f'{fst} does not exist')

        self.assertFalse(PR.fst_exists('some/thing'))
        self.assertFalse(PR.project_exists('some'))

class TestPRRandom(TestCase):
    temp_root = Path(__file__).parent / 'tmp'
    @classmethod
    def setUpClass(cls):
        # Create a temp dir structure
        cls.temp_root.mkdir()
        PR.root = cls.temp_root
        PR.update_interval = 0.5  # Short interval for faster testing
        
        # Create test projects/files
        files = {
            p: [f"file_{i}.hfst" for i in range(random.randint(1, 15))]
            for p in [f"Project_{i}" for i in range(31)]
        }
        
        for project, files in files.items():
            (cls.temp_root / project).mkdir()
            for f in files:
                (cls.temp_root / project / f).touch()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_root)

    def test_random_operations(self):
        operations = [
            self._get_projects,
            self._get_all_fsts,
            self._get_project_fsts,
            self._project_exists,
            self._fst_exists,
            self._add_project,
            self._del_project,
            self._add_fst,
            self._del_fst,
        ]
        
        for _ in range(50):  # Adjust count as needed
            op = random.choice(operations)
            op()

    def _get_real_projects(self):
        return list(str(d.relative_to(self.temp_root)) 
                        for d in self.temp_root.iterdir() 
                        if d.is_dir())
    
    def _get_real_fsts(self, proj: Union[str, Path]):
        if isinstance(proj, str):
            proj = self.temp_root.joinpath(proj)
        self.assertTrue(proj.is_dir())
        return list(str(f.relative_to(self.temp_root)) 
                        for f in proj.iterdir() 
                        if f.is_file())

    def _get_projects(self):
        existing_projects = self._get_real_projects()
        result = list(PR.get_projects())
        self.assertEqual(set(result), set(existing_projects))
        
    def _get_all_fsts(self):
        all_files = []
        for p in self.temp_root.iterdir():
            all_files.extend(self._get_real_fsts(p))
        result = list(PR.get_all_fsts())
        self.assertEqual(set(result), set(all_files))
        
    def _get_project_fsts(self):
        project_path = random.choice(self._get_real_projects())
        result = list(PR.get_fsts(project_path))
        self.assertEqual(set(result), 
                         set(self._get_real_fsts(project_path)))
        
    def _project_exists(self):
        existing_projects = self._get_real_projects()
        project = random.choice(existing_projects + [f"nonexistent{i}" for i in range(5)])
        expected = self.temp_root.joinpath(project).exists()
        self.assertEqual(PR.project_exists(project), expected)
        
    def _fst_exists(self):
        existing_projects = self._get_real_projects()
        project = random.choice(existing_projects)
        existing_fst = list(str(d.relative_to(self.temp_root)) 
                            for d in self.temp_root.joinpath(project).iterdir()
                            if d.is_file())
        path = random.choice(existing_fst + [f"{project}/ghost.hfst"])
        expected = self.temp_root.joinpath(path).exists()
        self.assertEqual(PR.fst_exists(path), expected)

    def _add_project(self):
        new_proj = f'RandProj{random.randint(1, 10_000_000)}'
        before_update = set(PR.get_projects())
        self.assertSetEqual(before_update, set(self._get_real_projects()))

        (self.temp_root / new_proj).mkdir(exist_ok=True)
        sleep(PR.update_interval)
        after_update = set(PR.get_projects())
        self.assertSetEqual(after_update, set(self._get_real_projects()))

    def _del_project(self):
        existing_projects = self._get_real_projects()        
        before_update = set(PR.get_projects())
        self.assertSetEqual(before_update, set(existing_projects))

        proj_to_delete = random.choice(existing_projects)
        shutil.rmtree(self.temp_root / proj_to_delete)
        sleep(PR.update_interval)

        after_update = set(PR.get_projects())
        self.assertSetEqual(after_update, set(self._get_real_projects()))

    def _add_fst(self):
        existing_projects = self._get_real_projects()   
        proj = random.choice(existing_projects)
        new_fst = f'{proj}/rand_fst_{random.randint(1, 10_000_000)}'
        before_update = set(PR.get_fsts(proj))
        self.assertSetEqual(before_update, set(self._get_real_fsts(proj)))

        (self.temp_root / new_fst).touch()
        sleep(PR.update_interval)
        after_update = set(PR.get_fsts(proj))
        self.assertSetEqual(after_update, set(self._get_real_fsts(proj)))

    def _del_fst(self):
        existing_projects = self._get_real_projects()   
        proj = random.choice(existing_projects)
        existing_fsts = self._get_real_fsts(proj)
        if len(existing_fsts) == 0:
            return
        fst_to_delete = random.choice(existing_fsts)
        before_update = set(PR.get_fsts(proj))
        self.assertSetEqual(before_update, set(self._get_real_fsts(proj)))

        (self.temp_root / fst_to_delete).unlink()
        sleep(PR.update_interval)
        after_update = set(PR.get_fsts(proj))
        self.assertSetEqual(after_update, set(self._get_real_fsts(proj)))
