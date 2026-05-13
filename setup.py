from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="artiq_thorlabs_ellX",
    install_requires=required,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "aqctl_artiq_thorlabs_ellX = artiq_thorlabs_ellX.aqctl_artiq_thorlabs_ellX:main",
        ],
    },
)