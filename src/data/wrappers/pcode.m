function varargout = pcode(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('pcode', varargin{:});
end