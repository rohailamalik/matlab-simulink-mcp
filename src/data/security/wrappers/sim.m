function varargout = sim(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('sim', varargin{:});
end