function varargout = copyfile(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('copyfile', varargin{:});
end