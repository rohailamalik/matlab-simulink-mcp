function varargout = mex(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('mex', varargin{:});
end