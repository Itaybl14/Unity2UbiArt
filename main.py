# Unity2Ubiart v1.1 by Itay, Worte and Rama.
import json, os, math, random, shutil, UnityPy, colorama, time, requests, subprocess
from PIL import Image
from colorama import Fore, Style
import tkinter as tk
from tkinter import filedialog

UnityPy.config.FALLBACK_UNITY_VERSION = '2021.3.9f1'

class Bundle:
    def unpack_Texture2D(source_file: str, destination_folder: str):
        os.makedirs(os.path.join(destination_folder), exist_ok=True)
        env = UnityPy.load(source_file)

        # iterate over internal objects
        for obj in env.objects:
            # process specific object types
            if obj.type.name == "Texture2D":
                # parse the object data
                data = obj.read()

                # create destination path
                dest = os.path.join(destination_folder, data.name)

                # make sure that the extension is correct
                dest, ext = os.path.splitext(dest)
                dest = f"{dest}.png"

                img = data.image
                img.save(dest)
                if not dest.endswith('_Phone.png'): # if its not a phone texture
                    Util.convert_to_dxt5(dest, dest.replace('.png', '.dds'))
            
    def unpack_all_assets(source_file: str, destination_folder: str):
        # create subfolders for each asset type
        asset_types = ['TextAsset', 'Sprite', 'MonoBehaviour']
        for asset_type in asset_types:
            os.makedirs(os.path.join(destination_folder, asset_type), exist_ok=True)

        map_name = ''
        # load the bundle file via UnityPy.load
        env = UnityPy.load(source_file)

        # iterate over internal objects
        for obj in env.objects:
            # process specific object types
            if obj.type.name == "Sprite":
                # parse the object data
                data = obj.read()

                # create destination path
                dest = os.path.join(destination_folder, 'Sprite', data.name)

                # make sure that the extension is correct
                dest, ext = os.path.splitext(dest)
                dest = f"{dest}.png"

                img = data.image
                img.save(dest)
                    
            elif obj.type.name == "TextAsset":
                # export asset
                data = obj.read()
                with open(os.path.join(destination_folder, 'TextAsset', data.name), "wb") as f:
                    f.write(bytes(data.script))

                # edit asset
                fp = os.path.join(destination_folder, 'TextAsset', data.name)
                with open(fp, "rb") as f:
                    data.script = f.read()
                data.save()
                    
            elif obj.type.name == "MonoBehaviour":
                mono_behaviour_extract_folder = os.path.join(destination_folder, 'MonoBehaviour')

                # export
                if obj.serialized_type.nodes:
                    # save decoded data
                    tree = obj.read_typetree()
                    if tree['m_Name'] == '':
                        tree['m_Name'] = 'MusicTrack'
                    else:
                        map_name = tree['m_Name']
                    fp = os.path.join(mono_behaviour_extract_folder, f"{tree['m_Name']}.json")
                    with open(fp, "wt", encoding="utf8") as f:
                        json.dump(tree, f, ensure_ascii=False, indent=4)
                else:
                    # save raw relevant data (without Unity MonoBehaviour header)
                    data = obj.read()
                    fp = os.path.join(mono_behaviour_extract_folder, f"{data.name}.bin")
                    with open(fp, "wb") as f:
                        f.write(data.raw_data)

                # edit
                if obj.serialized_type.nodes:
                    tree = obj.read_typetree()
                    # apply modifications to the data within the tree
                    obj.save_typetree(tree)
                else:
                    data = obj.read()
                    with open(os.path.join(mono_behaviour_extract_folder, data.name)) as f:
                        data.save(raw_data=f.read())

        return map_name

class Util:
    Ids = []
    def convert_pictogram(input_path, output_path, coach_count):
            if coach_count == 1:
                init_pictogram_size = (512, 512)
            else:
                init_pictogram_size = (512, 354) # NOTE: causes stretching in original texture, not sure why is it 354 or why it has to be stretched at all

            input_pictogram = Image.open(input_path)
            x, y = input_pictogram.size

            offset_x = math.floor((init_pictogram_size[0] - x) / 2)
            offset_y = math.ceil(init_pictogram_size[1] - y)

            output_pictogram = Image.new(input_pictogram.mode, init_pictogram_size, (255, 255, 255, 0))
            output_pictogram.paste(input_pictogram, (offset_x, offset_y))
            
            if coach_count > 1:
                output_pictogram = output_pictogram.resize((1024, 512))

            output_pictogram.save(output_path)

    def convert_list(input, __class):
        output = []
        for item in input:
            value = item[__class]
            value['__class'] = __class
            output.append(value)
        return output
    
    def convert_color(input):
        try:
            rgb = tuple(int(input[i:i+2], 16) for i in (0, 2, 4))
        except:
            return [1, 1, 0, 0]
        output = []

        output.append(float(str(float(100) / 100)[:8]))
        output.append(float(str(rgb[0] / 255)[:8]))
        output.append(float(str(rgb[1] / 255)[:8]))
        output.append(float(str(rgb[2] / 255)[:8]))

        return output
    
    def get_random_id():
        while True:
            id = random.randint(1000000000, 4000000000)
            if id not in Util.Ids:
                Util.Ids.append(id)
                return id
    
    def load_file(input_path):
        return json.load(open(input_path, encoding='UTF-8'))
    
    def save_file(path, jsonText, sortClips):
        if sortClips:
            jsonText['Clips'].sort(key=lambda x: x["StartTime"])
        open(path, 'wb').write(json.dumps(jsonText, separators=(',', ':')).encode() + b'\x00')
    
    def make_folder(input_folder):
        os.makedirs(input_folder, exist_ok=True)
    
    def log(author, message):
        print(f'{Fore.MAGENTA}[{author}]:{Style.RESET_ALL} {Fore.BLUE}{message}{Style.RESET_ALL}')
    
    def error(errmsg, toExit):
        print(f'{Fore.RED}[ERROR]: {errmsg}{Style.RESET_ALL}')
        if toExit:
            time.sleep(5)
            exit()

    def file_path(path, altpath, errmsg, toExit):
        if (os.path.isfile(path)) or (os.path.isdir(path)):
            return path
        elif (os.path.isfile(altpath)) or (os.path.isdir(altpath)):
            return altpath
        Util.error(errmsg, toExit)

    def songdb_mapinfo(map_name):
        songdb = Util.load_file('songdb.json')
        for map_id in songdb:
            map_info = songdb[map_id]
            if map_info['mapName'] == map_name:
                Util.log(map_name, 'Loaded SongDB Info.')
                return map_info
        return 
    
    def copy_files(input_folder, output_folder, file_extension):
        for filename in os.listdir(input_folder):
            if filename.split('.')[-1] == file_extension:
                shutil.copyfile(f'{input_folder}/{filename.lower()}', f'{output_folder}/{filename.lower()}')
    
    def gestures_exist_check(movespaces):
        movespaces = os.listdir(movespaces)
        if 'algoSettings' in movespaces:
            return 'PozeNet'
        elif 'scoringRules' in movespaces:
            return 'BlazePose'
        
    def convert_to_dxt5(input_path, output_path):
        # still needs to be updated, the converted dds file is too big compared to ubi ones.
        subprocess.run(f"bin\\nvcompress.exe -bc3 \"{input_path}\" \"{output_path}\"", shell=True, stdout=subprocess.DEVNULL)
        os.remove(input_path)

    def pick_audio_file(mapName):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title=f"Select {mapName} Audio File",
            filetypes=[("Audio Files", "*.opus;*.wav;*.ogg;*.mp3;*.flac"), ("All Files", "*.*")]
        )

        return file_path

config = Util.load_file('config.json')

def main(mapName, filesPath, config):
    Util.make_folder(f'output/{mapName}')
    music_track = Util.load_file(Util.file_path(f'{filesPath}/MonoBehaviour/MusicTrack.json', f'{filesPath}/MusicTrack.json', 'Cannot find your MusicTrack file', True))
    map_json = Util.load_file(Util.file_path(f'{filesPath}/MonoBehaviour/{mapName}.json', f'{filesPath}/{mapName}.json', 'Cannot find your MainJson file', True))

    tape = {"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":mapName,"SoundwichEvent":""}

    # ---- KaraokeData Tape ----
    Util.make_folder(f'output/{mapName}/Timeline')

    for clip in map_json['KaraokeData']['Clips']:
        karaoke_clip = clip['KaraokeClip']
        karaoke_clip['__class'] = 'KaraokeClip'
        tape['Clips'].append(karaoke_clip)
    
    Util.save_file(f'output/{mapName}/Timeline/{mapName.lower()}_tml_karaoke.ktape.ckd', tape, True)
    Util.log(mapName, f'Successfully generated KaraokeData tape.')

    # ---- DanceData Tape ----
    tape['Clips'] = []

    for motion_clip in map_json['DanceData']['MotionClips']:        
        motion_clip['Color'] = Util.convert_color(motion_clip['Color'][4:]) # for some reason it uses hex colors with 0xFF in the start just like Just Dance Now

        if motion_clip['MoveType'] == 0: # 0 = MSM
            motion_clip.update({
                '__class': 'MotionClip',
                'ClassifierPath': f"world/maps/{mapName.lower()}/timeline/moves/{motion_clip['MoveName']}.msm"
            })
            motion_clip.pop('MoveName')
            tape['Clips'].append(motion_clip)
        
        elif motion_clip['MoveType'] == 1: # 1 = GESTURE
            motion_clip.update({
                '__class': 'MotionClip',
                'ClassifierPath': f"world/maps/{mapName.lower()}/timeline/moves/{motion_clip['MoveName']}.gesture",
                'MotionPlatformSpecifics': {"X360":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1},"ORBIS":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":-0.200000,"HighThreshold":0.600000},"DURANGO":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1}}
            })
            motion_clip.pop('MoveName')
            tape['Clips'].append(motion_clip)

    if 'GoldEffectClips' in map_json['DanceData']:
        for gold_move in map_json['DanceData']['GoldEffectClips']:
            gold_move.update({
                '__class': 'GoldEffectClip',
                'EffectType': 1
            })
            tape['Clips'].append(gold_move)

    # Picto Clips
    for picto_clip in map_json['DanceData']['PictoClips']:
        picto_clip.update({
            '__class': 'PictogramClip',
            'PictoPath': f"world/maps/{mapName.lower()}/timeline/pictos/{picto_clip['PictoPath']}.png"
        })
        tape['Clips'].append(picto_clip)

    Util.save_file(f'output/{mapName}/Timeline/{mapName.lower()}_tml_dance.dtape.ckd', tape, True)
    Util.log(mapName, 'Successfully generated DanceData tape.')

    # ---- SongDB Items ----
    map_info = Util.songdb_mapinfo(mapName)
    if map_info:
        songdb_musictrack = json.loads(map_info['assetsMetadata']['audioPreviewTrk'])
        Util.log(mapName, 'Successfully loaded SongDB info.')
    else:
        songdb_musictrack = None

    # ---- MusicTrack Tape ----
    Util.make_folder(f'output/{mapName}/Audio')
    music_track_structure = music_track['m_structure']['MusicTrackStructure']
    markers = []

    for marker in music_track_structure['markers']:
        markers.append(marker['VAL'])

    startBeat = music_track_structure.get('startBeat', 0)
    endBeat = music_track_structure.get('endBeat', len(markers))
    UbiArt_music_track = {
    "__class": "Actor_Template",
    "WIP": 0,
    "LOWUPDATE": 0,
    "UPDATE_LAYER": 0,
    "PROCEDURAL": 0,
    "STARTPAUSED": 0,
    "FORCEISENVIRONMENT": 0,
    "COMPONENTS": [{
            "__class": "MusicTrackComponent_Template",
            "trackData": {
                "__class": "MusicTrackData",
                "structure": {
                    "__class": "MusicTrackStructure",
                    "markers": markers,
                    "signatures": Util.convert_list(music_track_structure['signatures'], 'MusicSignature'),
                    "sections": Util.convert_list(music_track_structure['sections'], 'MusicSection'),
                    "startBeat": startBeat,
                    "endBeat": endBeat,
                    "videoStartTime": music_track_structure.get('videoStartTime', 0),
                    "previewEntry": int(songdb_musictrack['PreviewEntry']) if songdb_musictrack else int(music_track_structure.get('previewEntry', 0)),
                    "previewLoopStart": int(songdb_musictrack['PreviewLoopStart']) if songdb_musictrack else int(music_track_structure.get('previewLoopStart', 0)),
                    "previewLoopEnd": int(songdb_musictrack['PreviewLoopEnd']) if songdb_musictrack and 'PreviewLoopEnd' in songdb_musictrack else int(music_track_structure.get('previewLoopEnd', endBeat)),
                    "volume": int(music_track_structure.get('volume', 0))
                },
                "path": f"world/maps/{mapName.lower()}/audio/{mapName.lower()}.ogg",
                "url": f"jmcs://jd-contents/{mapName}/{mapName}.ogg"
            }
        }
    ]
}
    if UbiArt_music_track["COMPONENTS"][0]['trackData']['structure']['previewLoopEnd'] == 0:
        UbiArt_music_track["COMPONENTS"][0]['trackData']['structure']['previewLoopEnd'] = endBeat
    
    Util.save_file(f'output/{mapName}/Audio/{mapName.lower()}_musictrack.tpl.ckd', UbiArt_music_track, False)
    Util.log(mapName, 'Successfully generated MusicTrack tpl.')

    # ---- Cinematics ----
    tape['Clips'] = []
    if 'HideHudClips' in map_json['DanceData']:
        for clip in map_json['DanceData']['HideHudClips']:
            clip.update({
                '__class': 'HideUserInterfaceClip',
                'Id': Util.get_random_id(),
                'TrackId': Util.get_random_id(),
                'EventType': 18,
                'CustomParam': ''
            })
            tape['Clips'].append(clip)
    if (config['MakeAmbs']) and (startBeat != 0):
        # NOTE: other ambs can be included inside the main audio because were using their online sound which includes ambs
        tape['Clips'].append({
            "__class": "SoundSetClip",
            "Id": Util.get_random_id(),
            "TrackId": Util.get_random_id(),
            "IsActive": 1,
            "StartTime":startBeat * 24,
            "Duration": abs(startBeat * 24), # NOTE: can be changed, its prob not that long...
            "SoundSetPath": f"world/maps/{mapName.lower()}/audio/amb/amb_{mapName.lower()}_intro.tpl",
            "SoundChannel": 0,
            "StartOffset": 0,
            "StopsOnEnd": 0,
            "AccountedForDuration": 0
        })
        Util.make_folder(f'output/{mapName}/Audio/AMB')
        Util.save_file(f'output/{mapName}/Audio/AMB/amb_{mapName.lower()}_intro.tpl.ckd', {
    "__class": "Actor_Template",
    "WIP": 0,
    "LOWUPDATE": 0,
    "UPDATE_LAYER": 0,
    "PROCEDURAL": 0,
    "STARTPAUSED": 0,
    "FORCEISENVIRONMENT": 0,
    "COMPONENTS": [
        {
            "__class": "SoundComponent_Template",
            "soundList": [
                {
                    "__class": "SoundDescriptor_Template",
                    "name": f"amb_{mapName.lower()}_intro",
                    "volume": 0,
                    "category": "amb",
                    "limitCategory": "",
                    "limitMode": 0,
                    "maxInstances": 4294967295,
                    "files": [
                        f"world/maps/{mapName.lower()}/audio/amb/amb_{mapName.lower()}_intro.wav"
                    ],
                    "serialPlayingMode": 0,
                    "serialStoppingMode": 0,
                    "params": {
                        "__class": "SoundParams",
                        "loop": 0,
                        "playMode": 1,
                        "playModeInput": "",
                        "randomVolMin": 0,
                        "randomVolMax": 0,
                        "delay": 0,
                        "randomDelay": 0,
                        "pitch": 1,
                        "randomPitchMin": 1,
                        "randomPitchMax": 1,
                        "fadeInTime": 0,
                        "fadeOutTime": 0,
                        "filterFrequency": 0,
                        "filterType": 2,
                        "transitionSampleOffset": 0
                    },
                    "pauseInsensitiveFlags": 0,
                    "outDevices": 4294967295,
                    "soundPlayAfterdestroy": 0
                }
            ]
        }
    ]
}, False)
    
    if len(tape['Clips']) > 0:
        Util.make_folder(f'output/{mapName}/Cinematics')
        Util.save_file(f'output/{mapName}/Cinematics/{mapName.lower()}_mainsequence.tape.ckd', tape, False)
        Util.log(mapName, 'Successfully generated MainSequence tape.')

    # ---- Audio Cutter ----
    # NOTE: the audio cutting is not perfect, and can be off for some maps! (ex. WheneverWhereverALT)
    if config['cutAudio']:
        Util.log(mapName, 'Cutting audio...')
        audioFile = Util.pick_audio_file(mapName)
        if audioFile:
            start = markers[int(abs(startBeat))] / 48
            subprocess.run(f'ffmpeg -y -i "{audioFile}" -ss {start}ms -loglevel quiet "output/{mapName}/Audio/{mapName.lower()}.ogg"')
            if (config['MakeAmbs']) and (startBeat != 0):
                subprocess.run(f'ffmpeg -y -i "{audioFile}" -ss 00:00:00 -t {start}ms -vn -loglevel quiet "output/{mapName}/Audio/AMB/amb_{mapName.lower()}_intro.wav"')
        else:
            Util.error('No audio file selected, skipping audio cutting.', False)
    
    # ---- SongDescription ----
    song_desc = map_json['SongDesc']

    if 'NumCoach' in song_desc:
        NumCoach = song_desc['NumCoach']
    else:
        NumCoach = 4 # default
    
    UbiArt_song_description = {
    "__class": "Actor_Template",
    "WIP": 0,
    "LOWUPDATE": 0,
    "UPDATE_LAYER": 0,
    "PROCEDURAL": 0,
    "STARTPAUSED": 0,
    "FORCEISENVIRONMENT": 0,
    "COMPONENTS": [{
            "__class": "JD_SongDescTemplate",
            "MapName": mapName,
            "JDVersion": config.get('JDVersion', 2023),
            "OriginalJDVersion": map_info['originalJDVersion'] if map_info else config.get('JDVersion', 2023),
            "Artist": map_info['artist'] if map_info else song_desc.get('Artist', f"{mapName}'s Artist"),
            "DancerName": "Unknown Dancer",
            "Title": map_info['title'] if map_info else song_desc.get('Title', f"{mapName}'s Title"),
            "Credits": map_info['credits'] if map_info else song_desc.get('Credits', 'All rights of the producer and other rightholders to the recorded work reserved. Unless otherwise authorized, the duplication, rental, loan, exchange or use of this video game for public performance, broadcasting and online distribution to the public are prohibited.'),
            "PhoneImages": {
                "cover": f"world/maps/{mapName.lower()}/menuart/textures/{mapName.lower()}_cover_phone.jpg",
                **{f"coach{i+1}": f"world/maps/{mapName.lower()}/menuart/textures/{mapName.lower()}_coach_{i+1}_phone.png" for i in range(NumCoach)}
            },
            "NumCoach": NumCoach,
            "MainCoach": -1, # without it the coaches says rip so
            "Difficulty": map_info['difficulty'] if map_info else song_desc.get('Difficulty', 1),
            "SweatDifficulty": map_info['sweatDifficulty'] if map_info else song_desc.get('SweatDifficulty', 1),
            "backgroundType": 0,
            "LyricsType": 0,
            "Tags": ["main"],
            "Status": 3,
            "LocaleID": 4294967295,
            "MojoValue": 0,
            "CountInProgression": 1,
            "DefaultColors": config.get('DefaultColors', {"songcolor_2a":[1,0.666667,0.666667,0.666667],"lyrics": [1,1,0,0],"theme":[1,1,1,1],"songcolor_1a":[1,0.266667,0.266667,0.266667],"songcolor_2b":[1,0.466667,0.466667,0.466667],"songcolor_1b":[1,0.066667,0.066667,0.066667]}),
            "VideoPreviewPath": ""
        }
    ]}

    if map_info:
        UbiArt_song_description["COMPONENTS"][0]['DefaultColors']['lyrics'] = Util.convert_color(map_info['lyricsColor'][1:-2])

    Util.save_file(f'output/{mapName}/songdesc.tpl.ckd', UbiArt_song_description , False)

    # ---- Pictograms ----

    # resizing/converting the pictos
    pictos_path = Util.file_path(f'{filesPath}/Pictos', f'{filesPath}/Sprite', 'Cannot find your pictograms path', False)
    if pictos_path:
        Util.log(mapName, 'Input pictograms folder found, converting...')
        Util.make_folder(f'output/{mapName}/Timeline/Pictos')

        for file_name in os.listdir(pictos_path):
            pictoPath = os.path.join(pictos_path, file_name)
            output_PictoPath = os.path.join(f'output/{mapName}/Timeline/Pictos', file_name)
            with Image.open(pictoPath) as img:
                width, height = img.size
                if width == height and NumCoach == 1: # only older maps (2023) needs resizing, and only if theres only 1 coach
                    shutil.copy(pictoPath, output_PictoPath)
                else:
                    Util.convert_pictogram(f'{pictos_path}/{file_name}', output_PictoPath, NumCoach)
            
            Util.convert_to_dxt5(output_PictoPath, output_PictoPath.replace('.png', '.dds'))
            
    # movespaces
    movespaces = Util.file_path(f'{filesPath}/moves', f'{filesPath}/TextAsset', 'Cannot find your moves path', False)
    if movespaces:
        Util.log(mapName, 'Input moves folder found, copying...')
        Util.make_folder(f'output/{mapName}/Timeline/Moves/WIIU')
        Util.copy_files(movespaces, f'output/{mapName}/Timeline/Moves/WIIU', 'msm')
        gesture = Util.gestures_exist_check(movespaces)
        if gesture:
            Util.log(mapName, f'{gesture} gestures found!.')
            Util.make_folder(f'output/{mapName}/Timeline/Moves/{gesture.upper()}')
            Util.copy_files(movespaces, f'output/{mapName}/Timeline/Moves/{gesture.upper()}', 'gesture')
    
    # ---- MenuArt ----
    if map_info:
        MenuArt_path = os.path.join('output', mapName, 'MenuArt')
        assets = map_info['assets']
        Util.log(mapName, 'Downloading SongDB assets...')
        for asset in config['DownloadableAssets']:
            if asset in assets:
                filePath_ = os.path.join(filesPath, asset)
                open(filePath_, 'wb').write(requests.get(assets[asset]).content) # basic file saving
                Bundle.unpack_Texture2D(filePath_, MenuArt_path)
                os.remove(filePath_)

    
    Util.log('tool', 'Done!')


if __name__ == '__main__':
    colorama.init()
    for filename in os.listdir('input'):
        filePath = os.path.join('input', filename)

        print(f'{Fore.YELLOW}---- {filePath} ----{Style.RESET_ALL}')

        if os.path.isfile(filePath):
            Util.log('Tool', f'Extracting [{filePath}]')
            filesPath = os.path.join('input', 'temp')
            mapName = Bundle.unpack_all_assets(filePath, filesPath)
        elif os.path.isdir(filePath):
            mapName = filename
            filesPath = filePath
        
        main(mapName, filesPath, config)
        try:
            shutil.rmtree(os.path.join('input', 'temp'))
        except:
            pass
