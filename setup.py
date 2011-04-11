try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='linesman',
    version='0.1',
    description='Profiling middleware',
    author='Andrew McFague',
    author_email='redmumba@gmail.com',
    url='',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "mako",
        "networkx",
        "ordereddict",
        "PIL"
    ]
)
