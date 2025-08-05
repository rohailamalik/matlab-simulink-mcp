function varargout = unloadlibrary(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('unloadlibrary', varargin{:});
end