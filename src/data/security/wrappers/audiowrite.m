function varargout = audiowrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('audiowrite', varargin{:});
end