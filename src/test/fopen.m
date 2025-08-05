function varargout = X(varargin) % X is the wrapper for built in X function
    check_args('read', varargin); % it should be 'read' or 'write' based on what the function essentially does
    [varargout{1:nargout}] = builtin('X', varargin{:}); % for functions that have outputs
end