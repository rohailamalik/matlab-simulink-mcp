function varargout = open_system(varargin)
    check_args('read', varargin);  % or 'run', depending on your policy
    [varargout{1:nargout}] = builtin('open_system', varargin{:});
end