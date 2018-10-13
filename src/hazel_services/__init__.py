import pkg_resources


def get_version():
    """Returns the package version details.
    """
    package = pkg_resources.require('hazel-services')
    return package[0].version
