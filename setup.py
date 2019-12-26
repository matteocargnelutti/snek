from distutils.core import setup

setup(
    name = 'snek-framework',
    packages = ['snek'],
    version = '0.1.0',
    license='Apache-2.0',
    description = ' A dead-simple static-site generator for Python',
    author = 'Matteo Cargnelutti',
    author_email = 'matteo.cargnelutti@gmail.com',
    url = 'https://github.com/matteocargnelutti/snek',
    download_url = 'https://github.com/matteocargnelutti/snek/raw/master/dist/snek-0.1.0.tar.gz',
    keywords = ['framework', 'static-site generator', 'web'],
    install_requires=[
        'libsass',
        'mako',
        'python-frontmatter',
        'markdown'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)