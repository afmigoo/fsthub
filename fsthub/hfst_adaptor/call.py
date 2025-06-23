from typing import List, Tuple, Union, Literal, Dict
from pathlib import Path
from dataclasses import dataclass
import subprocess
import logging
import re

from .exceptions import HFSTInvalidFormat, HfstException

logger = logging.getLogger(__name__)
OUTPUT_FORMATS = ['xerox', 'cg', 'apertium']

def injection_filter(option: str) -> str:
    """
    This module recieves user input only via arg list like so:
    ["hfst-lookup", "-q", "<user_file_name>", "--format", "<user_format>"]
    Files are checked to be present before being passed to call_command() two times:
        - at api level before calling this module
        - at call_hfst_*() functions with Path(user_input).is_file()
    Formats are checked to be present in `OUTPUT_FORMATS` before being passed to bash
    This filter provides a third and last resort if others fail
    """
    return re.sub(r'[ ";&|<>$(){}\[\]\\:*@#]', '', option)

def call_command(args: List[str], input: str = "") -> Tuple[str, str, int]:
    """Call custom bash command and pass input to stdin

    Parameters
    ----------
    args : List[str]
        args that will be passed to Popen. example: ['hfst-lookup', '-q', 'english.hfst']
    input : str
        input that will be passed to stdin

    Returns
    -------
    Tuple[str, str, int]
        stdout, stderr and return code
    """
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate(input=bytes(input, encoding='utf8'))
    stdout = stdout.decode() if stdout else ''
    stderr = stderr.decode() if stderr else ''
    return stdout, stderr, proc.returncode

def call_metadata_extractor(hfst_file: Union[Path, str]) -> str:
    if isinstance(hfst_file, str):
        hfst_file = Path(hfst_file)
    if not hfst_file.is_file():
        raise FileNotFoundError(hfst_file)
    hfst_file = str(hfst_file)

    stdout, stderr, code = call_command(['hfst-edit-metadata', '-p', 
                                         injection_filter(hfst_file)])
    
    if code != 0:
        raise HfstException(f'hfst-edit-metadata: {stdout.strip()} {hfst_file} code: {code}')
    return stdout

def call_hfst_proc(hfst_file: Union[Path, str],
                   input_strings: List[str],
                   oformat: str = 'cg') -> str:
    if not oformat in OUTPUT_FORMATS:
        raise ValueError(f'oformat must be one of {OUTPUT_FORMATS}, got {oformat}')
    if isinstance(hfst_file, str):
        hfst_file = Path(hfst_file)
    if not hfst_file.is_file():
        raise FileNotFoundError(hfst_file)
    hfst_file = str(hfst_file)

    inp_str = ' '.join(input_strings) + ' '
    stdout, stderr, code = call_command(['hfst-proc', f'--{injection_filter(oformat)}', 
                                         injection_filter(hfst_file)], 
                                        inp_str)
    if code != 0:
        if stdout.lower().strip() == 'transducer must be in hfst optimized lookup format.':
            raise HFSTInvalidFormat(f'hfst-proc: {stdout.strip()} {hfst_file}')
        else:
            raise HfstException(f'hfst-proc: stdout={stdout}; stderr={stderr} code: {code}')
    return stdout

def call_hfst_lookup(hfst_file: Union[Path, str],
                     input_strings: List[str],
                     oformat: str = 'cg') -> str:
    if not oformat in OUTPUT_FORMATS:
        raise ValueError(f'oformat must be one of {OUTPUT_FORMATS}, got {oformat}')
    if isinstance(hfst_file, str):
        hfst_file = Path(hfst_file)
    if not hfst_file.is_file():
        raise FileNotFoundError(hfst_file)
    hfst_file = str(hfst_file)

    inp_str = '\n'.join(input_strings)
    stdout, stderr, code = call_command(['hfst-lookup', '-q', 
                                         '--output-format', injection_filter(oformat), 
                                         injection_filter(hfst_file)], 
                                        inp_str)
    if code != 0:
        raise HfstException(f'hfst-lookup: stdout={stdout}; stderr={stderr} code: {code}')
    return stdout

def call_hfst(hfst_file: Union[Path, str], 
              input_strings: List[str],
              oformat: str = 'cg') -> str:
    """Inputs all strings to a HFST transducer and returns it's output.
    First, it tries to call hfst-proc but fallbacks to hfst-lookup if FST is not optimized.
    """
    if not oformat in OUTPUT_FORMATS:
        raise ValueError(f'oformat must be one of {OUTPUT_FORMATS}, got {oformat}')
    if isinstance(hfst_file, str):
        hfst_file = Path(hfst_file)
    if not hfst_file.is_file():
        raise FileNotFoundError(hfst_file)
    
    if hfst_file.suffix == '.hfst':
        return call_hfst_lookup(hfst_file, input_strings, oformat)
    if hfst_file.suffix == '.hfstol':
        try:
            return call_hfst_proc(hfst_file, input_strings, oformat)
        except HFSTInvalidFormat:
            return call_hfst_lookup(hfst_file, input_strings, oformat)
    raise ValueError(f'Invalid FST format. Expected .hfst/.hfstol, got \'{hfst_file.suffix}\'')
