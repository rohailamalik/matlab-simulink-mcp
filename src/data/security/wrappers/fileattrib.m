function varargout = fileattrib(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('fileattrib', varargin{:});
end