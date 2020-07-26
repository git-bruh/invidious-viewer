import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="invidious-viewer",
    version="0.0.1",
    packages=["invidious_viewer"],
    scripts=["invidious"],
    description="Python application to watch YouTube videos through the "
    "Invidious API, in the terminal!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lwritebadcode/invidious-viewer",
    install_requires=["python-mpv >= 0.5.2"],
    python_requires=">=3.6")
