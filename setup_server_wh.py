# ====================== Распространение приложений ===========================
# ---------------------------- Создание пакета --------------------------------

#   --------------------- Использование setuptools -------------------------

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup_server_wh.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='Messager server',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='GNU General Public License v3.0',
    description='My messenger',
    long_description=README,
    url='https://github.com/dmitricus/python-message-lessons',
    author='DanteOnline',
    author_email='dmitricus@ya.ru',
    classifiers = [],
    install_requires=['pycryptodome', 'pycryptodomex'],
    entry_points={
        'console_scripts': [
            'messenger = messenger.server.src.server:main',
        ]
    },
)