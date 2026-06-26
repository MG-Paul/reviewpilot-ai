import re
from typing import List, Dict, Any

def parse_ris(content: str) -> List[Dict[str, Any]]:
    """
    Parses RIS bibliography file format.
    Each reference starts with TY and ends with ER.
    """
    references = []
    current_ref = {}
    authors = []
    
    # Split content by line and clean whitespace
    lines = [line.strip() for line in content.splitlines()]
    
    for line in lines:
        if not line:
            continue
        
        # RIS matches format: TAG  - VALUE (can have variable spaces before hyphen)
        match = re.match(r"^([A-Z0-9]{2})\s*-\s*(.*)$", line)
        if match:
            tag, val = match.groups()
            
            if tag == "TY":
                # Start of a new reference
                current_ref = {"import_source": "RIS", "raw_metadata": {}}
                authors = []
            elif tag == "ER":
                # End of reference
                if current_ref:
                    current_ref["authors"] = authors
                    references.append(current_ref)
                    current_ref = {}
            elif current_ref is not None:
                # Add to raw metadata
                current_ref["raw_metadata"][tag] = val
                
                # Map standard tags
                if tag == "TI" or tag == "T1":
                    current_ref["title"] = val
                elif tag == "AB" or tag == "N2":
                    current_ref["abstract"] = val
                elif tag == "AU" or tag == "A1":
                    authors.append(val)
                elif tag == "JO" or tag == "JF" or tag == "T2":
                    current_ref["journal"] = val
                elif tag == "PY" or tag == "Y1":
                    # Extract 4 digit year
                    year_match = re.search(r"\d{4}", val)
                    current_ref["year"] = int(year_match.group(0)) if year_match else None
                elif tag == "DO":
                    current_ref["doi"] = val
                elif tag == "VL":
                    current_ref["volume"] = val
                elif tag == "IS":
                    current_ref["issue"] = val
                elif tag == "SP":
                    current_ref["pages"] = val
                elif tag == "EP" and "pages" in current_ref:
                    current_ref["pages"] = f"{current_ref['pages']}-{val}"
                    
    return references

def parse_bibtex(content: str) -> List[Dict[str, Any]]:
    """
    Parses BibTeX bibliography file format (basic regex-based parser).
    """
    references = []
    
    # Split by @ symbols which mark start of entries (excluding header or comments)
    entries = re.split(r'@', content)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        # Match type and citation key, e.g. article{key,
        entry_match = re.match(r"^([a-zA-Z]+)\s*\{\s*([^,]+),", entry.strip())
        if not entry_match:
            continue
            
        entry_type, cite_key = entry_match.groups()
        ref = {
            "import_source": "BibTeX",
            "raw_metadata": {"cite_key": cite_key, "entry_type": entry_type}
        }
        
        # Regex to pull fields like title = {val} or author = "val"
        field_matches = re.finditer(
            r'([a-zA-Z0-9_-]+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|"([^"]*)"|([0-9]+))', 
            entry
        )
        
        authors = []
        for match in field_matches:
            field = match.group(1).lower()
            val = match.group(2) or match.group(3) or match.group(4)
            if not val:
                continue
                
            val = val.strip()
            ref["raw_metadata"][field] = val
            
            if field == "title":
                # Strip curly braces commonly used in bibtex for casing protection
                ref["title"] = val.replace("{", "").replace("}", "")
            elif field == "abstract":
                ref["abstract"] = val
            elif field == "author":
                # Authors in BibTeX are usually separated by 'and'
                authors = [a.strip() for a in val.split(" and ")]
            elif field == "journal" or field == "booktitle":
                ref["journal"] = val
            elif field == "year":
                ref["year"] = int(val) if val.isdigit() else None
            elif field == "doi":
                ref["doi"] = val
            elif field == "volume":
                ref["volume"] = val
            elif field == "number":
                ref["issue"] = val
            elif field == "pages":
                ref["pages"] = val
                
        ref["authors"] = authors
        if "title" in ref:
            references.append(ref)
            
    return references

def parse_bibliography_file(filename: str, content: str) -> List[Dict[str, Any]]:
    """
    Auto-detects format from filename or content and parses it.
    """
    if filename.endswith(".ris") or "TY  -" in content:
        return parse_ris(content)
    elif filename.endswith(".bib") or "@article" in content.lower() or "@inproceedings" in content.lower():
        return parse_bibtex(content)
    else:
        raise ValueError("Unsupported bibliography file format. Please upload .ris or .bib files.")
