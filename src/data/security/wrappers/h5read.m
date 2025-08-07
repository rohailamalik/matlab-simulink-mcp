function varargout = h5read(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('h5read', varargin{:});
end