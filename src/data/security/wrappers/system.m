function varargout = system(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('system', varargin{:});
end