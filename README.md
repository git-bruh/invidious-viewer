# invidious-viewer
# Installation
`pip install invidious-viewer --user`

Add ~/.local/bin to PATH by adding the following to your ~/.bashrc :

`PATH=$HOME/.local/bin:$PATH`

This will allow you to launch invidious-viewer by using the `invidious` command in the terminal. 

# Usage
Note :
The MPV player is required, along with `libmpv.so` which should be provided by your distribution's package manager.

Default behaviour :
Wait for the user to enter a search term and return all results from the first page of results.

Additional usage options :
```
usage: invidious [-h] [-i INSTANCE] [-r RESULTS] [-n]
                 [-u URL | -c CHANNEL | -p | -t]

optional arguments:
  -h, --help            show this help message and exit
  -i INSTANCE, --instance INSTANCE
                        Specify a different invidious instance
  -r RESULTS, --results RESULTS
                        Return specific number of results
  -n, --no-video        Play audio only
  -u URL, --url URL     Specify link to play [Video/Playlist]
  -c CHANNEL, --channel CHANNEL
                        View videos from a specific channel
  -p, --popular         View popular videos (Default invidious page)
  -t, --trending        View trending videos
```

Example :
`invidious --channel "linus tech tips" --instance https://invidious.snopyta.org --results 5 --no-video`

Returns the first 5 results from the LTT channel, disables video playback, and fetches all URLs from the <a href="https://invidious.snopyta.org/">Snopyta instance</a>.

# Screenshots
![ScreenShot](screenshots/LTT.png)
![ScreenShot](screenshots/Popular.png)
![ScreenShot](screenshots/Playlist.png)
