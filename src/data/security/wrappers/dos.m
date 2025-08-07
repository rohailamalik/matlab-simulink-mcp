function varargout = dos(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('dos', varargin{:});
end