function varargout = matlabroot(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('matlabroot', varargin{:});
end