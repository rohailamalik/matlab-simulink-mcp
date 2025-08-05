function varargout = realpath(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('realpath', varargin{:});
end