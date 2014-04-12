from setuptools import setup, find_packages
import everbean

long_description = open('README.md').read()

setup(
    name='Everbean',
    author='Messense Lv',
    author_email='messense@icloud.com',
    version=everbean.__version__,
    description='Everbean - sync notes from book.douban.com to Evernote',
    keywords="everbean, douban, evernote, note, book",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open("requirements.txt").readlines(),
    tests_require=['nose'],
    test_suite='nose.collector',
)
