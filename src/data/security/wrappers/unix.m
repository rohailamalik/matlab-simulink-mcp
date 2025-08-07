function varargout = unix(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('unix', varargin{:});
end