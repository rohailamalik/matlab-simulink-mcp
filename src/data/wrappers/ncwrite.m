function varargout = ncwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('ncwrite', varargin{:});
end