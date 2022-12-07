import os

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider(resource=Resource({
    'telemetry.sdk.language': 'python',
    'telemetry.sdk.name': 'opentelemetry',
    'telemetry.sdk.version': '1.10.0',
    'service.name': 'Auth API'
}))

console_processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(console_processor)

jaeger_processor = BatchSpanProcessor(
    JaegerExporter(
        agent_host_name=os.getenv('OPENTELEMETRY_JAEGER_HOST', 'localhost'),
        agent_port=int(os.getenv('OPENTELEMETRY_JAEGER_PORT', 6831)),
    )
)
provider.add_span_processor(jaeger_processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)
