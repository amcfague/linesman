try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='linesman',
    version='0.1',
    description='WSGI Profiling middleware',
    author='Andrew McFague',
    author_email='redmumba@gmail.com',
    url='',
    packages=find_packages(exclude=["ez_setup"]),
    package_data = {
        'linesman': ['templates/*', 'media/*'],
    },
    zip_safe=False,
    install_requires=[
        "mako",
        "networkx",
        "ordereddict",
        "PIL"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    entry_points="""
        [paste.filter_app_factory]
        profiler = linesman.middleware:profiler_filter_app_factory

        [paste.filter_factory]
        profiler = linesman.middleware:profiler_filter_factory
    """
)
