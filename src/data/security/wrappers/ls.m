function varargout = ls(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('ls', varargin{:});
end