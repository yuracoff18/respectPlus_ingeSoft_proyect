from . import faceit, steam


def fetch(data):
    return steam.fetch(data) if data.platform == "steam" else faceit.fetch(data)
