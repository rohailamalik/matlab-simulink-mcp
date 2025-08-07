function varargout = movefile(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('movefile', varargin{:});
end