"""
Simple test script for molview library.

This demonstrates basic functionality without requiring Jupyter.
"""

import molview as mv

# Test 1: Import and version
print("MolView version:", mv.__version__)
print("✓ Import successful")

# Test 2: Available palettes
print("\nAvailable rainbow palettes:")
for palette in mv.RAINBOW_PALETTES.keys():
    print(f"  - {palette}")
print("✓ Palette data loaded")

# Test 3: Create viewer
v = mv.view(width=800, height=600)
print("\n✓ Viewer created")

# Test 4: Color themes
print("\nTesting color themes:")

# Element
v.setColorMode('element')
print("  ✓ Element color mode")

# Custom
v.setColorMode('custom', color='#FF0000')
print("  ✓ Custom color mode")

# Residue
v.setColorMode('residue')
print("  ✓ Residue color mode")

# Chain
v.setColorMode('chain')
print("  ✓ Chain color mode")

# Secondary
v.setColorMode('secondary', helix_color='#FF0000', sheet_color='#00FF00', coil_color='#0000FF')
print("  ✓ Secondary structure color mode")

# Rainbow
v.setColorMode('rainbow', palette='viridis')
print("  ✓ Rainbow color mode (viridis)")

# pLDDT
v.setColorMode('plddt')
print("  ✓ pLDDT color mode")

# Test 5: Other features
v.setSurface(True, opacity=40)
print("\n✓ Surface configuration")

v.setIllustrativeStyle(True)
print("✓ Illustrative style")

v.setBackgroundColor('#000000')
print("✓ Background color")

v.spin(True)
print("✓ Spin animation")

v.zoomTo()
print("✓ Camera reset")

# Test 6: Add model (with dummy data)
sample_pdb = """ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C
ATOM      4  O   ALA A   1       1.251   2.390   0.000  1.00  0.00           O
END"""

v.addModel(sample_pdb, 'pdb')
print("\n✓ Model added")

# Test 7: Generate HTML (without displaying)
html = v._generate_html()
print("✓ HTML generated")
print(f"  HTML length: {len(html)} characters")

# Summary
print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
print("\nTo use in Jupyter notebook:")
print("  import molview as mv")
print("  v = mv.view()")
print("  v.addModel(pdb_data, 'pdb')")
print("  v.setColorMode('rainbow', palette='viridis')")
print("  v.show()")
