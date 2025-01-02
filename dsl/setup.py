from setuptools import setup, find_packages

setup(
    name="shipping-dsl",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'pydantic',
        'flask-sqlalchemy'
    ],
)
