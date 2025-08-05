function varargout = diary(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('diary', varargin{:});
end