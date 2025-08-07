function varargout = ncread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('ncread', varargin{:});
end