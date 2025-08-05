function varargout = isfolder(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('isfolder', varargin{:});
end