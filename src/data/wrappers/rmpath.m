function varargout = rmpath(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('rmpath', varargin{:});
end