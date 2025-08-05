function varargout = h5write(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('h5write', varargin{:});
end