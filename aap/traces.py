"""Observable events only. Call append under the workspace's serialization lock."""
import json
from django.db.models import Max
from aap.models import TraceEvent


def append(result, kind, tool='', arguments=None, success=None, data=None, error=None):
    sequence = (result.events.aggregate(value=Max('sequence'))['value'] or 0) + 1
    return TraceEvent.objects.create(result=result, sequence=sequence, kind=kind, tool=tool,
        arguments=arguments or {}, success=success, data=data or {}, error=error)


def rows(result):
    from .story import event_story
    return [{'sequence': event.sequence, 'timestamp': event.timestamp, 'kind': event.kind,
        'tool': event.tool, 'success': event.success, 'request_sequence': event.data.get('request_sequence'),
        **event_story({'kind': event.kind, 'tool': event.tool, 'arguments': event.arguments,
            'success': event.success, 'data': event.data, 'error': event.error}),
        'arguments': json.dumps(event.arguments, indent=2), 'data': json.dumps(event.data, indent=2),
        'error': json.dumps(event.error, indent=2) if event.error else ''} for event in result.events.all()]
