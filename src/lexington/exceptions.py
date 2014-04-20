class LexingtonException(Exception):
    pass

class NoRouteMatchedError(LexingtonException):
    pass

class NoViewForRouteError(LexingtonException):
    pass
