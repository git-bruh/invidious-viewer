# invidious-viewer
# Installation
`pip install --user invidious-viewer`

For installing the git version:

`pip install --user -U git+https://github.com/git-bruh/invidious-viewer.git`

Add `~/.local/bin` to `PATH` by adding the following to your `~/.bashrc`:

`PATH=$HOME/.local/bin:$PATH`

This will allow invidious-viewer to be launched by using the `invidious` command in the terminal. 

# Usage
Note:
The MPV player is required, along with `libmpv.so` which should be provided by your distribution's package manager. Compiling MPV with LuaJIT support may also be required on a source-based distribution.

Default behaviour:
Return the first page of results for the entered search term.

Additional usage options:
```
usage: invidious_viewer.py [-h] [-i INSTANCE] [-r RESULTS] [-v]
                           [-u URL | -c CHANNEL | -p | -t]

optional arguments:
  -h, --help            show this help message and exit
  -i INSTANCE, --instance INSTANCE
                        Specify a different invidious instance
  -r RESULTS, --results RESULTS
                        Return specific number of results
  -v, --video           Toggle video playback
  -u URL, --url URL     Specify link or ID to play [Video/Playlist]
  -c CHANNEL, --channel CHANNEL
                        View videos from a specific channel
  -p, --popular         View popular videos (Default invidious page)
  -t, --trending        View trending videos
```

Config File:
```
{
    "instance": "https://invidious.snopyta.org",
    "play_video": true,
    "captions": false
}
```

The instance can be permanently specified in the config file, along with the video playback and closed captions preference.

The suggested alternative instance is https://invidious.13ad.de as all the required endpoints are provided.

Usage example:
`invidious --channel "Channel Name" --instance https://invidious.snopyta.org --results 5`

Returns the first 5 results from the specified channel and fetches all URLs from the <a href="https://invidious.snopyta.org/">Snopyta instance</a>.

# Screenshots
![ScreenShot](https://raw.githubusercontent.com/git-bruh/invidious-viewer/master/screenshots/Search.png)
![ScreenShot](https://raw.githubusercontent.com/git-bruh/invidious-viewer/master/screenshots/Popular.png)
![ScreenShot](https://raw.githubusercontent.com/git-bruh/invidious-viewer/master/screenshots/Playlist.png)
