from typing import Optional

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def trace(span_name: str, tags: Optional[dict] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                if tags:
                    for k in tags.keys():
                        span.set_attribute(k, tags[k])
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
