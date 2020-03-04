from setuptools import setup, find_packages
from sys import version_info


def install_requires():
    requires = [
        'traitlets>=4.1',
        'six>=1.9.0',
        'pyyaml>=3.11',
    ]
    if (version_info.major, version_info.minor) < (3, 4):
        requires.append('singledispatch>=3.4.0')
    return requires


def extras_require():
    return {
        'test': [
            'tox',
            'pytest>=2.8.5',
            'pytest-cov>=1.8.1',
            'pytest-pep8>=1.0.6',
            'click>=6.0',
        ],
    }


def main():
    setup(
        name='straitlets',
        # remember to update straitlets/__init__.py!
        version='0.3.3',
        description="Serializable IPython Traitlets",
        author="Quantopian Team",
        author_email="opensource@quantopian.com",
        packages=find_packages(include='straitlets.*'),
        include_package_data=True,
        zip_safe=True,
        url="https://github.com/quantopian/serializable-traitlets",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Framework :: IPython',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python',
        ],
        install_requires=install_requires(),
        extras_require=extras_require()
    )


if __name__ == '__main__':
    main()
