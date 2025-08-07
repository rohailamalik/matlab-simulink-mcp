function varargout = fclose(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('fclose', varargin{:});
end