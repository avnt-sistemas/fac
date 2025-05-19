from setuptools import setup, find_packages

setup(
    name="flutter-app-creator",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2>=3.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "colorama>=0.4.4",
    ],
    entry_points="""
        [console_scripts]
        fac=main:cli
    """,
    package_data={
        "": ["templates/**/*"],
    },
    author="Anthero Vieira Neto",
    author_email="antherovn@gmail.com",
    description="Flutter App Creator - Generate full-featured Flutter applications from YAML",
    keywords="flutter, code generator, yaml",
    python_requires=">=3.8",
)