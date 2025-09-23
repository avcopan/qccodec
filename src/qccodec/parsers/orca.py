"""Parsers for Orca output files."""

import re
from enum import Enum
from pathlib import Path
from typing import Generator, Optional, Union

from qcconst import constants
from qcio import (
    CalcType,
    ProgramInput,
    ProgramOutput,
    Provenance,
    SinglePointResults,
    Structure,
)

from qccodec.exceptions import MatchNotFoundError, ParserError

from ..registry import register
from .utils import re_finditer, re_search


class OrcaFileType(str, Enum):
    """Orca filetypes."""

    STDOUT = "stdout"
    DIRECTORY = "directory"


def iter_files(
    stdout: Optional[str], directory: Optional[Union[Path, str]]
) -> Generator[tuple[OrcaFileType, Union[str, bytes, Path]], None, None]:
    """
    Iterate over the files in an Orca output directory.

    If stdout is provided, yields a tuple for it.

    If directory is provided, iterates over the directory to yield files according to
    program-specific logic.

    Args:
        stdout: The contents of the Orca stdout file.
        directory: The path to the directory containing the Orca output files.

    Yields:
        (FileType, contents) tuples for a program's output.
    """
    if stdout is not None:
        yield OrcaFileType.STDOUT, stdout

    if directory is not None:
        directory = Path(directory)
        # Check if the directory exists and is a directory
        if not directory.exists() or not directory.is_dir():
            raise ParserError(
                f"Directory {directory} does not exist or is not a directory."
            )
        yield OrcaFileType.DIRECTORY, directory


@register(
    filetype=OrcaFileType.STDOUT,
    calctypes=[CalcType.energy, CalcType.gradient, CalcType.hessian],
    target="energy",
)
def parse_energy(contents: str) -> float:
    """Parse the final energy from Orca stdout.

    NOTE:
        - Works on frequency files containing many energy values because re.search()
          returns the first result.
    """
    regex = r"FINAL ENERGY: (-?\d+(?:\.\d+)?)"
    return float(re_search(regex, contents).group(1))
