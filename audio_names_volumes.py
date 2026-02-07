AUDIO_NAMES_VOLUMES = {
    "bones.mp3": 0.5,
    "church.mp3": 1.0,
    "lagoon.mp3": 0.25,
    "moor.mp3": 0.4,
    "opening.mp3": 1.0,
    "river.mp3": 0.02,
    "ruins.mp3": 0.5,
    "victory.mp3": 0.25
}

def get_volume(audio_name: str) -> float:
    return AUDIO_NAMES_VOLUMES[audio_name]

def get_audio_names() -> list[str]:
    return list(AUDIO_NAMES_VOLUMES.keys())
