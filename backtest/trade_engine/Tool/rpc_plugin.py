import os
import logging
import asyncio
import threading
import time
from functools import wraps, lru_cache
from typing import Dict, Any, Callable, TypeVar, Type, List


import opentracing
from opentracing.propagation import Format
from jaeger_client import Config

logger = logging.getLogger(__name__)


JAEGER_HOST = "1111111111111111111111111"


TRACERS: Dict[str, Any] = {}


@lru_cache()
def get_service_name():
    service_name = "te"
    app_name = "default"
    dyno = os.getenv('DYNO', 'default.1')
    dyno = dyno.split('.')[0]
    return f"{service_name}__{app_name}_{dyno}"


def get_tracer(service_name=None, asyncio_enabled=False):
    service_name = service_name or get_service_name()
    if service_name in TRACERS:
        return TRACERS[service_name]

    kwargs = dict(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'local_agent': {
                'reporting_host': JAEGER_HOST,
                # 'reporting_port': '5775',
            },
        },
        service_name=service_name,
    )

    if asyncio_enabled:
        # asyncio loop is running in this thread!
        from opentracing.scope_managers.asyncio import AsyncioScopeManager
        kwargs['scope_manager'] = AsyncioScopeManager()

    config = Config(
        **kwargs
    )
    config.initialize_tracer()
    return opentracing.tracer


class RPCClientTracingMixin():
    def __init__(self, *args, service_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        # 创建跟踪器
        self._tracer = get_tracer(service_name=service_name)

    def __getattr__(self, method):
        orig_method = super().__getattr__(method)
        if method.startswith('_') or method in ['close']:
            return orig_method

        @wraps(orig_method)
        def wrapper(*args, **kwargs):
            span = self._tracer.active_span
            with self._tracer.start_span(f'{self.__class__.__name__}#{method}', child_of=span) as new_span:  # as span:
                _span_ctx = {}
                self._tracer.inject(new_span, Format.TEXT_MAP, _span_ctx)
                ret = orig_method(*args, _span_ctx=_span_ctx, **kwargs)
                return ret

        return wrapper



class RPCClientKwargsMixin():
    def __getattr__(self, method):
        orig_method = super().__getattr__(method)
        if method.startswith('_') or method in ['close']:
            return orig_method

        @wraps(orig_method)
        def wrapper(*args, **kwargs):
            data = dict(
                args=args, kwargs=kwargs,
                meta=dict(
                    source_name=get_service_name(), started_at_ms=int(time.time() * 1000)
                )
            )
            return orig_method(data)
        return wrapper
