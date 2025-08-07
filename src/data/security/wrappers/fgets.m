function varargout = fgets(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('fgets', varargin{:});
end