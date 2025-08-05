function varargout = open(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('open', varargin{:});
end