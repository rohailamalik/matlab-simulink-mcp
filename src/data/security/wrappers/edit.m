function varargout = edit(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('edit', varargin{:});
end