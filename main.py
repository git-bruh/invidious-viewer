import urllib.request
import argparse
import datetime
import json
import mpv

string = r'''
  _____            _     _ _
 |_   _|          (_)   | (_)
   | |  _ ____   ___  __| |_  ___  _   _ ___
   | | | '_ \ \ / / |/ _` | |/ _ \| | | / __|
  _| |_| | | \ V /| | (_| | | (_) | |_| \__ \
 |_____|_| |_|\_/ |_|\__,_|_|\___/ \__,_|___/
'''

parser = argparse.ArgumentParser()
parser.add_argument("-u",
                    "--url",
                    help="Specify link to play [Video/Playlist]")
parser.add_argument("-n",
                    "--no-video",
                    help="Play audio only",
                    action="store_true",
                    default=False)
parser.add_argument("-p",
                    "--popular",
                    help="View popular videos (Main invidious page)",
                    action="store_true")
args = parser.parse_args()

player = mpv.MPV(ytdl=True,
                 input_default_bindings=True,
                 input_vo_keyboard=True,
                 osc=True)


def length(arg):
    try:
        return datetime.timedelta(seconds=arg)
    except TypeError:
        return arg


def player_config(no_video):
    if no_video:
        player.vid = False
        player.terminal = True
        player.input_terminal = True
    elif not no_video:
        player.vid = "auto"
        player.terminal = False
        player.input_terminal = False


def get_by_url(url):
    content_id = url.split("=")[1]
    video_id_len = 11
    if len(content_id) > video_id_len:
        api_url = "https://invidio.us/api/v1/playlists/{}".format(content_id)
        content_type = "playlist"
    else:
        api_url = content_id
        content_type = "video"
    return content_type, api_url


def get_data(content_type, api_url, search_term):
    data = ["videoId", "title", "lengthSeconds"]
    if content_type == "search":
        url = "https://invidio.us/api/v1/search?q={}".format(search_term)
    elif content_type == "popular":
        url = "https://invidio.us/api/v1/popular"
    elif content_type == "playlist":
        url = api_url
    elif content_type == "video":
        return [api_url]
    content = json.loads(urllib.request.urlopen(url).read())
    count = 0
    video_ids = []
    if content_type == "playlist":
        content = content["videos"]
    for i in content:
        count += 1
        video_ids.append(i[data[0]])
        results = "{}: {} [{}]".format(count, i[data[1]], length(i[data[2]]))
        print(results)
    queue_list = []
    if content_type == "search" or content_type == "playlist" or content_type == "popular":
        queue = input("> ").split()
        for item in queue:
            item = int(item) - 1
            queue_list.append(item)
        video_ids = [video_ids[i] for i in queue_list]
    return video_ids, len(queue_list)


def video_playback(video_ids, queue_length):
    data = ["hlsUrl", "formatStreams", "title"]
    if queue_length == 0:
        queue_length = 1
    queue = 0
    for video_id in video_ids:
        queue += 1
        url = "https://invidio.us/api/v1/videos/{}".format(video_id)
        stream_url = json.loads(urllib.request.urlopen(url).read())
        # Try to get URL for 720p, 360p, then livestream
        try:
            url = stream_url[data[1]][1]["url"]
        except IndexError:
            try:
                url = stream_url[data[1]][0]["url"]
            except IndexError:
                url = stream_url[data[0]]
        title = stream_url[data[2]]
        print(f"[{queue} of {queue_length}] {title}")
        player.play(url)
        player.wait_for_playback()


if __name__ == "__main__":
    print(string)
    if args.popular:
        video_ids = get_data("popular", None, None)
    elif args.url is not None:
        url = get_by_url(args.url)
        video_ids = get_data(url[0], url[1], None)
    else:
        search_term = "+".join(input("> ").split())
        video_ids = get_data("search", None, search_term)
    player_config(args.no_video)
    video_playback(video_ids[0], video_ids[1])
