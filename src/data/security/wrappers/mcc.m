function varargout = mcc(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('mcc', varargin{:});
end