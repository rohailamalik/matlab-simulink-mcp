function varargout = what(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('what', varargin{:});
end