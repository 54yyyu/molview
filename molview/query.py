"""Query and fetch protein structures from RCSB PDB."""

import urllib.request
import urllib.error


def fetch_pdb(pdb_id, format='pdb'):
    """
    Fetch a protein structure from RCSB PDB.

    Parameters
    ----------
    pdb_id : str
        PDB ID (e.g., '1UBQ', '7BV2')
    format : str, optional
        Format: 'pdb' or 'mmcif' (default: 'pdb')

    Returns
    -------
    str
        Structure data in the requested format

    Raises
    ------
    ValueError
        If format is not 'pdb' or 'mmcif'
    urllib.error.HTTPError
        If PDB ID is not found or download fails

    Examples
    --------
    >>> import molview as mv
    >>> data = mv.fetch_pdb('1UBQ')
    >>> v = mv.view()
    >>> v.addModel(data)  # Format auto-detected
    >>> v.show()

    >>> # Fetch mmCIF format
    >>> data = mv.fetch_pdb('7BV2', format='mmcif')
    >>> v.addModel(data)  # Auto-detects mmCIF
    """
    # Normalize PDB ID
    pdb_id = pdb_id.strip().upper()

    # Validate format
    format = format.lower()
    if format not in ['pdb', 'mmcif', 'cif']:
        raise ValueError(f"Format must be 'pdb' or 'mmcif', got '{format}'")

    # Normalize mmcif/cif to mmcif
    if format == 'cif':
        format = 'mmcif'

    # Construct URL based on format
    if format == 'pdb':
        url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    else:  # mmcif
        url = f'https://files.rcsb.org/download/{pdb_id}.cif'

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"PDB ID '{pdb_id}' not found in RCSB PDB database")
        else:
            raise


def query(pdb_id, format='pdb'):
    """
    Alias for fetch_pdb() to match py3dmol API.

    Parameters
    ----------
    pdb_id : str
        PDB ID (e.g., '1UBQ', '7BV2')
    format : str, optional
        Format: 'pdb' or 'mmcif' (default: 'pdb')

    Returns
    -------
    str
        Structure data in the requested format

    Examples
    --------
    >>> import molview as mv
    >>> data = mv.query('1UBQ')
    >>> v = mv.view()
    >>> v.addModel(data)  # Format auto-detected
    >>> v.show()
    """
    return fetch_pdb(pdb_id, format)


def fetch_alphafold(uniprot_id, version=4):
    """
    Fetch an AlphaFold predicted structure from AlphaFold DB.

    Parameters
    ----------
    uniprot_id : str
        UniProt ID (e.g., 'P00520', 'Q9Y6K9')
    version : int, optional
        AlphaFold database version (default: 4)

    Returns
    -------
    str
        Structure data in mmCIF format

    Raises
    ------
    ValueError
        If UniProt ID is not found
    urllib.error.HTTPError
        If download fails

    Examples
    --------
    >>> import molview as mv
    >>> data = mv.fetch_alphafold('P00520')
    >>> v = mv.view()
    >>> v.addModel(data)  # Format auto-detected as mmCIF
    >>> v.setColorMode('plddt')
    >>> v.show()
    """
    # Normalize UniProt ID
    uniprot_id = uniprot_id.strip().upper()

    # Construct URL for AlphaFold DB
    url = f'https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v{version}.cif'

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"UniProt ID '{uniprot_id}' not found in AlphaFold DB (version {version})")
        else:
            raise


def search_pdb(query_text, max_results=10):
    """
    Search RCSB PDB for structures matching a query.

    Note: This requires the requests library. Returns PDB IDs only.

    Parameters
    ----------
    query_text : str
        Search query (e.g., 'hemoglobin', 'SARS-CoV-2')
    max_results : int, optional
        Maximum number of results to return (default: 10)

    Returns
    -------
    list of str
        List of PDB IDs matching the query

    Examples
    --------
    >>> import molview as mv
    >>> pdb_ids = mv.search_pdb('ubiquitin', max_results=5)
    >>> print(pdb_ids)
    ['1UBQ', '1D3Z', '2JF5', ...]

    >>> # Fetch the first result
    >>> if pdb_ids:
    ...     data = mv.fetch_pdb(pdb_ids[0])
    ...     v = mv.view()
    ...     v.addModel(data)  # Format auto-detected
    ...     v.show()
    """
    try:
        import json
    except ImportError:
        raise ImportError("json module required for search functionality")

    # Simple text search query for RCSB PDB
    search_url = 'https://search.rcsb.org/rcsbsearch/v2/query'

    query_json = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "value": query_text
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": max_results
            }
        }
    }

    try:
        req = urllib.request.Request(
            search_url,
            data=json.dumps(query_json).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

            if 'result_set' in result and result['result_set']:
                return [entry['identifier'] for entry in result['result_set']]
            else:
                return []

    except urllib.error.HTTPError as e:
        print(f"Search failed: {e}")
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []
