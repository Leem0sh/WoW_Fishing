from setuptools import setup


setup(
    name="wowfishingbot",
    version="0.0.1",
    description="Bot for world of warcraft fishing",
    py_modules=["check", "fishing_v2"],
    package_dir={"": "src"},
    entry_points={"console_scripts": {"fish=fishing_v2:main"}},
)