function varargout = VideoWriter(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('VideoWriter', varargin{:});
end