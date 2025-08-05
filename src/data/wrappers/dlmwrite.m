function varargout = dlmwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('dlmwrite', varargin{:});
end