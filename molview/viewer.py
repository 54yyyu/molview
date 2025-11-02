"""Main viewer class for molview - py3dmol-compatible API."""

import html
import json
import os
import uuid
from pathlib import Path
from IPython.display import HTML, display

from .colors import get_color_theme, RAINBOW_PALETTES


class MolView:
    """
    Molstar-based protein viewer for Jupyter notebooks.

    Similar to py3dmol.view() but powered by Molstar for advanced features.

    Parameters
    ----------
    width : int, optional
        Width of the viewer in pixels (default: 800)
    height : int, optional
        Height of the viewer in pixels (default: 600)
    viewergrid : tuple, optional
        Grid layout (rows, cols) for multiple viewers, e.g., (2, 2) creates a 2x2 grid
    panel : bool, optional
        Show control panel on the right side (default: False)

    Examples
    --------
    >>> import molview as mv
    >>> v = mv.view(width=800, height=600)
    >>> v.addModel(open('protein.pdb').read(), 'pdb')
    >>> v.setColorMode('rainbow', palette='viridis')
    >>> v.show()

    >>> # With control panel
    >>> v = mv.view(width=800, height=600, panel=True)
    >>> v.addModel(pdb_data)
    >>> v.show()
    """

    def __init__(self, width=800, height=600, viewergrid=None, panel=False):
        self.width = width
        self.height = height
        self.viewergrid = viewergrid
        self.panel = panel

        # Grid mode setup
        if viewergrid is not None:
            if not isinstance(viewergrid, tuple) or len(viewergrid) != 2:
                raise ValueError("viewergrid must be a tuple of (rows, cols)")
            self.rows, self.cols = viewergrid
            self.total_viewers = self.rows * self.cols
            # Each grid cell has its own models list
            self.grid_models = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.rows = None
            self.cols = None
            self.total_viewers = 1

        # Structure data
        self.models = []
        self.current_model_index = -1

        # Display settings
        self.color_mode = 'element'
        self.color_params = {}
        self.background_color = '#FFFFFF'
        self.surface_enabled = False
        self.surface_opacity = 40
        self.illustrative_enabled = False
        self.spin_enabled = False
        self.spin_speed = 0.2
        self.show_sequence = False
        self.show_animation = False
        self.remove_solvent = False

        # Style settings
        self.style_settings = {
            'cartoon': True,
            'stick': False,
            'sphere': False,
            'line': False
        }

    def _detect_format(self, data):
        """
        Auto-detect the file format from the data content.

        Parameters
        ----------
        data : str
            Molecular structure data

        Returns
        -------
        str
            Detected format: 'pdb', 'mmcif', or 'sdf'
        """
        # Get first few lines for detection (strip whitespace)
        lines = [line.strip() for line in data.strip().split('\n')[:50] if line.strip()]

        if not lines:
            # Default to PDB if empty
            return 'pdb'

        # Check for mmCIF format
        # mmCIF files start with data_ and contain loop_ constructs
        first_line = lines[0].lower()
        if first_line.startswith('data_'):
            return 'mmcif'

        # Check for loop_ or _atom_site keywords (mmCIF)
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith('loop_') or line_lower.startswith('_atom_site') or line_lower.startswith('_cell'):
                return 'mmcif'

        # Check for SDF format
        # SDF files have specific markers like $$$$, M  END, V2000, V3000
        data_upper = data.upper()
        if '$$$$' in data_upper or 'M  END' in data_upper:
            return 'sdf'
        if 'V2000' in data_upper or 'V3000' in data_upper:
            return 'sdf'

        # Check for PDB format keywords
        # Common PDB record types at the start of files
        pdb_keywords = ['HEADER', 'TITLE', 'COMPND', 'SOURCE', 'KEYWDS', 'EXPDTA',
                        'AUTHOR', 'REVDAT', 'REMARK', 'SEQRES', 'HELIX', 'SHEET',
                        'ATOM', 'HETATM', 'MODEL', 'CRYST1', 'ORIGX', 'SCALE', 'MTRIX']

        for line in lines[:20]:  # Check first 20 non-empty lines
            # PDB records are typically in the first 6 characters
            if len(line) >= 6:
                record_type = line[:6].strip().upper()
                if record_type in pdb_keywords:
                    return 'pdb'

        # Check for typical ATOM/HETATM lines (can appear later in file)
        for line in lines:
            if len(line) >= 4:
                record_type = line[:6].strip().upper()
                if record_type in ['ATOM', 'HETATM']:
                    return 'pdb'

        # Default to PDB format if unable to detect
        return 'pdb'

    def addModel(self, data, format=None, keepH=False, viewer=None, name=None):
        """
        Add a molecular model to the viewer.

        Parameters
        ----------
        data : str
            Molecular structure data (PDB, mmCIF, or SDF format)
        format : str, optional
            Format of the data: 'pdb', 'mmcif', 'cif', or 'sdf'.
            If None, format will be auto-detected (default: None)
        keepH : bool, optional
            Keep hydrogen atoms (not implemented, for py3dmol compatibility)
        viewer : tuple, optional
            Grid position (row, col) for grid mode, e.g., viewer=(0, 1)
        name : str, optional
            Name for this structure. Defaults to 'Structure 1', 'Structure 2', etc.

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> # Auto-detect format (recommended)
        >>> v = mv.view()
        >>> v.addModel(open('protein.pdb').read())
        >>> v.show()

        >>> # Explicit format
        >>> v = mv.view()
        >>> v.addModel(pdb_data, 'pdb')
        >>> v.show()

        >>> # Grid viewer
        >>> v = mv.view(viewergrid=(2, 2))
        >>> v.addModel(pdb1, viewer=(0, 0))
        >>> v.addModel(pdb2, viewer=(0, 1))
        >>> v.show()

        >>> # Custom names for structures
        >>> v = mv.view()
        >>> v.addModel(pdb_data, name='Wild Type')
        >>> v.addModel(mutant_data, name='L99A Mutant')
        >>> v.show()
        """
        # Auto-detect format if not specified
        if format is None:
            format = self._detect_format(data)

        # Normalize format
        format = format.lower()
        if format in ['cif', 'mmcif']:
            format = 'mmcif'
        elif format not in ['pdb', 'sdf']:
            raise ValueError(f"Unsupported format '{format}'. Use 'pdb', 'mmcif', or 'sdf'")

        # Handle grid mode
        if self.viewergrid is not None:
            # Generate default name for grid mode
            if name is None:
                if viewer is None:
                    # Will be auto-placed, count existing models
                    existing_count = sum(1 for row in self.grid_models for cell in row if cell is not None)
                    name = f'Structure {existing_count + 1}'
                else:
                    row, col = viewer
                    name = f'Structure ({row},{col})'

            model = {
                'data': data,
                'format': format,
                'keepH': keepH,
                'name': name
            }

            if viewer is None:
                # Auto-place in next available cell
                viewer = self._get_next_available_cell()
            row, col = viewer
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                raise ValueError(f"viewer position ({row}, {col}) out of bounds for {self.rows}x{self.cols} grid")
            self.grid_models[row][col] = model
        else:
            # Single viewer mode - generate default name
            if name is None:
                name = f'Structure {len(self.models) + 1}'

            model = {
                'data': data,
                'format': format,
                'keepH': keepH,
                'name': name
            }

            self.models.append(model)
            self.current_model_index = len(self.models) - 1

        return self

    def setStyle(self, style=None, **kwargs):
        """
        Set molecular representation style.

        Note: Currently only cartoon mode is fully supported.
        Additional styles coming soon.

        Parameters
        ----------
        style : dict, optional
            Style dictionary (py3dmol format)
        **kwargs : dict
            Style parameters

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.setStyle({'cartoon': {}})
        """
        if style is not None:
            if 'cartoon' in style:
                self.style_settings['cartoon'] = True
            if 'stick' in style:
                self.style_settings['stick'] = True
            if 'sphere' in style:
                self.style_settings['sphere'] = True

        return self

    def setColorMode(self, mode, **kwargs):
        """
        Set color theme for the structure.

        Parameters
        ----------
        mode : str
            Color mode: 'custom', 'element', 'residue', 'chain', 'secondary', 'rainbow', or 'plddt'
        **kwargs : dict
            Additional parameters for the color mode

        Keyword Arguments
        -----------------
        color : str
            Hex color for 'custom' mode (default: '#4ECDC4')
        palette : str
            Palette name for 'rainbow' mode: 'rainbow', 'viridis', 'plasma', 'magma', 'blue-red', 'pastel'
        helix_color : str
            Hex color for helices in 'secondary' mode (default: '#0FA3FF')
        sheet_color : str
            Hex color for sheets in 'secondary' mode (default: '#24B235')
        coil_color : str
            Hex color for coils in 'secondary' mode (default: '#E8E8E8')
        custom_colors : dict
            Chain ID to color mapping for 'chain' mode

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.setColorMode('element')
        >>> v.setColorMode('custom', color='#FF0000')
        >>> v.setColorMode('rainbow', palette='viridis')
        >>> v.setColorMode('secondary', helix_color='#FF0000', sheet_color='#00FF00')
        >>> v.setColorMode('chain', custom_colors={'A': '#FF0000', 'B': '#00FF00'})
        """
        theme = get_color_theme(mode, **kwargs)
        config = theme.to_molstar_config()

        self.color_mode = config['name']
        self.color_params = config['params']

        return self

    def setBackgroundColor(self, color):
        """
        Set background color.

        Parameters
        ----------
        color : str
            Hex color code (e.g., '#FFFFFF')

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.setBackgroundColor('#000000')  # Black background
        >>> v.setBackgroundColor('#FFFFFF')  # White background
        """
        self.background_color = color
        return self

    def setSurface(self, enabled=True, opacity=40, inherit_color=True, color=None):
        """
        Enable or disable surface representation.

        Parameters
        ----------
        enabled : bool, optional
            Enable surface rendering (default: True)
        opacity : int, optional
            Surface opacity 0-100 (default: 40)
        inherit_color : bool, optional
            Inherit color from current theme (default: True)
        color : str, optional
            Custom surface color if inherit_color=False

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.setSurface(True, opacity=50)
        >>> v.setSurface(True, opacity=30, inherit_color=False, color='#FF0000')
        """
        self.surface_enabled = enabled
        self.surface_opacity = max(0, min(100, opacity))

        if not inherit_color and color:
            # Store custom surface color in params
            self.color_params['surface_color'] = color

        return self

    def setIllustrativeStyle(self, enabled=True):
        """
        Enable illustrative rendering style with outlines.

        Parameters
        ----------
        enabled : bool, optional
            Enable illustrative style (default: True)

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.setIllustrativeStyle(True)
        >>> v.setIllustrativeStyle(False)
        """
        self.illustrative_enabled = enabled
        return self

    def setLayout(self, mode):
        """
        Set layout mode (single or grid).

        Note: This method is primarily for interactive use with panel=True.
        Grid dimensions are auto-calculated based on number of loaded models.

        Parameters
        ----------
        mode : str
            Layout mode: 'single' or 'grid'

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v = mv.view(panel=True)
        >>> v.addModel(pdb1)
        >>> v.addModel(pdb2)
        >>> v.setLayout('grid')  # Switch to grid view
        >>> v.setLayout('single')  # Switch back to single view
        """
        if mode not in ['single', 'grid']:
            raise ValueError("mode must be 'single' or 'grid'")

        # This will be handled by JavaScript in the viewer
        # The actual grid is created dynamically from loaded models
        return self

    def zoomTo(self, sel=None):
        """
        Reset camera to fit the structure.

        Parameters
        ----------
        sel : dict, optional
            Selection (not implemented, for py3dmol compatibility)

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.zoomTo()
        """
        # Will be handled by JavaScript
        return self

    def spin(self, enabled=True, speed=0.2):
        """
        Enable continuous rotation.

        Parameters
        ----------
        enabled : bool, optional
            Enable spinning (default: True)
        speed : float, optional
            Rotation speed (default: 0.2)

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.spin(True)
        >>> v.spin(True, speed=1.0)
        >>> v.spin(False)
        """
        self.spin_enabled = enabled
        self.spin_speed = speed
        return self

    def removeSolvent(self, enabled=True):
        """
        Remove solvent molecules (water, ions) from visualization.

        Parameters
        ----------
        enabled : bool, optional
            Enable solvent removal (default: True)

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.removeSolvent(True)
        >>> v.removeSolvent(False)
        """
        self.remove_solvent = enabled
        return self

    def clear(self):
        """
        Clear all models from the viewer.

        Returns
        -------
        self
            For method chaining

        Examples
        --------
        >>> v.clear()
        """
        self.models = []
        self.current_model_index = -1
        return self

    def show(self):
        """
        Display the viewer in Jupyter notebook.

        This renders the HTML and displays it in the notebook output.

        Examples
        --------
        >>> v = mv.view()
        >>> v.addModel(pdb_data, 'pdb')
        >>> v.show()
        """
        html = self._generate_html()
        # Wrap in iframe for proper Jupyter notebook display
        iframe_html = self._wrap_in_iframe(html)
        display(HTML(iframe_html))

    def _repr_html_(self):
        """IPython rich display representation."""
        html = self._generate_html()
        # Wrap in iframe for proper Jupyter notebook display
        return self._wrap_in_iframe(html)

    def _generate_html(self):
        """Generate HTML for the viewer."""
        # Convert boolean to JavaScript
        def bool_to_js(val):
            return 'true' if val else 'false'

        # Check if grid mode
        if self.viewergrid is not None:
            return self._generate_grid_html(bool_to_js)
        else:
            return self._generate_single_html(bool_to_js)

    def _wrap_in_iframe(self, html_content):
        """
        Wrap HTML content in an iframe for proper Jupyter notebook display.

        This ensures that complete HTML documents with scripts are properly
        isolated and rendered in the notebook.
        """
        # Generate unique ID for this viewer instance
        viewer_id = f"molview-{uuid.uuid4().hex[:8]}"

        # Escape HTML for srcdoc attribute
        escaped_html = html.escape(html_content)

        # Calculate total width (add panel width if enabled OR if in grid mode)
        # In grid mode, we need to reserve space for panel since it will show when switching to single view
        panel_width = 280 if (self.panel or self.viewergrid is not None) else 0
        total_width = self.width + panel_width

        # Create iframe with srcdoc
        iframe_html = f'''<iframe
            id="{viewer_id}"
            width="{total_width}"
            height="{self.height}"
            frameborder="0"
            srcdoc="{escaped_html}"
            style="border: none;"
        ></iframe>'''

        return iframe_html

    def _calculate_grid_dimensions(self, num_models):
        """
        Calculate optimal grid dimensions for n models.

        Args:
            num_models: Number of models to display

        Returns:
            tuple: (rows, cols) for grid layout
        """
        import math

        if num_models == 0:
            return (1, 1)

        rows = math.ceil(math.sqrt(num_models))
        cols = math.ceil(num_models / rows)
        return (rows, cols)

    def _get_next_available_cell(self):
        """
        Find next empty grid cell for auto-placement.

        Returns:
            tuple: (row, col) of next available cell

        Raises:
            ValueError: If grid is full
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid_models[row][col] is None:
                    return (row, col)
        raise ValueError(f"Grid is full ({self.rows}x{self.cols})")

    def _generate_single_html(self, bool_to_js):
        """Generate HTML for single viewer mode."""
        template_path = Path(__file__).parent / 'templates' / 'viewer.html'

        with open(template_path, 'r') as f:
            template = f.read()

        # Get current model data
        structure_data = ''
        structure_format = 'pdb'
        if self.current_model_index >= 0 and self.current_model_index < len(self.models):
            model = self.models[self.current_model_index]
            # Properly escape for JavaScript string (order matters!)
            structure_data = (model['data']
                .replace('\\', '\\\\')  # Escape backslashes first
                .replace('"', '\\"')     # Escape double quotes
                .replace('\n', '\\n')    # Escape newlines
                .replace('\r', '\\r'))   # Escape carriage returns
            structure_format = model['format']

        # Replace template variables
        html = template.replace('{{height}}', str(self.height))
        html = html.replace('{{width}}', str(self.width))
        html = html.replace('{{panel_enabled}}', bool_to_js(self.panel))
        html = html.replace('{{color_mode}}', self.color_mode)
        html = html.replace('{{color_params}}', json.dumps(self.color_params))
        html = html.replace('{{background_color}}', self.background_color)
        html = html.replace('{{surface_enabled}}', bool_to_js(self.surface_enabled))
        html = html.replace('{{surface_opacity}}', str(self.surface_opacity))
        html = html.replace('{{illustrative_enabled}}', bool_to_js(self.illustrative_enabled))
        html = html.replace('{{spin_enabled}}', bool_to_js(self.spin_enabled))
        html = html.replace('{{spin_speed}}', str(self.spin_speed))
        html = html.replace('{{show_sequence}}', bool_to_js(self.show_sequence))
        html = html.replace('{{show_animation}}', bool_to_js(self.show_animation))
        html = html.replace('{{remove_solvent}}', bool_to_js(self.remove_solvent))
        html = html.replace('{{structure_data}}', structure_data)
        html = html.replace('{{structure_format}}', structure_format)

        # Grid mode variables (not used in single mode)
        html = html.replace('{{is_grid_mode}}', 'false')
        html = html.replace('{{rows}}', '1')
        html = html.replace('{{cols}}', '1')
        html = html.replace('{{grid_data}}', '[[]]')

        # Pass all models for multi-structure support
        all_models_data = []
        for model in self.models:
            all_models_data.append({
                'name': model.get('name', 'Structure'),
                'data': model['data'],
                'format': model['format']
            })
        html = html.replace('{{all_models}}', json.dumps(all_models_data))

        return html

    def _generate_grid_html(self, bool_to_js):
        """Generate HTML for grid viewer mode."""
        # Use the same template as single mode
        template_path = Path(__file__).parent / 'templates' / 'viewer.html'

        with open(template_path, 'r') as f:
            template = f.read()

        # Prepare grid data - let json.dumps handle escaping
        grid_data_processed = []
        for row in self.grid_models:
            row_data = []
            for cell in row:
                if cell is None:
                    row_data.append(None)  # Will become null in JSON
                else:
                    cell_json = {
                        'data': cell['data'],  # Raw data, json.dumps will escape
                        'format': cell['format'],
                        'name': cell.get('name', 'Structure')
                    }
                    row_data.append(cell_json)
            grid_data_processed.append(row_data)

        # Replace template variables
        html = template.replace('{{height}}', str(self.height))
        html = html.replace('{{width}}', str(self.width))
        html = html.replace('{{rows}}', str(self.rows))
        html = html.replace('{{cols}}', str(self.cols))
        html = html.replace('{{grid_data}}', json.dumps(grid_data_processed))
        html = html.replace('{{color_mode}}', self.color_mode)
        html = html.replace('{{color_params}}', json.dumps(self.color_params))
        html = html.replace('{{background_color}}', self.background_color)
        html = html.replace('{{surface_enabled}}', bool_to_js(self.surface_enabled))
        html = html.replace('{{surface_opacity}}', str(self.surface_opacity))
        html = html.replace('{{illustrative_enabled}}', bool_to_js(self.illustrative_enabled))
        html = html.replace('{{spin_enabled}}', bool_to_js(self.spin_enabled))
        html = html.replace('{{spin_speed}}', str(self.spin_speed))
        html = html.replace('{{remove_solvent}}', bool_to_js(self.remove_solvent))

        # Grid mode flag
        html = html.replace('{{is_grid_mode}}', 'true')

        # Single mode variables (not used in grid mode)
        html = html.replace('{{panel_enabled}}', 'false')
        html = html.replace('{{show_sequence}}', 'false')
        html = html.replace('{{show_animation}}', 'false')
        html = html.replace('{{structure_data}}', '')
        html = html.replace('{{structure_format}}', 'pdb')
        html = html.replace('{{all_models}}', '[]')  # Empty for grid mode

        return html

    # Additional py3dmol-compatible methods for future implementation

    def removeAllModels(self):
        """Remove all models (alias for clear)."""
        return self.clear()

    def getModel(self, model_id=0):
        """Get model by ID (placeholder for compatibility)."""
        if 0 <= model_id < len(self.models):
            return self.models[model_id]
        return None

    def setViewStyle(self, style=None):
        """Set view style (placeholder for compatibility)."""
        return self

    def addSurface(self, surf_type, style=None, sel=None):
        """Add surface (use setSurface instead)."""
        self.setSurface(True)
        return self

    def addLabel(self, text, options=None, sel=None):
        """Add label (not implemented yet)."""
        return self

    def render(self):
        """Render the viewer (use show instead)."""
        self.show()


# Factory function to match py3dmol API
def view(width=800, height=600, viewergrid=None, panel=False, **kwargs):
    """
    Create a new MolView viewer instance.

    This is the main entry point, similar to py3dmol.view().

    Parameters
    ----------
    width : int, optional
        Width of the viewer in pixels (default: 800)
    height : int, optional
        Height of the viewer in pixels (default: 600)
    viewergrid : tuple, optional
        Grid layout (rows, cols) for multiple viewers, e.g., (2, 2) for a 2x2 grid
    panel : bool, optional
        Show control panel on the right side (default: False)
    **kwargs : dict
        Additional viewer options

    Returns
    -------
    MolView
        Viewer instance

    Examples
    --------
    >>> import molview as mv
    >>> v = mv.view(width=800, height=600)
    >>> v.addModel(open('protein.pdb').read(), 'pdb')
    >>> v.setColorMode('rainbow', palette='viridis')
    >>> v.show()

    >>> # With control panel
    >>> v = mv.view(width=800, height=600, panel=True)
    >>> v.addModel(pdb_data)
    >>> v.show()
    """
    return MolView(width=width, height=height, viewergrid=viewergrid, panel=panel)
