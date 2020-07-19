# invidious-viewer

Simple python application to watch YouTube videos through the <a href="https://github.com/iv-org/invidious">invidio.us</a> API.

# Usage
1. Clone the repository
2. Install the requirements

```pip install -r requirements.txt```
3. Run the program

```python3 main.py```

Additional usage options :
```
usage: main.py [-h] [-u URL] [-n] [-p]

optional arguments:
  -h, --help         show this help message and exit
  -u URL, --url URL  Specify link to play [Video/Playlist]
  -n, --no-video     Play audio only
  -p, --popular      View popular videos (Main invidious page)
```
