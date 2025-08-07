function varargout = javaclasspath(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('javaclasspath', varargin{:});
end