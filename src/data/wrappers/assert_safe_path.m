function assert_safe_path(path, mode)
% Checks and blocks if the path argument is an absolute path etc.
% Then gets the wrapper directory, current working directory.
% If the targeted file is in wrapper directory, it can only be run
% For current working directory, it can read, write and run
% For other files on the path, it can only read and run



    if is_forbidden_path(path)
        error("Access denied for forbidden path: %s", path);
    end

    wrapper_path = getFuncPath();
    cwd = builtin('which');  
    path = builtin('which', (path));


    if startsWith(path, cwd)
        in_cwd = True;
    elseif startsWith(path, wrapper_path)
        in_wpath = True;
    else
        in_path = True;
    end 

    switch mode
        case 'run'
            allowed = in_cwd || in_path || in_wpath;
        case 'read'
            allowed = in_cwd  || in_path;
        case 'write'
            allowed = in_cwd;
        otherwise
            allowed = false;
    end

    if ~allowed
        error("Access denied for path: %s (mode: %s)", path, mode);
    end
end


function is_bad = is_forbidden_path(path_str)
    path_str = string(path_str);

    % Define forbidden patterns
    is_abs = is_absolute_path(path_str);
    has_dotdot = contains(path_str, "..");
    has_wildcard = contains(path_str, "*");

    is_bad = is_abs || has_dotdot || has_wildcard;
end

function tf = is_absolute_path(p)
% Check for Windows-style (e.g., C:\...) or Unix-style (/...)
tf = startsWith(p, "/") || ~isempty(regexp(p, "^[a-zA-Z]:[\\/]", "once"));
end

function funcDir = getFuncPath()
% Get full path of this function
fullPath = mfilename('fullpath');
[funcDir, ~, ~] = fileparts(fullPath);
end 