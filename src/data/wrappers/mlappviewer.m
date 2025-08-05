function varargout = mlappviewer(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('mlappviewer', varargin{:});
end