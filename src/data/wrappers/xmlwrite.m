function varargout = xmlwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('xmlwrite', varargin{:});
end