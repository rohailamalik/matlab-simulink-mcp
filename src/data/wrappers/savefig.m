function varargout = savefig(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('savefig', varargin{:});
end