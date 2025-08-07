function varargout = str2func(varargin)
    arg = varargin{1};
    
    % Convert to string if not already
    if ~ischar(arg) && ~isstring(arg)
        error('Invalid argument to str2func');
    end

    % Normalize
    code_str = lower(string(arg));

    % List of dangerous function patterns
    forbidden = [
        "eval", "feval", "system", "unix", "dos", "builtin", "str2func", ...
        "perl", "python", "py.", "javamethod", "javaobject", ...
        "javaclasspath", "javaaddpath", "pyenv", ...
        "matlab.desktop.editor.openDocument", "matlab.desktop.editor.openDocument", ...
        'addpath', 'rmpath','cd','userpath','path','savepath','restoredefaultpath', ...
        'genpath', 'which', 'what', 'matlabroot', 'uigetdir', 'uigetfile', 'uiopen', 'uiputfile'
    ];

    for f = forbidden
        if contains(code_str, f)
            error("Use of %s is not allowed", f);
        end
    end

    % Check for shell command
    if startsWith(strtrim(code_str), "!")
        error("Shell command is not allowed");
    end

    % Otherwise delegate to builtin
    [varargout{1:nargout}] = builtin('str2func', varargin{:});
end