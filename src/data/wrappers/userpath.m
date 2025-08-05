function varargout = userpath(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('userpath', varargin{:});
end