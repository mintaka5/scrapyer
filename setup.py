from setuptools import setup, find_packages

setup(
    name="scrapyer",
    author="Chris Walsh",
    author_email="chris.is.rad@pm.me",
    classifiers=[],
    description="a web page scraper",
    license="MIT",
    version="0.0.1",
    url="https://github.com/mintaka5/scrapyer",
    packages=find_packages(),
    install_requires=[
        
    ],
    entry_points={
        'console_scripts': [
            'scrapyer = scrapyer.main:boot_up'
        ]
    }
)