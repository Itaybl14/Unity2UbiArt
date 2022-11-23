# Unity2Ubiart v1.0 by Itay, Worte and Rama.
import json, os, math, random, shutil
from PIL import Image, ImageColor

class Util:
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

    def convert_list(input_data, __class):
        def convert_entry(entry):
            # Setting up the __class
            entry[__class]['__class'] = __class

            # Returning the entry
            return entry[__class]
        
        output = map(convert_entry, input_data)
        return list(output)
    
    def convert_color(input_data):
        try:
            # For some reason it uses hex colors with 0xFF in the start just like Just Dance Now
            rgb = ImageColor.getcolor(input_data.replace('0xFF', ''), 'RGB')
            
            output = [1.0] # First floating-point number is alpha
            for color in rgb:
                output.append(float('{:.8f}'.format(color)))

            return output
        except:
            # (Default) Red color
            return [1.0, 1.0, 0.0, 0.0]
    
    def get_random_id():
        return random.randint(1000000000, 9999999999)
    
    def load_file(input_path):
        with open(input_path, encoding="utf-8") as file:
            return json.load(file)
    
    def save_file(output_path, input_data):
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(input_data, file)
    
    def make_folder(input_folder):
        if not os.path.exists(input_folder):
            os.mkdir(input_folder)
    
    def log(author, message):
        print(f'[{author}] {message}')

config = Util.load_file('config.json')

for folder_name in os.listdir('input'):
    music_track = Util.load_file(f'input/{folder_name}/MusicTrack.json')
    map_json = Util.load_file(f'input/{folder_name}/{folder_name}.json')
    map_name = map_json['m_Name']

    Util.log('Tool', f'Started converting {map_name}!')
    Util.make_folder(f'output/{map_name}')

    tape = {
        "__class": "Tape",
        "Clips": [],
        "TapeClock": 0,
        "TapeBarCount": 1,
        "FreeResourcesAfterPlay": 0,
        "MapName": map_name,
        "SoundwichEvent": ""
    }

    for clip in map_json['KaraokeData']['Clips']:
        karaoke_clip = clip['KaraokeClip']
        karaoke_clip['__class'] = 'KaraokeClip'
        tape['Clips'].append(karaoke_clip)
    
    tape['Clips'].sort(key=lambda x: x["StartTime"])
    Util.save_file(f'output/{map_name}/{map_name.lower()}_tml_karaoke.ktape.ckd', tape)

    Util.log(map_name, f'Successfully generated KaraokeData tape.')

    tape['Clips'] = []

    gold_effect_clips = []

    for motion_clip in map_json['DanceData']['MotionClips']:
        motion_clip['__class'] = 'MotionClip'
        motion_clip['MoveType'] = 0
        motion_clip['Color'] = Util.convert_color(motion_clip['Color'])

        if f'world/maps/{map_name.lower()}/timeline/moves' and '.gesture' not in motion_clip['MoveName']:
            motion_clip['ClassifierPath'] = f"world/maps/{map_name.lower()}/timeline/moves/{motion_clip['MoveName']}.msm"
            motion_clip.pop('MoveName')
            if f'world/maps/{map_name.lower()}/timeline/moves/' not in motion_clip['ClassifierPath'] and '.gesture' not in motion_clip['ClassifierPath']:
                 motion_clip['MotionPlatformSpecifics'] = {"X360":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1},"ORBIS":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":-0.200000,"HighThreshold":0.600000},"DURANGO":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1}}
            tape['Clips'].append(motion_clip)

    if 'GoldEffectClips' in map_json['DanceData']:
        for gold_move in map_json['DanceData']['GoldEffectClips']:
            gold_move['__class'] = "GoldEffectClip" 
            tape['Clips'].append(gold_move)

    # Picto Clips
    for picto_clips in map_json['DanceData']['PictoClips']:
        picto_clips['PictoPath'] = f"world/maps/{map_name.lower()}/timeline/pictos/{picto_clips['PictoPath']}.png"
        picto_clips['__class'] = 'PictogramClip'

        tape['Clips'].append(picto_clips)

    tape['Clips'].sort(key=lambda x: x["StartTime"]) # sorting the clips by their StartTime

    Util.save_file(f'output/{map_name}/{map_name.lower()}_tml_dance.dtape.ckd', tape)
    Util.log(map_name, 'Successfully generated DanceData tape.')

    # Song Description
    song_desc = map_json['SongDesc']
    __song_desc = {
        "__class": "Actor_Template",
        "WIP": 0,
        "LOWUPDATE": 0,
        "UPDATE_LAYER": 0,
        "PROCEDURAL": 0,
        "STARTPAUSED": 0,
        "FORCEISENVIRONMENT": 0,
        "COMPONENTS": [{
            "__class": "JD_SongDescTemplate",
            "MapName": map_name,
            "JDVersion": config['JDVersion'],
            "OriginalJDVersion": config['JDVersion'],
            "Artist": song_desc['Artist'],
            "DancerName": "Unknown Dancer",
            "Title": song_desc['Title'],
            "Credits":  song_desc['Credits'],
            "PhoneImages": {"cover": f"world/maps/{map_name.lower()}/menuart/textures/{map_name.lower()}_cover_phone.jpg"},
            "NumCoach": song_desc['NumCoach'],
            "MainCoach": -1, # without it the coaches says rip so
            "Difficulty": song_desc['Difficulty'],
            "SweatDifficulty": song_desc['SweatDifficulty'],
            "backgroundType": 0,
            "LyricsType": 0,
            "Tags": ["main"],
            "Status": 3,
            "LocaleID": 4294967295,
            "MojoValue": 0,
            "CountInProgression": 1,
            "DefaultColors": config['DefaultColors'],
            "VideoPreviewPath": ""
        }]
    }

    for i in range(song_desc['NumCoach']):
        i += 1
        __song_desc['COMPONENTS'][0]['PhoneImages'][f'coach{i}'] = f"world/maps/{map_name.lower()}/menuart/textures/{map_name.lower()}_coach_{i}_phone.png"

    Util.save_file(f'output/{map_name}/songdesc.tpl.ckd', __song_desc)
    Util.log(map_name, 'Successfully generated SongDescription tape.')

    # Music Track
    music_track_structure = music_track['m_structure']['MusicTrackStructure']
    markers = []

    for marker in music_track_structure['markers']:
        markers.append(marker['VAL'])
    
    __music_track = {
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
                        "startBeat": music_track_structure['startBeat'],
                        "endBeat": music_track_structure['endBeat'],
                        "videoStartTime": music_track_structure['videoStartTime'],
                        "previewEntry": music_track_structure['previewEntry'],
                        "previewLoopStart": music_track_structure['previewLoopStart'],
                        "previewLoopEnd": music_track_structure['previewLoopEnd'],
                        "volume": music_track_structure['volume']
                    },
                    "path": f"world/maps/{map_name.lower()}/audio/{map_name.lower()}.ogg",
                    "url": f"jmcs://jd-contents/{map_name}/{map_name}.ogg"
                }
            }
        ]
    }
    Util.save_file(f'output/{map_name}/{map_name.lower()}_musictrack.tpl.ckd', __music_track)
    Util.log(map_name, 'Successfully generated MusicTrack tape.')

    # cinematics:
    if 'HideHudClips' in clip in map_json['DanceData']:
        Util.make_folder(f'output/{map_name}/cinematics')
        tape['Clips'] = []
        for clip in map_json['DanceData']['HideHudClips']:
            clip['__class'] = 'HideUserInterfaceClip'
            clip['Id'] = Util.get_random_id()
            clip['TrackId'] = Util.get_random_id()
            clip['EventType'] = 18
            clip['CustomParam'] = ''
            tape['Clips'].append(clip)
        Util.save_file(f'output/{map_name}/cinematics/{map_name.lower()}_mainsequence.tape.ckd', tape)

    # resizing the pictos
    if os.path.isdir(f'input/{folder_name}/pictos'):
        Util.log(map_name, 'Input pictograms folder found, resizing...')
        Util.make_folder(f'output/{map_name}/pictos')

        for file_name in os.listdir(f'input/{folder_name}/pictos'):
            Util.convert_pictogram(f'input/{folder_name}/pictos/{file_name}', f'output/{map_name}/pictos/{file_name}', song_desc['NumCoach'])
            
    # renaming moves files
    if os.path.isdir(f'input/{folder_name}/moves'):
        Util.log(map_name, 'Input moves folder found, renaming...')
        Util.make_folder(f'output/{map_name}/moves')
        for filename in os.listdir(f'input/{folder_name}/moves'):
            shutil.copyfile(f'input/{folder_name}/moves/{filename.lower()}', f'output/{map_name}/moves/{filename.lower()}')
    
    Util.log('tool', 'Done!')
