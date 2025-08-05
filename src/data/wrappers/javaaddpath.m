function varargout = javaaddpath(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('javaaddpath', varargin{:});
end