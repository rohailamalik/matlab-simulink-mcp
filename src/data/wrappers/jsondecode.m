function varargout = jsondecode(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('jsondecode', varargin{:});
end