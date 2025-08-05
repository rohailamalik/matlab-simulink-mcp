function varargout = restoredefaultpath(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('restoredefaultpath', varargin{:});
end