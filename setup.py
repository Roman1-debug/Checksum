from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="checksum",
    version="1.0.0",
    author="Roman",
    author_email="hisecids@gmail.com",
    description="Professional file integrity verification tool for cybersecurity professionals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Roman1-debug/checksum",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "checksum=checksum.cli:main",
        ],
    },
    keywords="checksum, hash, verification, integrity, security, cybersecurity, md5sum, sha256sum",
)
