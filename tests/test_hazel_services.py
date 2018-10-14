# pylint: disable=protected-access
import pytest
from zope.interface import Interface
from hazel_services import _RegistrarBase, Registrar


class TestRegistrar:
    def test_singleton_nature(self):
        reg1 = Registrar()
        reg2 = Registrar()
        assert reg1 == reg2
        assert reg1._registry == reg2._registry

    def test_resolve_service_factory_by_type(self):
        reg = DummyRegistrar()
        reg.register_service_factory(lambda c, s: 'foo-factory', IFooService)
        reg.register_service_factory(lambda c, s: 'bar-factory', IBarService)

        factory = reg.find_service_factory(IFooService)
        assert factory is not None
        factory2 = reg.find_service_factory(IBarService)
        assert factory2 is not None
        assert factory is not factory2

    def test_resolve_service_by_type(self):
        reg = DummyRegistrar()
        reg.register_service(DummyService('bar'), IBarService)
        reg.register_service(DummyService('foo'), IFooService)

        srv = reg.find_service(IFooService)
        assert srv() == 'foo'
        srv2 = reg.find_service(IBarService)
        assert srv2() == 'bar'

    def test_resolve_service_by_name(self):
        reg = DummyRegistrar()
        reg.register_service(DummyService('foo'), IFooService, name='foo')
        reg.register_service(DummyService('bar'), IFooService, name='bar')

        srv = reg.find_service(IFooService, name='foo')
        assert srv() == 'foo'
        srv = reg.find_service(IFooService, name='bar')
        assert srv() == 'bar'

    @pytest.mark.skip('Needs to be revisited')
    def test_resolve_service_by_context(self):
        reg = DummyRegistrar()
        reg.register_service(DummyService('foo'), IFooService)
        reg.register_service(DummyService('bar'), IFooService, context=Leaf)

        srv = reg.find_service(IFooService)
        assert srv() == 'foo'
        srv = reg.find_service(IFooService, context=Leaf)
        assert srv() == 'bar'


class Leaf:
    pass


class IFooService(Interface):
    pass


class IBarService(Interface):
    pass


class DummyService:
    def __init__(self, result):
        self.result = result

    def __call__(self):
        return self.result


class DummyServiceFactory:
    def __init__(self, result):
        self.result = result

    def __call__(self, context):
        return DummyService(self.result)


class DummyRegistrar(_RegistrarBase):
    pass
