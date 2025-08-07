function varargout = delete(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('delete', varargin{:});
end