function varargout = save_system(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('save_system', varargin{:});
end