import urllib.request
import feedparser
import argparse
import datetime
import json
import mpv
import os

CRED = "\033[91m"
CBLUE = "\33[34m"
CGREEN = "\33[32m"
CEND = "\033[0m"


def length(arg):
    try:
        return datetime.timedelta(seconds=arg)
    except TypeError:
        return arg


def download(url):
    content = urllib.request.urlopen(url).read()
    content = json.loads(content)
    return content


def player_config(video, player):
    if not video:
        player.vid = False
        player.terminal = True
        player.input_terminal = True
    else:
        player.vid = "auto"
        player.terminal = False
        player.input_terminal = False


def get_by_url(url, instance):
    try:
        content_id = url.split("=")[1]
    except IndexError:
        content_id = url
    video_id_len = 11
    if len(content_id) > video_id_len:
        api_url = "{}/api/v1/playlists/{}".format(instance, content_id)
        content_type = "playlist"
    else:
        api_url = content_id
        content_type = "video"
    return content_type, api_url


def config(instance):
    config_path = os.path.expanduser("~/.config/invidious/")
    config_file = config_path + "config.json"
    config_dict = {"instance": instance, "play_video": True}
    if not os.path.exists(config_file):
        print("Created config file at {}".format(config_file))
        try:
            os.mkdir(config_path)
        except FileExistsError:
            pass
        with open(config_file, "w") as f:
            json.dump(config_dict, f)
    with open(config_file, "r") as f:
        content = json.loads(f.read())
        return content


def get_data(content_type, results, instance, search_term=None, api_url=None):
    if "search" in content_type or "channel" in content_type:
        url = "{}/api/v1/search?q={}".format(instance, search_term)
    elif "popular" in content_type:
        url = "{}/api/v1/popular".format(instance)
    elif "trending" in content_type:
        url = "{}/api/v1/trending".format(instance)
    elif "playlist" in content_type:
        url = api_url
    elif "video" in content_type:
        return [api_url], 0
    rss = False
    content = download(url)
    count = 0
    max_len = 60
    max_results = results
    if results is not None:
        try:
            max_results = int(results)
        except ValueError:
            max_results = None
    video_ids = []
    title_list = []
    if content_type == "playlist":
        content = content["videos"]
    elif content_type == "channel":
        content_ = content
        channel_url = "{}/api/v1/channels/videos/{}".format(instance,
                                                     content_[0]["authorId"])
        content = download(channel_url)
        # Fetch videos from RSS fead if invidious fails
        if len(content) == 0:
            rss = True
            content = {}
            id_key = "videoId"
            title_key = "title"
            author_key = "author"
            length_key = "lengthSeconds"
            content.setdefault(id_key, [])
            content.setdefault(title_key, [])
            content.setdefault(author_key, [])
            content.setdefault(length_key, [])
            rss_feed = feedparser.parse("{}/feed/channel/{}".format(instance,
                                                  content_[0]["authorId"]))
            rss_count = -1
            # RSS returns only 15 results
            while rss_count < 14:
                rss_count += 1
                entries = rss_feed.entries[rss_count]
                content[id_key].append(entries.yt_videoid)
                content[title_key].append(entries.title)
                content[author_key].append(entries.author)
                content[length_key].append(0)
    if rss:
        for i in content["title"]:
            title = i
            title_list.append(title)
    else:
        for i in content:
            title = i["title"][:max_len]
            title_list.append(title)
    longest_title = len(max(title_list, key=len))
    def content_loop(loop_variable, count=count):
        for i in loop_variable:
            count += 1
            if count <= 9:
                count_ = " {}".format(count)
            else:
                count_ = count
            if max_results is not None and count < max_results:
                continue
            if rss:
                title = i[:max_len].ljust(longest_title)
                for item in content["author"]:
                    channel = item
                for item in content["videoId"]:
                    if item not in video_ids:
                        video_ids.append(item)
                for item in content["lengthSeconds"]:
                    video_length = length(item)
            else:
                title = i["title"][:max_len].ljust(longest_title)
                channel = i["author"]
                video_ids.append(i["videoId"])
                video_length = length(i["lengthSeconds"])
            results = "{}: {}{} {}[{}] {}{} {}".format(count_, CGREEN, title,
                                                       CBLUE, video_length, CRED,
                                                       channel, CEND)
            print(results)
    if rss:
        content_loop(content["title"])
    else:
        content_loop(content)
    queue_list = []
    if content_type == "search" or "playlist" or "popular":
        queue = input("> ").split()
        if len(queue) == 1 and queue[0] == "all":
            return video_ids, len(video_ids)
        for item in queue:
            item = int(item) - 1
            queue_list.append(item)
        video_ids = [video_ids[i] for i in queue_list]
    return video_ids, len(queue_list)


def video_playback(video_ids, queue_length, instance, player):
    if queue_length == 0:
        queue_length = 1
    queue = 0
    for video_id in video_ids:
        queue += 1
        url = "{}/api/v1/videos/{}".format(instance, video_id)
        stream_url = download(url)
        title = stream_url["title"]
        print("[{} of {}] {}".format(queue, queue_length, title))
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
                    print("No URL found")
        player.play(url)
        player.wait_for_playback()
    player.terminate()


def main():
    string = r'''
      _____            _     _ _
     |_   _|          (_)   | (_)
       | |  _ ____   ___  __| |_  ___  _   _ ___
       | | | '_ \ \ / / |/ _` | |/ _ \| | | / __|
      _| |_| | | \ V /| | (_| | | (_) | |_| \__ \
     |_____|_| |_|\_/ |_|\__,_|_|\___/ \__,_|___/
    '''
    print(string)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--instance",
        help="Specify a different invidious instance (Overrides config file)")
    parser.add_argument("-r",
                        "--results",
                        type=int,
                        help="Return specific number of results")
    parser.add_argument("-v",
                        "--video",
                        help="Play video (Overrides config file)",
                        action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u",
                       "--url",
                       help="Specify link or ID to play [Video/Playlist]")
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
    url_ = args.url
    results = args.results
    default_instance = "https://invidious.snopyta.org"
    invidious_config = config(default_instance)
    if args.instance is not None:
        instance = args.instance
    else:
        instance = invidious_config.get("instance")
    if args.video:
        video = args.video
    else:
        video = invidious_config.get("play_video")
    if args.popular:
        video_ids = get_data("popular", results, instance)
    elif args.trending:
        video_ids = get_data("trending", results, instance)
    elif args.channel is not None:
        channel_name = "+".join(args.channel.split())
        video_ids = get_data("channel", results, instance, channel_name)
    elif args.url is not None:
        url = get_by_url(url_, instance)
        video_ids = get_data(url[0], results, instance, api_url=url[1])
    else:
        search_term = "+".join(input("> ").split())
        video_ids = get_data("search", results, instance, search_term)
    player_config(video, player)
    video_playback(video_ids[0], video_ids[1], instance, player)


if __name__ == "__main__":
    main()
