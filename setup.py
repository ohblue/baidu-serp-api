from setuptools import setup, find_packages

setup(
    name='baidu-serp-api',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
    author='Ben Chen',
    author_email='chan@live.cn',
    description='A library to extract data from Baidu SERP and output it as JSON objects',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ohblue/baidu-serp-api',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)