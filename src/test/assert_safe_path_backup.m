function assert_safe_path(path, mode)
%ASSERT_SAFE_PATH Enforces sandbox restrictions for file access.
%   path (string): Target file path.
%   mode (string): 'read', 'write', 'delete', or 'run'

    % Dynamically determine the sandbox root as current working directory
    cwd = realpath(pwd);  % full resolved path of cwd
    path = realpath(path);         % full resolved path of input

    % Safe directories that can be used for running code
    SAFE_PATHS = {
        cwd,
        fullfile(cwd, 'sandbox_wrappers'),
        fullfile(cwd, 'matlab_helpers')
    };

    % Determine if the path is within allowed regions
    in_cwd = startsWith(path, cwd);
    on_safe_path = any(startsWith(path, SAFE_PATHS));
    in_matlabroot = startsWith(path, matlabroot);

    switch mode
        case 'read'
            allowed = in_cwd;
        case 'write'
            allowed = in_cwd;
        case 'delete'
            allowed = false;
        case 'run'
            allowed = in_cwd || on_safe_path;  % not allowing matlabroot
        otherwise
            allowed = false;
    end

    if ~allowed
        error("[SANDBOX] Access denied for path: %s (mode: %s)", path, mode);
    end
end