function varargout = rehash(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('rehash', varargin{:});
end