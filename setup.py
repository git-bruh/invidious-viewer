import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="invidious-viewer",
    version="0.0.4",
    packages=["invidious_viewer"],
    scripts=["invidious"],
    description="Python application to watch YouTube videos through the "
    "Invidious API, in the terminal!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["video", "music", "audio", "youtube", "invidious"],
    classifiers=[
        "Topic :: Utilities", "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Multimedia :: Video", "Operating System :: POSIX :: Linux",
        "Intended Audience :: End Users/Desktop",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    url="https://github.com/lwritebadcode/invidious-viewer",
    install_requires=["python-mpv >= 0.5.2"],
    python_requires=">=3.6")
