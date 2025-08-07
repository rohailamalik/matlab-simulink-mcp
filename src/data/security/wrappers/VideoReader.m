function varargout = VideoReader(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('VideoReader', varargin{:});
end