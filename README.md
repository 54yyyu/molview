# MolView

A Molstar-based protein viewer for Jupyter notebooks with a py3dmol-compatible API.

## Features

- **py3dmol-compatible API** - Easy transition from py3dmol
- **Powered by Molstar** - Advanced molecular visualization engine
- **Rich color themes** - 7 color modes including rainbow gradients and pLDDT confidence
- **Surface rendering** - Customizable molecular surfaces
- **Illustrative style** - Artistic rendering with outlines
- **Direct PDB/AlphaFold fetching** - Download structures without leaving Python
- **Grid layout** - Compare multiple structures side-by-side
- **Jupyter integration** - Native display in notebooks

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import molview as mv

# Create viewer
v = mv.view(width=800, height=600)

# Load structure
with open('protein.pdb') as f:
    v.addModel(f.read(), 'pdb')

# Display
v.show()
```

## Fetching Structures from Databases

MolView can directly fetch structures from RCSB PDB and AlphaFold DB:

### Fetch from RCSB PDB
```python
import molview as mv

# Fetch ubiquitin structure (1UBQ)
data = mv.fetch_pdb('1UBQ')

v = mv.view()
v.addModel(data, 'pdb')
v.show()
```

### Fetch mmCIF format
```python
# Fetch in mmCIF format
data = mv.fetch_pdb('7BV2', format='mmcif')
v = mv.view()
v.addModel(data, 'mmcif')
v.show()
```

### Fetch from AlphaFold DB
```python
# Fetch AlphaFold prediction for Human ABL1 kinase
data = mv.fetch_alphafold('P00519')

v = mv.view()
v.addModel(data, 'mmcif')
v.setColorMode('plddt')  # Color by confidence
v.show()
```

### Search PDB Database
```python
# Search for structures
pdb_ids = mv.search_pdb('hemoglobin', max_results=5)
print(pdb_ids)  # ['1A3N', '1GZX', '2HHB', ...]

# Visualize first result
if pdb_ids:
    data = mv.fetch_pdb(pdb_ids[0])
    v = mv.view()
    v.addModel(data, 'pdb')
    v.show()
```

## Color Modes

MolView supports all color modes from the nano protein viewer:

### 1. Element (by atom type)
```python
v.setColorMode('element')
```

### 2. Custom (single color)
```python
v.setColorMode('custom', color='#FF0000')  # Red
v.setColorMode('custom', color='#4ECDC4')  # Teal (default)
```

### 3. Residue (by amino acid)
```python
v.setColorMode('residue')
```

### 4. Chain (by chain ID)
```python
# Auto colors
v.setColorMode('chain')

# Custom chain colors
v.setColorMode('chain', custom_colors={
    'A': '#FF0000',  # Red
    'B': '#00FF00',  # Green
    'C': '#0000FF'   # Blue
})
```

### 5. Secondary Structure
```python
# Default colors (helix=blue, sheet=green, coil=gray)
v.setColorMode('secondary')

# Custom colors
v.setColorMode('secondary',
    helix_color='#FF0000',  # Red helices
    sheet_color='#00FF00',  # Green sheets
    coil_color='#0000FF'    # Blue coils
)
```

### 6. Rainbow (gradient by sequence)
```python
# Available palettes: 'rainbow', 'viridis', 'plasma', 'magma', 'blue-red', 'pastel'
v.setColorMode('rainbow', palette='viridis')
v.setColorMode('rainbow', palette='plasma')
v.setColorMode('rainbow', palette='magma')
```

### 7. pLDDT (confidence for predicted structures)
```python
v.setColorMode('plddt')
```

## Grid Viewer (Multiple Structures)

Compare multiple structures side-by-side in a grid layout:

```python
# Create a 2x2 grid
v = mv.view(viewergrid=(2, 2), width=900, height=900)

# Load structures into specific positions
v.addModel(pdb1, 'pdb', viewer=(0, 0))  # Top-left
v.addModel(pdb2, 'pdb', viewer=(0, 1))  # Top-right
v.addModel(pdb3, 'pdb', viewer=(1, 0))  # Bottom-left
v.addModel(pdb4, 'pdb', viewer=(1, 1))  # Bottom-right

# Settings apply to all viewers
v.setColorMode('rainbow', palette='viridis')
v.setSurface(True, opacity=40)
v.show()
```

**Note**: In grid mode, the `viewer=(row, col)` parameter is required for `addModel()`.

See [example/grid_examples.ipynb](example/grid_examples.ipynb) for more grid layout examples.

## Advanced Features

### Surface Rendering
```python
# Enable surface with default opacity (40%)
v.setSurface(True)

# Custom opacity (0-100)
v.setSurface(True, opacity=60)

# Custom surface color
v.setSurface(True, opacity=40, inherit_color=False, color='#FF0000')
```

### Illustrative Style
```python
# Enable artistic rendering with outlines
v.setIllustrativeStyle(True)
```

### Camera Controls
```python
# Reset camera view
v.zoomTo()

# Enable continuous rotation
v.spin(True)
```

### Background Color
```python
v.setBackgroundColor('#000000')  # Black
v.setBackgroundColor('#FFFFFF')  # White
```

## Complete Example

```python
import molview as mv

# Create viewer
v = mv.view(width=800, height=600)

# Load structure
with open('protein.pdb') as f:
    pdb_data = f.read()
v.addModel(pdb_data, 'pdb')

# Set rainbow coloring with viridis palette
v.setColorMode('rainbow', palette='viridis')

# Add semi-transparent surface
v.setSurface(True, opacity=40)

# Enable illustrative style
v.setIllustrativeStyle(True)

# Set black background
v.setBackgroundColor('#000000')

# Display
v.show()
```

## Comparison with py3dmol

MolView is designed to be a drop-in replacement for py3dmol with additional features:

### py3dmol code:
```python
import py3dmol
v = py3dmol.view(width=800, height=600)
v.addModel(pdb_data, 'pdb')
v.setStyle({'cartoon': {'color': 'spectrum'}})
v.show()
```

### Equivalent MolView code:
```python
import molview as mv
v = mv.view(width=800, height=600)
v.addModel(pdb_data, 'pdb')
v.setColorMode('rainbow')
v.show()
```

## Supported Formats

- **PDB** - Protein Data Bank format
- **mmCIF** - Macromolecular Crystallographic Information File
- **SDF** - Structure Data File (coming soon)

## API Reference

### Viewer Creation
- `view(width, height, viewergrid)` - Create viewer instance
  - `viewergrid=(rows, cols)` - Optional grid layout for multiple structures

### Model Management
- `addModel(data, format, viewer)` - Load structure data
  - `viewer=(row, col)` - Required in grid mode to specify position
- `clear()` - Remove all models

### Fetching Structures
- `fetch_pdb(pdb_id, format='pdb')` - Fetch structure from RCSB PDB
- `query(pdb_id, format='pdb')` - Alias for fetch_pdb (py3dmol compatibility)
- `fetch_alphafold(uniprot_id, version=4)` - Fetch AlphaFold prediction
- `search_pdb(query_text, max_results=10)` - Search PDB database

### Styling
- `setColorMode(mode, **kwargs)` - Set color theme
- `setStyle(style)` - Set representation (cartoon default)
- `setSurface(enabled, opacity, inherit_color, color)` - Configure surface
- `setIllustrativeStyle(enabled)` - Toggle illustrative rendering
- `setBackgroundColor(color)` - Set background

### Camera
- `zoomTo()` - Reset camera view
- `spin(enabled)` - Toggle continuous rotation

### Display
- `show()` - Render in notebook

## Color Palettes

### Rainbow Palettes
Available palettes for `setColorMode('rainbow', palette='...')`:

- `'rainbow'` - Classic rainbow (ROYGBIV)
- `'viridis'` - Perceptually uniform (purple to yellow)
- `'plasma'` - Bright and vibrant (purple to yellow)
- `'magma'` - Dark and moody (black to white)
- `'blue-red'` - Simple blue to red gradient
- `'pastel'` - Soft pastel colors

### Custom Color Palette
Pre-defined colors for `setColorMode('custom', color='...')`:

- Teal: `#4ECDC4` (default)
- Red: `#FF6B6B`
- Blue: `#4DABF7`
- Green: `#69DB7C`
- Yellow: `#FFD93D`
- Orange: `#FF922B`
- Purple: `#DA77F2`
- Pink: `#FF8CC8`
- Cyan: `#15AABF`
- Gray: `#868E96`

## Requirements

- Python >=3.7
- IPython >=7.0.0
- Jupyter >=1.0.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Repository**: [github.com/54yyyu/molview](https://github.com/54yyyu/molview)

This package uses modern Python packaging with `pyproject.toml` (PEP 517/518).

## Acknowledgments

- Built with [Molstar](https://molstar.org/) - Modern molecular visualization toolkit
- API inspired by [py3dmol](https://github.com/3dmol/3Dmol.js) - Python interface to 3Dmol.js
- Color palettes from scientific visualization best practices

## Roadmap

- [x] Multiple viewer grid support
- [ ] Selection and highlighting
- [ ] Animation playback
- [ ] Label/annotation support
- [ ] Export to image/video
- [ ] Additional representation styles (stick, sphere, line)
- [ ] Measurement tools
- [ ] Surface customization options
