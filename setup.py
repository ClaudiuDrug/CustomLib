from setuptools import setup

setup(
    name='customlib',
    version='2.0.0',
    packages=['customlib'],
    license='MIT License',
    author='Claudiu DRUG',
    author_email='claudiu.drug@outlook.com',
    description='Custom library.',
    install_requires=[
        "cryptography==36.0.1",
        "keyring==23.5.0",
        "pywin32==303",
    ],
    python_requires=">=3.7",
)
