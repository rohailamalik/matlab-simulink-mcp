function varargout = mkdir(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('mkdir', varargin{:});
end