"""
Test apps' views through a `django.test.Client` object.
"""
from unittest import TestCase
from pathlib import Path
import subprocess
import os
import shutil

from hfst_adaptor.call import (
    injection_filter,
    call_hfst_lookup,
    call_hfst_proc,
    call_hfst,
    call_example_generator,
    call_metadata_extractor
)

class TestHfstCompilable(TestCase):
    test_data = Path(__file__).parent / 'test_data'
    test_root = Path(__file__).parent / 'tmp'

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)
        shutil.copyfile(self.test_data / 'Makefile',
                        self.test_root / 'Makefile')
        shutil.copyfile(self.test_data / 'ping.fst',
                        self.test_root / 'ping.fst')

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def test_hfst_binary_compilation_ability(self):
        result = subprocess.run(
            ["make"],
            cwd=self.test_root,
            capture_output=True
        )
        self.assertEqual(
            result.returncode, 0,
            f'Test hfst binary did not compile successfully\n{result.stdout}\n{result.stderr}'
        )

class TestHfstCalls(TestCase):
    test_data = Path(__file__).parent / 'test_data'
    test_root = Path(__file__).parent / 'tmp'
    test_hfst = test_root / 'ping.hfstol'
    expected_proc_out = {
        'xerox': 'ping\tpong'.strip(),
        'cg': '"<ping>"\n\t"pong"'.strip(),
        'apertium': '^ping/pong$'.strip()
    }
    expected_lookup_out = {
        'xerox': 'ping\tpong\t0.000000'.strip(),
        # this is a known fixed bug, waiting for the release
        # https://github.com/hfst/hfst/issues/589
        'cg': '"<ping>"\n\t""pong\t0.000000'.strip(),
        'apertium': '^ping/pong$'.strip()
    }

    def setUp(self):
        self.test_root.mkdir(exist_ok=True)
        shutil.copyfile(self.test_data / 'Makefile',
                        self.test_root / 'Makefile')
        shutil.copyfile(self.test_data / 'ping.fst',
                        self.test_root / 'ping.fst')
        result = subprocess.run(
            ["make"],
            cwd=self.test_root,
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(f'Failed to compile test hfst:\n{result.stdout}\n{result.stderr}')

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def test_hfst_proc(self):
        for fmt, exp_out in self.expected_proc_out.items():
            real_out = call_hfst_proc(
                self.test_hfst,
                ['ping'], oformat=fmt
            ).strip()
            self.assertEqual(
                real_out, exp_out,
                f'Hfst returned unexpected output ({fmt}):\n{real_out}\nexpected:\n{exp_out}'
            )

    def test_hfst_lookup(self):
        for fmt, exp_out in self.expected_lookup_out.items():
            real_out = call_hfst_lookup(
                self.test_hfst,
                ['ping'], oformat=fmt
            ).strip()
            self.assertEqual(
                real_out, exp_out,
                f'Hfst returned unexpected output ({fmt}):\n{real_out}\nexpected:\n{exp_out}'
            )

    def test_hfst_call(self):
        for fmt, exp_out in self.expected_proc_out.items():
            real_out = call_hfst(
                self.test_hfst,
                ['ping'], oformat=fmt
            ).strip()
            self.assertEqual(
                real_out, exp_out,
                f'Hfst returned unexpected output ({fmt}):\n{real_out}\nexpected:\n{exp_out}'
            )

    def test_hfst_gen_example(self):
        exp_out = 'ping:pong'
        for _ in range(20):
            real_out = call_example_generator(
                self.test_hfst
            ).strip()
            self.assertEqual(
                real_out, exp_out,
                f'Hfst example generator returned unexpected output:\n{real_out}\nexpected:\n{exp_out}'
            )

    def test_hfst_meta_extraction(self):
        exp_lines = [
            'foo: bar',
            'Author: Jane Doe',
            'Year: 2000'
        ]
        real_out = call_metadata_extractor(
            self.test_hfst
        ).strip()
        for exp_l in exp_lines:
            self.assertIn(
                exp_l, real_out,
                f'Hfst meta extractor didnt return {exp_l}\ngot:\n{real_out}'
            )
