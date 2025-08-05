function varargout = readmatrix(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('readmatrix', varargin{:});
end