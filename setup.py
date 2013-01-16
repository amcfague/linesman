try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys

install_requires = ["mako", "networkx", "PIL", "pygraphviz", 'Paste', 'WebOb']

# ordereddict is required for versions < 2.7; its included in collections in
# versions 2.7+ and 3.0+
if sys.version_info < (2, 7):
    install_requires.append("ordereddict")

setup(
    name='linesman',
    version='0.2.3',
    description='WSGI Profiling middleware',
    long_description=open("README.rst", "r").read(),
    author='Andrew McFague',
    author_email='redmumba@gmail.com',
    url='http://pypi.python.org/pypi/linesman',
    test_suite='nose.collector',
    tests_require=['nose', 'mock==0.7', 'webtest'],
    zip_safe=False,
    packages=find_packages(exclude=["ez_setup", "linesman.tests", "linesman.tests.*"]),
    package_data = {
        'linesman': ['templates/*', 'media/css/*', 'media/js/*', 'media/images/*'],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
    ],
    entry_points="""
        [paste.filter_app_factory]
        profiler = linesman.middleware:profiler_filter_app_factory
        [paste.filter_factory]
        profiler = linesman.middleware:profiler_filter_factory
    """
)
