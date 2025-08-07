function varargout = calllib(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('calllib', varargin{:});
end