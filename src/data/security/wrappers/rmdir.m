function varargout = rmdir(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('rmdir', varargin{:});
end