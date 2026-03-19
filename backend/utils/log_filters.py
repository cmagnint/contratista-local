import threading
import logging

_local = threading.local()

def set_request(request):
    _local.request = request

class RequestFilter(logging.Filter):
    def filter(self, record):
        request = getattr(_local, 'request', None)
        record.endpoint = f"{request.method} {request.path}" if request else "N/A"
        return True