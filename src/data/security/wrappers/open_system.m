function varargout = open_system(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('open_system', varargin{:});
end