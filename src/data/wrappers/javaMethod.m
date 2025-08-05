function varargout = javaMethod(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('javaMethod', varargin{:});
end