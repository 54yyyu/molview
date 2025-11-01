"""Color theme definitions and utilities for molview."""

# Rainbow color palettes from the nano protein viewer
RAINBOW_PALETTES = {
    'rainbow': ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF8000', '#FF0000'],
    'viridis': ['#440154', '#482878', '#3e4989', '#31688e', '#26828e', '#1f9e89',
                '#35b779', '#6ece58', '#b5de2b', '#fde724'],
    'plasma': ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b',
               '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'],
    'magma': ['#000004', '#1c1044', '#4f127b', '#812581', '#b5367a', '#e55964',
              '#fb8861', '#fec287', '#fcfdbf'],
    'blue-red': ['#0000FF', '#FF0000'],
    'pastel': ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#E0BBE4']
}

# Default chain colors
DEFAULT_CHAIN_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B4B4', '#52B788'
]

# Custom color palette (matching nano viewer)
CUSTOM_COLOR_PALETTE = {
    'teal': '#4ECDC4',
    'red': '#FF6B6B',
    'blue': '#4DABF7',
    'green': '#69DB7C',
    'yellow': '#FFD93D',
    'orange': '#FF922B',
    'purple': '#DA77F2',
    'pink': '#FF8CC8',
    'cyan': '#15AABF',
    'gray': '#868E96'
}

# pLDDT confidence color scheme (for predicted structures)
PLDDT_COLORS = {
    'very_high': '#0053D6',  # Dark blue (>90)
    'confident': '#65CBF3',  # Light blue (70-90)
    'low': '#FFDB13',        # Yellow (50-70)
    'very_low': '#FF7D45'    # Orange (<50)
}

# Secondary structure default colors
SECONDARY_STRUCTURE_COLORS = {
    'helix': '#0FA3FF',  # Royal blue for alpha helix
    'sheet': '#24B235',  # Lime green for beta sheet
    'coil': '#E8E8E8'    # Light gray for coil/loop
}


class ColorTheme:
    """Base class for color themes."""

    def __init__(self, name):
        self.name = name

    def to_molstar_config(self):
        """Convert to Molstar configuration."""
        raise NotImplementedError


class CustomColorTheme(ColorTheme):
    """Single custom color theme."""

    def __init__(self, color='#4ECDC4'):
        super().__init__('custom')
        self.color = color

    def to_molstar_config(self):
        return {
            'name': 'uniform',
            'params': {'value': self._hex_to_int(self.color)}
        }

    @staticmethod
    def _hex_to_int(hex_color):
        """Convert hex color to integer for Molstar."""
        return int(hex_color.replace('#', ''), 16)


class ElementColorTheme(ColorTheme):
    """Color by element type."""

    def __init__(self):
        super().__init__('element')

    def to_molstar_config(self):
        return {
            'name': 'element-symbol',
            'params': {}
        }


class ResidueColorTheme(ColorTheme):
    """Color by residue/amino acid."""

    def __init__(self):
        super().__init__('residue')

    def to_molstar_config(self):
        return {
            'name': 'residue-name',
            'params': {}
        }


class ChainColorTheme(ColorTheme):
    """Color by chain ID."""

    def __init__(self, custom_colors=None):
        super().__init__('chain')
        self.custom_colors = custom_colors or {}

    def to_molstar_config(self):
        if self.custom_colors:
            # Custom chain colors will be handled via custom theme
            return {
                'name': 'custom-chain-colors',
                'params': {'colors': self.custom_colors}
            }
        return {
            'name': 'chain-id',
            'params': {}
        }


class SecondaryStructureTheme(ColorTheme):
    """Color by secondary structure (helix, sheet, coil)."""

    def __init__(self, helix_color=None, sheet_color=None, coil_color=None):
        super().__init__('secondary')
        self.helix_color = helix_color or SECONDARY_STRUCTURE_COLORS['helix']
        self.sheet_color = sheet_color or SECONDARY_STRUCTURE_COLORS['sheet']
        self.coil_color = coil_color or SECONDARY_STRUCTURE_COLORS['coil']

    def to_molstar_config(self):
        return {
            'name': 'secondary-structure',
            'params': {
                'colors': {
                    'name': 'custom',
                    'params': {
                        'alphaHelix': self._hex_to_int(self.helix_color),
                        'threeTenHelix': self._hex_to_int(self.helix_color),
                        'piHelix': self._hex_to_int(self.helix_color),
                        'betaStrand': self._hex_to_int(self.sheet_color),
                        'betaTurn': self._hex_to_int(self.sheet_color),
                        'coil': self._hex_to_int(self.coil_color),
                        'bend': self._hex_to_int(self.coil_color),
                        'turn': self._hex_to_int(self.coil_color),
                        'dna': self._hex_to_int(self.coil_color),
                        'rna': self._hex_to_int(self.coil_color),
                        'carbohydrate': self._hex_to_int(self.coil_color)
                    }
                },
                'saturation': -1,
                'lightness': 0
            }
        }

    @staticmethod
    def _hex_to_int(hex_color):
        """Convert hex color to integer for Molstar."""
        return int(hex_color.replace('#', ''), 16)


class RainbowColorTheme(ColorTheme):
    """Rainbow gradient coloring by sequence position."""

    def __init__(self, palette='rainbow'):
        super().__init__('rainbow')
        if palette not in RAINBOW_PALETTES:
            raise ValueError(f"Unknown palette '{palette}'. Available: {list(RAINBOW_PALETTES.keys())}")
        self.palette = palette
        self.colors = RAINBOW_PALETTES[palette]

    def to_molstar_config(self):
        return {
            'name': 'rainbow-sequence',
            'params': {
                'palette': self.palette,
                'colors': self.colors
            }
        }


class PLDDTColorTheme(ColorTheme):
    """pLDDT confidence coloring for predicted structures."""

    def __init__(self):
        super().__init__('plddt')

    def to_molstar_config(self):
        return {
            'name': 'plddt-confidence',
            'params': {}
        }


def get_color_theme(mode, **kwargs):
    """
    Get a color theme object.

    Parameters
    ----------
    mode : str
        Color mode: 'custom', 'element', 'residue', 'chain', 'secondary', 'rainbow', or 'plddt'
    **kwargs : dict
        Additional parameters for the color theme

    Returns
    -------
    ColorTheme
        Color theme object

    Examples
    --------
    >>> theme = get_color_theme('custom', color='#FF0000')
    >>> theme = get_color_theme('rainbow', palette='viridis')
    >>> theme = get_color_theme('secondary', helix_color='#FF0000')
    """
    mode = mode.lower()

    if mode == 'custom':
        return CustomColorTheme(color=kwargs.get('color', '#4ECDC4'))
    elif mode == 'element':
        return ElementColorTheme()
    elif mode == 'residue':
        return ResidueColorTheme()
    elif mode == 'chain':
        return ChainColorTheme(custom_colors=kwargs.get('custom_colors'))
    elif mode == 'secondary':
        return SecondaryStructureTheme(
            helix_color=kwargs.get('helix_color'),
            sheet_color=kwargs.get('sheet_color'),
            coil_color=kwargs.get('coil_color')
        )
    elif mode == 'rainbow':
        return RainbowColorTheme(palette=kwargs.get('palette', 'rainbow'))
    elif mode == 'plddt':
        return PLDDTColorTheme()
    else:
        raise ValueError(f"Unknown color mode '{mode}'. Available: custom, element, residue, chain, secondary, rainbow, plddt")


# Utility functions for color manipulation
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def interpolate_color(color1, color2, factor):
    """Interpolate between two hex colors."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    r = int(rgb1[0] + factor * (rgb2[0] - rgb1[0]))
    g = int(rgb1[1] + factor * (rgb2[1] - rgb1[1]))
    b = int(rgb1[2] + factor * (rgb2[2] - rgb1[2]))

    return rgb_to_hex(r, g, b)


def generate_gradient(colors, steps):
    """
    Generate a gradient of colors.

    Parameters
    ----------
    colors : list of str
        List of hex colors to interpolate between
    steps : int
        Number of color steps to generate

    Returns
    -------
    list of str
        List of hex colors
    """
    if steps <= 0:
        return []
    if steps == 1:
        return [colors[0]]
    if len(colors) == 0:
        return []
    if len(colors) == 1:
        return [colors[0]] * steps

    gradient = []
    segment_count = len(colors) - 1

    for i in range(steps):
        position = i / (steps - 1) * segment_count
        segment_index = int(position)
        segment_position = position - segment_index

        if segment_index >= segment_count:
            gradient.append(colors[-1])
        else:
            color = interpolate_color(
                colors[segment_index],
                colors[segment_index + 1],
                segment_position
            )
            gradient.append(color)

    return gradient
