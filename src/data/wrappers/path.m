function varargout = path(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('path', varargin{:});
end