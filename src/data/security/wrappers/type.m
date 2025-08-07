function varargout = type(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('type', varargin{:});
end