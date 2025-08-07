function varargout = jsonencode(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('jsonencode', varargin{:});
end