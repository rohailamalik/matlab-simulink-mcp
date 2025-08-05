function varargout = load(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('load', varargin{:});
end