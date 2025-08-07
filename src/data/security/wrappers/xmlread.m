function varargout = xmlread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('xmlread', varargin{:});
end