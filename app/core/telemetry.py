import os

from app.core.logging import logger


def init_telemetry(app=None):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
    except Exception as exc:
        logger.warning("telemetry.disabled", extra={"error": str(exc)})
        return

    resource = Resource.create({
        "service.name": os.getenv("SERVICE_NAME", "image-service")
    })
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        logger.info("telemetry.otlp_exporter.enabled", extra={"endpoint": otlp_endpoint})
    else:
        exporter = ConsoleSpanExporter()
        logger.info("telemetry.console_exporter.enabled", extra={"reason": "OTEL_EXPORTER_OTLP_ENDPOINT not configured"})

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument(set_logging_format=True)
    BotocoreInstrumentor().instrument()

    if app is not None:
        FastAPIInstrumentor().instrument_app(app)
