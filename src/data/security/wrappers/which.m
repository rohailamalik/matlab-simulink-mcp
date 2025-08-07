function varargout = which(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('which', varargin{:});
end