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
parser.add_argument("-c",
                    "--channel",
                    help="View videos from a specific channel")
parser.add_argument("-n",
                    "--no-video",
                    help="Play audio only",
                    action="store_true",
                    default=False),
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
    if content_type == "search" or content_type == "channel":
        url = "https://invidio.us/api/v1/search?q={}".format(search_term)
    elif content_type == "popular":
        url = "https://invidio.us/api/v1/popular"
    elif content_type == "playlist":
        url = api_url
    elif content_type == "video":
        return [api_url], 0
    content = json.loads(urllib.request.urlopen(url).read())
    count = 0
    video_ids = []
    if content_type == "playlist":
        content = content["videos"]
    elif content_type == "channel":
        channel_url = "https://invidio.us/api/v1/channels/{}".format(
            content[0]["authorId"])
        content = json.loads(urllib.request.urlopen(channel_url).read())
        content = content["latestVideos"]
    for i in content:
        count += 1
        video_ids.append(i["videoId"])
        results = "{}: {} [{}]".format(count, i["title"],
                                       length(i["lengthSeconds"]))
        print(results)
    queue_list = []
    if content_type == "search" or "playlist" or "popular":
        queue = input("> ").lower().split()
        if "all" in queue:
            return video_ids, len(video_ids)
        for item in queue:
            item = int(item) - 1
            queue_list.append(item)
        video_ids = [video_ids[i] for i in queue_list]
    return video_ids, len(queue_list)


def video_playback(video_ids, queue_length):
    if queue_length == 0:
        queue_length = 1
    queue = 0
    for video_id in video_ids:
        queue += 1
        url = "https://invidio.us/api/v1/videos/{}".format(video_id)
        stream_url = json.loads(urllib.request.urlopen(url).read())
        # Try to get URL for 1080p, 720p, 360p, then livestream
        try:
            url = stream_url["adaptiveFormats"][15]["url"]
            audio_url = stream_url["adaptiveFormats"][0]["url"]
            player.audio_files = [audio_url]
        except IndexError:
            try:
                url = stream_url["formatStreams"][1]["url"]
            except IndexError:
                try:
                    url = stream_url["hlsUrl"]
                except KeyError:
                    print("No URL found")
                    continue
        title = stream_url["title"]
        print(f"[{queue} of {queue_length}] {title}")
        player.play(url)
        player.wait_for_playback()


if __name__ == "__main__":
    print(string)
    if args.popular:
        video_ids = get_data("popular", None, None)
    elif args.channel is not None:
        channel_name = "+".join(args.channel.split())
        video_ids = get_data("channel", None, channel_name)
    elif args.url is not None:
        url = get_by_url(args.url)
        video_ids = get_data(url[0], url[1], None)
    else:
        search_term = "+".join(input("> ").split())
        video_ids = get_data("search", None, search_term)
    player_config(args.no_video)
    video_playback(video_ids[0], video_ids[1])
