from setuptools import find_packages, setup
import versioneer

commands = versioneer.get_cmdclass().copy()

pkgname = 'protosanity'

data_files = [
]

package_data = [
]



packages = find_packages(exclude=['src', 'src.*', 'common', '*/protobuf'])
print('Packages:', packages)

# common dependencies
# todo: fully test unified dependencies
deps = [
    'typing',
    'vprint',
    'pyyaml',
    'grpcio>=1.22',
    'grpcio-tools',
    'protobuf>=3.9',
]

setup(
    name=pkgname,
    author="Michael McDermott",
    url="https://github.com/xkortex/protosanity",
    version=versioneer.get_version(),
    script_name='setup.py',
    python_requires='>3.5',
    zip_safe=False,
    packages=packages,
    install_requires=deps,
    data_files=data_files,
    include_package_data=True,
    extras_require={
    },
    cmdclass=commands,
)
