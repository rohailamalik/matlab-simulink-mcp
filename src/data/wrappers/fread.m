function varargout = fread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('fread', varargin{:});
end