function varargout = cd(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('cd', varargin{:});
end