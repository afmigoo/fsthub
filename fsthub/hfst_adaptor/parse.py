from typing import List, Dict
from dataclasses import dataclass
import re

@dataclass
class ParsedItem:
    input_str: str
    out_variants: List[str]

    def __str__(self):
        return f'{self.input_str} -> {"/".join(self.out_variants)}'

def parse_apertium_format(fst_stdout: str) -> List[ParsedItem]:
    items: List[ParsedItem] = []
    # regex: all strings like '^+$' (apertium format) with no nested ^ or $ 
    for raw in re.finditer(r'\^([^\^\$]+)\$', fst_stdout):
        apertium = raw.groups()[-1]
        input_str, *output_variants = apertium.split('/')
        items.append(ParsedItem(input_str=input_str,
                                out_variants=output_variants))
    return items

def parse_metadata(hfst_output: str, lower_keys: bool = False) -> Dict[str, str]:
    lines = hfst_output.split('\n')
    metadata = {}
    for l in lines:
        semicol_idx = l.find(':')
        if semicol_idx == -1:
            continue
        key = l[:semicol_idx].lower() if lower_keys else l[:semicol_idx]
        value = l[semicol_idx + 1:] if semicol_idx + 1 < len(l) else ''
        metadata[key] = value.strip()
    return metadata
