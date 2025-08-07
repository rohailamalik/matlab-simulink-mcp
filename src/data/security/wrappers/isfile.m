function varargout = isfile(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('isfile', varargin{:});
end