from setuptools import setup
from sys import version_info


def install_requires():
    requires = ['traitlets>=4.0', 'pytest>=2.8.5', 'six>=1.9.0']
    if (version_info.major, version_info.minor) < (3, 4):
        requires.append('singledispatch>=3.4.0')
    return requires


def main():
    setup(
        name='straitlets',
        version='0.0.1',
        description="Serializable IPython Traitlets",
        author="Scott Sanderson",
        author_email="ssanderson@quantopian.com",
        packages=[
            'straitlets',
        ],
        include_package_data=True,
        zip_safe=True,
        url="https://github.com/quantopian/serializable-traitlets",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Framework :: IPython',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python',
        ],
        install_requires=install_requires(),
    )


if __name__ == '__main__':
    main()
