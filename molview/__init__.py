"""
MolView - Molstar-based protein viewer for Jupyter notebooks

A py3dmol-compatible library powered by Molstar for advanced molecular visualization.

Examples
--------
>>> import molview as mv
>>> v = mv.view(width=800, height=600)
>>> v.addModel(open('protein.pdb').read())  # Format auto-detected
>>> v.setColorMode('rainbow', palette='viridis')
>>> v.setSurface(True, opacity=40)
>>> v.show()
"""

from .viewer import view, MolView
from .colors import (
    get_color_theme,
    RAINBOW_PALETTES,
    CUSTOM_COLOR_PALETTE,
    SECONDARY_STRUCTURE_COLORS,
    PLDDT_COLORS
)
from .query import fetch_pdb, query, fetch_alphafold, search_pdb

__version__ = '0.1.0'
__author__ = 'Steven Yu'

__all__ = [
    'view',
    'MolView',
    'get_color_theme',
    'RAINBOW_PALETTES',
    'CUSTOM_COLOR_PALETTE',
    'SECONDARY_STRUCTURE_COLORS',
    'PLDDT_COLORS',
    'fetch_pdb',
    'query',
    'fetch_alphafold',
    'search_pdb',
]
