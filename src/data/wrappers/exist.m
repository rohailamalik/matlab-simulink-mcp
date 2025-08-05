function varargout = exist(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('exist', varargin{:});
end