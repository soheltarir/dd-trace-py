from nose.tools import eq_
from pyramid.config import Configurator

from .test_pyramid import PyramidTestCase, PyramidBase


class TestPyramidAutopatch(PyramidTestCase):
    instrument = False


class TestPyramidExplicitTweens(PyramidTestCase):
    instrument = False

    def get_settings(self):
        return {
            'pyramid.tweens': 'pyramid.tweens.excview_tween_factory\n',
        }


class TestPyramidDistributedTracing(PyramidBase):
    instrument = False

    def test_distributed_tracing(self):
        # ensure the Context is properly created
        # if distributed tracing is enabled
        headers = {
            'x-datadog-trace-id': '100',
            'x-datadog-parent-id': '42',
            'x-datadog-sampling-priority': '2',
        }
        self.app.get('/', headers=headers, status=200)
        writer = self.tracer.writer
        spans = writer.pop()
        eq_(len(spans), 1)
        # check the propagated Context
        span = spans[0]
        eq_(span.trace_id, 100)
        eq_(span.parent_id, 42)
        eq_(span.get_metric('_sampling_priority_v1'), 2)


def _include_me(config):
    pass


def test_config_include():
    """ This test makes sure that relative imports still work when the
    application is run with ddtrace-run """
    config = Configurator()
    config.include('._include_me')
