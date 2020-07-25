import urllib.request
import argparse
import datetime
import json
import mpv

CRED = "\033[91m"
CBLUE = "\33[34m"
CGREEN = "\33[32m"
CEND = "\033[0m"
instance = None


def length(arg):
    try:
        return datetime.timedelta(seconds=arg)
    except TypeError:
        return arg


def download(url):
    content = urllib.request.urlopen(url).read()
    content = json.loads(content)
    return content


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
        api_url = "{}/api/v1/playlists/{}".format(instance, content_id)
        content_type = "playlist"
    else:
        api_url = content_id
        content_type = "video"
    return content_type, api_url


def get_data(content_type, api_url, search_term):
    if content_type == "search" or content_type == "channel":
        url = "{}/api/v1/search?q={}".format(instance, search_term)
    elif content_type == "popular":
        url = "{}/api/v1/popular".format(instance)
    elif content_type == "trending":
        url = "{}/api/v1/trending".format(instance)
    elif content_type == "playlist":
        url = api_url
    elif content_type == "video":
        return [api_url], 0
    content = download(url)
    count = 0
    video_ids = []
    if content_type == "playlist":
        content = content["videos"]
    elif content_type == "channel":
        channel_url = "{}/api/v1/channels/{}".format(instance,
                                                     content[0]["authorId"])
        content = download(channel_url)
        content = content["latestVideos"]
    title_list = []
    max_len = 60
    for i in content:
        title = i["title"][:max_len]
        title_list.append(title)
    longest_title = len(max(title_list, key=len))
    for i in content:
        count += 1
        if count <= 9:
            count_ = " {}".format(count)
        else:
            count_ = count
        video_ids.append(i["videoId"])
        title = i["title"][:max_len].ljust(longest_title)
        video_length = length(i["lengthSeconds"])
        channel = i["author"]
        results = "{}: {}{} {}[{}] {}{} {}".format(count_, CGREEN, title,
                                                   CBLUE, video_length, CRED,
                                                   channel, CEND)
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
        url = "{}/api/v1/videos/{}".format(instance, video_id)
        stream_url = download(url)
        title = stream_url["title"]
        print(f"[{queue} of {queue_length}] {title}")
        # Try to get URL for 1080p, 720p, 360p, then livestream
        try:
            url = stream_url["adaptiveFormats"][-3]["url"]
            audio_url = stream_url["adaptiveFormats"][3]["url"]
            player.audio_files = [audio_url]
        except IndexError:
            try:
                url = stream_url["formatStreams"][1]["url"]
            except IndexError:
                try:
                    url = stream_url["hlsUrl"]
                except KeyError:
                    print("No URL found\n")
                    continue
        player.play(url)
        player.wait_for_playback()
    player.terminate()


if __name__ == "__main__":
    string = r'''
      _____            _     _ _
     |_   _|          (_)   | (_)
       | |  _ ____   ___  __| |_  ___  _   _ ___
       | | | '_ \ \ / / |/ _` | |/ _ \| | | / __|
      _| |_| | | \ V /| | (_| | | (_) | |_| \__ \
     |_____|_| |_|\_/ |_|\__,_|_|\___/ \__,_|___/
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--instance",
                        help="Specify a different invidious instance",
                        default="https://invidio.us")
    parser.add_argument("-n",
                        "--no-video",
                        help="Play audio only",
                        action="store_true",
                        default=False),
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u",
                       "--url",
                       help="Specify link to play [Video/Playlist]")
    group.add_argument("-c",
                       "--channel",
                       help="View videos from a specific channel")
    group.add_argument("-p",
                       "--popular",
                       help="View popular videos (Default invidious page)",
                       action="store_true")
    group.add_argument("-t",
                       "--trending",
                       help="View trending videos",
                       action="store_true")
    args = parser.parse_args()

    player = mpv.MPV(ytdl=True,
                     input_default_bindings=True,
                     input_vo_keyboard=True,
                     osc=True)
    player.on_key_press("ENTER")(lambda: player.playlist_next(mode="force"))
    print(string)
    instance = args.instance
    if args.popular:
        video_ids = get_data("popular", None, None)
    elif args.trending:
        video_ids = get_data("trending", None, None)
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
