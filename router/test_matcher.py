import pytest

from router.route import Route
from router.matcher import Matcher


class FakeRequest:
    def __init__(self, method, path):
        self.method = method
        self.path = path

    @classmethod
    def from_str(cls, value):
        return cls(*value.split())


def route_from_str(value):
    pattern, *methods = value.split()
    if methods:
        methods = methods[0].split(',')

    return Route(pattern, 0, methods=methods)


@pytest.fixture
def matcher():
    routes = [
        '/',
        '/test GET',
        '/hi/{there} POST,DELETE',
        '/{oh}/{dear} PATCH'
    ]

    return Matcher([route_from_str(r) for r in routes])


def parametrize_request_and_route(cases):
    return pytest.mark.parametrize(
        'req,route',
        ((FakeRequest.from_str(req), route_from_str(route))
         for req, route in cases),
         ids=[req + '-' + route for req, route in cases])


@parametrize_request_and_route([
    ('GET /', '/'),
    ('POST /', '/'),
    ('GET /test', '/test GET'),
    ('DELETE /hi/jane', '/hi/{there} POST,DELETE'),
    ('PATCH /lets/dance', '/{oh}/{dear} PATCH')
])
def test_matcher(matcher, req, route):
    assert matcher.match_request(req) == route


def parametrize_request(requests):
    return pytest.mark.parametrize(
        'req', (FakeRequest.from_str(r) for r in requests), ids=requests)


@parametrize_request([
    'POST /test',
    'GET /test/',
    'GET /hi/jane',
    'POST /hi/jane/',
    'GET /abc'
])
def test_matcher_not_found(matcher, req):
    assert matcher.match_request(req) is None