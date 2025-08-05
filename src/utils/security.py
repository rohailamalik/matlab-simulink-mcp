from pathlib import Path
import re


def check_commands(code: str) -> str | None:
    clean_code = code.lower()

    forbidden_commands = [
        r'\beval\b',
        r'\brehash\b',
        r'\bfeval\b',
        r'\bsystem\b',
        r'\bunix\b',
        r'\bdos\b',
        r'\bbuiltin\b',
        r'\bstr2func\b',
        r'\bperl\b',
        r'\bpython\b',
        r'\bpyenv\b',
        r'\bpy\.',          
        r'\bjavaobject\b',
        r'\bjavamethod\b',
        r'\bjavamethodedt\b',
        r'\bjavaclasspath\b',
        r'\bjavaaddpath\b',
        r'\bmatlab\.desktop\.editor\.opendocument\b',
        r'\bmatlab\.desktop\.editor\.save\b',
        r'\baddpath\b',
        r'\brmpath\b',
        r'\bcd\b',
        r'\buserpath\b',
        r'\bpath\b',
        r'\bsavepath\b',
        r'\brestoredefaultpath\b',
        r'\bgenpath\b',
        r'\bwhich\b',
        r'\bwhat\b',
        r'\bmatlabroot\b',
        r'\buigetdir\b',
        r'\buigetfile\b', 
        r'\buiopen\b', 
        r'\buiputfile\b'
    ]

    if re.search(r'^\s*!', code, re.MULTILINE):
        return "Use of system shell command (!) is not allowed."

    for flag in forbidden_commands:
        if re.search(flag, clean_code):
            return f"Use of {re.sub(r'^\\b|\\b$', '', flag).replace(r'\.', '.')} is not allowed"
        
    return None


def check_paths(code: str) -> str | None:
    string_literals = re.findall(r"(?:'[^']*'|\"[^\"]*\")", code)

    for s in string_literals:
        s = s[1:-1]  # Strip quotes

        # Using Path().is_absolute() instead of os.path.isabs
        if Path(s).is_absolute():
            return "Absolute paths are not allowed. Only files on MATLAB path are accessible."

        # Using parts to check for directory traversal
        if any(part == ".." for part in Path(s).parts):
            return "Paths with .. are not allowed. Only files on MATLAB path are accessible."

        # Wildcard check remains the same
        if "*" in s or "?" in s:
            return "Paths with * or ? are not allowed."

    return None


def check_code(code: str) -> str | None:
    return check_commands(code) or check_paths(code)