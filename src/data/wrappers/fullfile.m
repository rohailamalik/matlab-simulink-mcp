function varargout = fullfile(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('fullfile', varargin{:});
end