function varargout = audioread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('audioread', varargin{:});
end