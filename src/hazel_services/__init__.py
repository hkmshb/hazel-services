# pylint: disable=C0330
import pkg_resources
from wired import ServiceRegistry
from zope.interface import Interface


def get_version():  # pragma: no cover
    """Returns the package version details.
    """
    package = pkg_resources.require('hazel-services')
    return package[0].version


class SingletonServiceWrapper:
    def __init__(self, service):
        self.service = service

    def __call__(self, context, scope):
        return self.service


class ProxyFactory:
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, container):
        scope = None
        return self.factory(container.context, scope)


class _RegistrarBase:
    """Represents the base class for classes able to register and manage
    services and function as an IoC object.

    This is an internal class and not meant for directy use in code. It
    was provided as a base class to aid unit testing.
    """

    def __init__(self):
        self._registry = ServiceRegistry()

    @property
    def services(self):
        key = '_container'
        if not hasattr(self, key):
            container = self._registry.create_container()
            setattr(self, key, container)
        return getattr(self, key)

    def register_service(
        self, service, iface=Interface, context=None, name=''
    ):
        service_factory = SingletonServiceWrapper(service)
        self.register_service_factory(
            service_factory, iface, context=context, name=name
        )

    def register_service_factory(
        self, service_factory, iface=Interface, context=None, name=''
    ):
        self._registry.register_factory(
            ProxyFactory(service_factory), iface, context=context, name=name
        )

    def find_service_factory(self, iface, context=None, name=''):
        factory = self._registry.find_factory(
            iface, context=context, name=name
        )
        if not factory:
            raise LookupError('could not find registered service')
        if isinstance(factory, ProxyFactory):
            return factory.factory
        return factory

    def find_service(self, iface, context=None, name=''):
        return self.services.get(iface, context=context, name=name)


class SingletonMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        cls.__instance = None
        original_new = cls.__new__

        def meta_new(cls, *args, **kwargs):
            if not cls.__instance:
                cls_obj = original_new(cls, *args, **kwargs)
                cls.__instance = cls_obj
            return cls.__instance

        # replace `__new__` method
        cls.__new__ = staticmethod(meta_new)


class Registrar(_RegistrarBase, metaclass=SingletonMeta):
    """A singleton class for registering and managing services.
    """
