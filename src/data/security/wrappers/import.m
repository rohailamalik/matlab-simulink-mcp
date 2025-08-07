function varargout = import(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('import', varargin{:});
end