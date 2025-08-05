function varargout = save(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('save', varargin{:});
end