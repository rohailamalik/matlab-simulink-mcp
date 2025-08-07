function varargout = loadlibrary(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('loadlibrary', varargin{:});
end