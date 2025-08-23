functions = {
    'VideoReader': 'read',
    'VideoWriter': 'write',
    'audioread': 'read',
    'audiowrite': 'write',
    'calllib': 'read',
    'copyfile': 'read',
    'csvread': 'read',
    'csvwrite': 'write',
    'delete': 'write',
    'diary': 'write',
    'dir': 'read',
    'dlmwrite': 'write',
    'dos': 'run',
    'edit': 'read',
    'eval': 'run',
    'evalin': 'run',
    'evaluateSections': 'run',
    'fclose': 'write',
    'feval': 'run',
    'fgetl': 'read',
    'fgets': 'read',
    'fileread': 'read',
    'fopen': 'write',
    'fprintf': 'write',
    'fread': 'read',
    'fscanf': 'read',
    'fwrite': 'write',
    'h5read': 'read',
    'h5write': 'write',
    'import': 'read',
    'imread': 'read',
    'imwrite': 'write',
    'load': 'read',
    'load_system': 'read',
    'mcc': 'run',
    'mex': 'run',
    'mkdir': 'write',
    'movefile': 'write',
    'ncread': 'read',
    'ncwrite': 'write',
    'netcdf.create': 'write',
    'netcdf.open': 'read',
    'open': 'read',
    'open_system': 'read',
    'openfig': 'read',
    'pcode': 'write',
    'readmatrix': 'read',
    'readtable': 'read',
    'rmdir': 'write',
    'run': 'run',
    'save': 'write',
    'save_system': 'write',
    'saveas': 'write',
    'savefig': 'write',
    'sim': 'run',
    'textscan': 'read',
    'type': 'read',
    'writematrix': 'write',
    'writetable': 'write',
    'xlsread': 'read',
    'xlswrite': 'write',
    'xmlread': 'read',
    'xmlwrite': 'write'
 }

import os

# Prepare folder to store wrapper files
output_folder = os.path.join(os.getcwd(), "safety_wrappers")
os.makedirs(output_folder, exist_ok=True)

# Generate wrapper .m files for valid identifiers
for func, operation in functions.items():
    if func.isidentifier():
        code_lines = [
            f"function varargout = {func}(varargin)",
            f"    check_args('{operation}', varargin);",
            f"    [varargout{{1:nargout}}] = builtin('{func}', varargin{{:}});",
            f"end"
        ]
        filepath = os.path.join(output_folder, f"{func}.m")
        with open(filepath, 'w') as f:
            f.write("\n".join(code_lines))

print(filepath)