function varargout = readtable(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('readtable', varargin{:});
end