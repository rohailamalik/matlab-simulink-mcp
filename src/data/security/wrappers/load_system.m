function varargout = load_system(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('load_system', varargin{:});
end