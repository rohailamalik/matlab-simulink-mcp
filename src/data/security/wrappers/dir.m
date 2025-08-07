function varargout = dir(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('dir', varargin{:});
end