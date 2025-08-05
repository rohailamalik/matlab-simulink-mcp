function varargout = fwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('fwrite', varargin{:});
end