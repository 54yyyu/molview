# MolView

<img src="https://raw.githubusercontent.com/54yyyu/molview/main/media/logo.ico" width="10%" alt="Molview" align="left">

An IPython/Jupyter widget for interactive molecular visualization, based on [Molstar](https://molstar.org/). This is the Jupyter widget version of [nano-protein-viewer](https://github.com/54yyyu/nano-protein-viewer).


## Features

- **Molstar-powered visualization** - Advanced molecular graphics engine
- **Multiple color modes** - Element, chain, secondary structure, rainbow gradients, pLDDT confidence, and custom colors
- **Interactive controls** - Optional control panel with real-time adjustments
- **Surface rendering** - Molecular surfaces with customizable opacity
- **Illustrative rendering** - Outline-based artistic visualization
- **Grid layout** - Side-by-side comparison of multiple structures
- **Structure fetching** - Direct download from RCSB PDB and AlphaFold Database
- **File downloads** - Export loaded structures
- **py3dmol-like API** - Familiar interface for easy adoption

## Installation

```bash
pip install molview
```

## Quick Start

```python
import molview as mv

# Create viewer
v = mv.view(width=800, height=600)

# Load structure from file
with open('protein.pdb') as f:
    v.addModel(f.read())

# Or fetch from RCSB PDB
pdb_data = mv.fetch_pdb('1CRN')
v.addModel(pdb_data)

# Customize and display
v.setColorMode('rainbow', palette='viridis')
v.show()
```

## Control Panel

Enable the interactive control panel for real-time adjustments:

```python
v = mv.view(width=800, height=600, panel=True)
v.addModel(pdb_data)
v.show()
```

The panel provides controls for:
- Color modes with customizable parameters
- Surface rendering toggle and opacity
- Solvent molecule removal
- File downloads
- Spin animation with speed control

## Fetching Structures

### From RCSB PDB

```python
# Fetch PDB format
data = mv.fetch_pdb('1UBQ')
v = mv.view()
v.addModel(data)
v.show()

# Fetch mmCIF format
data = mv.fetch_pdb('7BV2', format='mmcif')
v.addModel(data)
```

### From AlphaFold Database

```python
# Fetch by UniProt ID
data = mv.fetch_alphafold('P00519')
v = mv.view()
v.addModel(data)
v.setColorMode('plddt')  # Color by confidence
v.show()
```

### Search PDB

```python
# Search for structures
pdb_ids = mv.search_pdb('hemoglobin', max_results=5)
print(pdb_ids)  # ['1A3N', '1GZX', '2HHB', ...]

# Visualize first result
data = mv.fetch_pdb(pdb_ids[0])
v = mv.view()
v.addModel(data)
v.show()
```

## Color Modes

### Element

Color by atom type (CPK coloring):

```python
v.setColorMode('element')
```

### Custom

Single uniform color:

```python
v.setColorMode('custom', color='#FF6B6B')
```

### Chain

Color by protein chain:

```python
# Automatic colors
v.setColorMode('chain')

# Custom chain colors
v.setColorMode('chain', custom_colors={
    'A': '#FF0000',
    'B': '#00FF00'
})
```

### Secondary Structure

Color by structural elements:

```python
# Default colors
v.setColorMode('secondary')

# Custom colors
v.setColorMode('secondary',
    helix_color='#FF6B6B',
    sheet_color='#4ECDC4',
    coil_color='#FFE66D'
)
```

### Rainbow Gradient

Color by sequence position with scientific color palettes:

```python
v.setColorMode('rainbow', palette='viridis')
v.setColorMode('rainbow', palette='plasma')
v.setColorMode('rainbow', palette='magma')
```

Available palettes: `rainbow`, `viridis`, `plasma`, `magma`, `blue-red`, `pastel`

### pLDDT Confidence

Color predicted structures by confidence scores:

```python
v.setColorMode('plddt')
```

Colors: Dark blue (>90), light blue (70-90), yellow (50-70), orange (<50)

## Grid Layout

Display multiple structures side-by-side:

```python
# Create 2x2 grid
v = mv.view(viewergrid=(2, 2), width=900, height=900)

# Load structures into specific positions
v.addModel(pdb1, viewer=(0, 0))  # Top-left
v.addModel(pdb2, viewer=(0, 1))  # Top-right
v.addModel(pdb3, viewer=(1, 0))  # Bottom-left
v.addModel(pdb4, viewer=(1, 1))  # Bottom-right

# Apply settings to all viewers
v.setColorMode('rainbow', palette='viridis')
v.show()
```

The `viewer=(row, col)` parameter is required when using grid layout.

## Advanced Features

### Surface Rendering

```python
# Enable with default opacity (40%)
v.setSurface(True)

# Custom opacity (0-100)
v.setSurface(True, opacity=60)

# Custom surface color
v.setSurface(True, opacity=40, inherit_color=False, color='#FF0000')
```

### Illustrative Style

Artistic rendering with outlines:

```python
v.setIllustrativeStyle(True)
```

### Animation

```python
# Enable spinning
v.spin(True)

# Custom speed
v.spin(True, speed=0.5)

# Stop spinning
v.spin(False)
```

### Solvent Removal

Remove water molecules and ions:

```python
v.removeSolvent(True)
```

### Background Color

```python
v.setBackgroundColor('#000000')  # Black
v.setBackgroundColor('#FFFFFF')  # White
```
## Complete Example

```python
import molview as mv

# Create viewer with control panel
v = mv.view(width=800, height=600, panel=True)

# Fetch and load structure
pdb_data = mv.fetch_pdb('1CRN')
v.addModel(pdb_data)

# Apply styling
v.setColorMode('rainbow', palette='viridis')
v.setSurface(True, opacity=40)
v.setIllustrativeStyle(True)
v.setBackgroundColor('#1a1a2e')
v.spin(True, speed=0.2)

# Display
v.show()
```

## API Reference

### Creating Viewers

```python
view(width=800, height=600, viewergrid=None, panel=False)
```

- `width`, `height`: Viewer dimensions in pixels
- `viewergrid`: Tuple of `(rows, cols)` for grid layout
- `panel`: Enable interactive control panel

### Loading Structures

```python
addModel(data, format=None, viewer=None)
```

- `data`: Structure data string
- `format`: Auto-detected if not specified (`pdb`, `mmcif`, `sdf`)
- `viewer`: Grid position `(row, col)` for grid layout

### Fetching Data

```python
fetch_pdb(pdb_id, format='pdb')        # Fetch from RCSB PDB
fetch_alphafold(uniprot_id, version=4)  # Fetch from AlphaFold DB
search_pdb(query, max_results=10)       # Search PDB database
query(pdb_id, format='pdb')            # Alias for fetch_pdb
```

### Styling Methods

```python
setColorMode(mode, **kwargs)              # Set color scheme
setBackgroundColor(color)                 # Set background
setSurface(enabled, opacity, ...)         # Configure surface
setIllustrativeStyle(enabled)            # Toggle outlines
spin(enabled, speed)                      # Toggle rotation
removeSolvent(enabled)                    # Toggle solvent visibility
zoomTo()                                  # Reset camera
show()                                    # Render viewer
```

## Supported Formats

- **PDB** - Protein Data Bank format
- **mmCIF** - Macromolecular Crystallographic Information File  
- **SDF** - Structure Data File (small molecules)

Format is auto-detected from file content.

## Requirements

- Python >=3.7
- IPython >=7.0.0
- Jupyter >=1.0.0

## Examples

See the `example/` directory for Jupyter notebooks:
- `example.ipynb` - Comprehensive feature demonstrations
- `grid_examples.ipynb` - Grid layout examples

## py3dmol Compatibility

MolView provides a py3dmol-like API for easy adoption. Key differences:

- Format auto-detection (second parameter optional)
- Additional color modes (pLDDT, rainbow gradients)
- Built-in control panel
- Grid layout support
- Structure fetching utilities

## Related Projects

- [nano-protein-viewer](https://github.com/54yyyu/nano-protein-viewer) - Standalone web version
- [Molstar](https://molstar.org/) - Underlying visualization engine

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Molstar](https://molstar.org/) - Modern molecular visualization toolkit
- Project idea inspired by [py2Dmol](https://github.com/sokrypton/py2Dmol)
- API inspired by [py3dmol](https://github.com/3dmol/3Dmol.js) - Python interface to 3Dmol.js
- Color palettes from scientific visualization best practices

## Roadmap

- [x] Multiple viewer grid support
- [ ] Selection and highlighting
- [ ] Animation playback
- [ ] Label/annotation support
- [x] Export to image/video
- [ ] Additional representation styles (stick, sphere, line)
- [x] Surface customization options
