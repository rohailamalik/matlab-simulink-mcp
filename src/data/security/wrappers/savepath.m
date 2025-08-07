function varargout = savepath(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('savepath', varargin{:});
end