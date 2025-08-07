function varargout = javaObject(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('javaObject', varargin{:});
end