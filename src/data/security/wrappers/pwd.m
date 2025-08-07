function varargout = pwd(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('pwd', varargin{:});
end