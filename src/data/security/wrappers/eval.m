function varargout = eval(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('eval', varargin{:});
end