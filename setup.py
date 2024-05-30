from setuptools import setup, find_packages

def get_version():
    try:
        from subprocess import check_output
        version = check_output(['git', 'describe', '--tags']).decode().strip()
        return version
    except Exception as e:
        print("Error getting version from Git tags:", e)
        return '0.1' 
setup(
    name='baidu-serp-api',
    version=get_version(),
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
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
