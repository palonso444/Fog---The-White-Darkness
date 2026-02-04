AUDIO_VOLUMES = {
    "bones.mp3": 0.5,
    "church.mp3": 1.0,
    "lagoon.mp3": 0.3,
    "moor.mp3": 0.4,
    "opening.mp3": 1.0,
    "river.mp3": 0.11,
    "ruins.mp3": 0.6,
    "victory.mp3": 0.12
}

def get_volume(audio_name: str) -> float:
    return AUDIO_VOLUMES[audio_name]
