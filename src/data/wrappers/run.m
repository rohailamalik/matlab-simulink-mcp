function varargout = run(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('run', varargin{:});
end