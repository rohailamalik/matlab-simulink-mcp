function varargout = fopen(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('fopen', varargin{:});
end