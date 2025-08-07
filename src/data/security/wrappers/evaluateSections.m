function varargout = evaluateSections(varargin)
    check_args('run', varargin);
    [varargout{1:nargout}] = builtin('evaluateSections', varargin{:});
end