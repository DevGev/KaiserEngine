from setuptools import find_packages, setup

setup(
    name='kaiserengine',
    description='A game engine developed in python.',
    version='0.1.0',
    url='https://github.com/devgev/KaiserEngine',
    author='Kamal Developers',
    author_email='kamaldevelopers@tutanota.com',
    license='Unlicense',
    keywords='game development',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'audioplayer',
        'pygame',
    ]
)
