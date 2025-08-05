function varargout = evalin(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('evalin', varargin{:});
end