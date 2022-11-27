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

    def convert_list(input, __class):
        output = []

        for item in input:
            value = item[__class]
            value['__class'] = __class

            output.append(value)
        
        return output
    
    def convert_color(input):
        rgb = ImageColor.getcolor(input, 'RGB')
        output = []

        output.append(float(str(float(100) / 100)[:8]))
        output.append(float(str(rgb[0] / 255)[:8]))
        output.append(float(str(rgb[1] / 255)[:8]))
        output.append(float(str(rgb[2] / 255)[:8]))

        return output
    
    def get_random_id():
        return random.randint(1000000000, 6000000000)
    
    def load_file(input_path):
        return json.load(open(input_path, encoding='UTF-8'))
    
    def save_file(output_path, input):
        open(output_path, 'w', encoding='UTF-8').write(json.dumps(input))
    
    def make_folder(input_folder):
        try:
            os.mkdir(input_folder)
        except:
            pass
    
    def log(author, message):
        print(f'[{author}] {message}')

config = Util.load_file('config.json')

for folder_name in os.listdir('input'):
    music_track = Util.load_file(f'input/{folder_name}/MusicTrack.json')
    map_json = Util.load_file(f'input/{folder_name}/{folder_name}.json')
    map_name = map_json['m_Name']

    Util.log('Tool', f'Started converting {map_name}!')
    Util.make_folder(f'output/{map_name}')

    tape = {"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":map_name,"SoundwichEvent":""}

    for clip in map_json['KaraokeData']['Clips']:
        karaoke_clip = clip['KaraokeClip']
        karaoke_clip['__class'] = 'KaraokeClip'
        tape['Clips'].append(karaoke_clip)
    
    tape['Clips'].sort(key=lambda x: x["StartTime"])
    Util.save_file(f'output/{map_name}/{map_name.lower()}_tml_karaoke.ktape.ckd', tape)

    Util.log(map_name, f'Successfully generated KaraokeData tape.')

    tape['Clips'] = []

    for motion_clip in map_json['DanceData']['MotionClips']:
        motion_clip['__class'] = 'MotionClip'
        motion_clip['MoveType'] = 0
        
        try:
            motion_clip['Color'] = Util.convert_color(motion_clip['Color'].replace('0xFF', '')) # for some reason it uses hex colors with 0xFF in the start just like Just Dance Now
        except:
            motion_clip['Color'] = [1,1,0,0] # red

        if f'world/maps/{map_name.lower()}/timeline/moves' and '.gesture' not in motion_clip['MoveName']:
            motion_clip['ClassifierPath'] = f"world/maps/{map_name.lower()}/timeline/moves/{motion_clip['MoveName']}.msm"
            motion_clip.pop('MoveName')
            if f'world/maps/{map_name.lower()}/timeline/moves/' not in motion_clip['ClassifierPath'] and '.gesture' not in motion_clip['ClassifierPath']:
                 motion_clip['MotionPlatformSpecifics'] = {"X360":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1},"ORBIS":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":-0.200000,"HighThreshold":0.600000},"DURANGO":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1}}
            tape['Clips'].append(motion_clip)

    if 'GoldEffectClips' in map_json['DanceData']:
        for gold_move in map_json['DanceData']['GoldEffectClips']:
            gold_move['__class'] = "GoldEffectClip" 
            gold_move['EffectType'] = 1
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
            "PhoneImages": {
                "cover": f"world/maps/{map_name.lower()}/menuart/textures/{map_name.lower()}_cover_phone.jpg"},
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
        }
    ]}

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
    if 'HideHudClips' in map_json['DanceData']:
        Util.make_folder(f'output/{map_name}/cinematics')
        tape['Clips'] = []
        for clip in map_json['DanceData']['HideHudClips']:
            clip['__class'] = 'HideUserInterfaceClip'
            clip['Id'] = Util.get_random_id()
            clip['TrackId'] = Util.get_random_id()
            clip['EventType'] = 18
            clip['CustomParam'] = ''
            tape['Clips'].append(clip)
        tape['Clips'].sort(key=lambda x: x["StartTime"]) # sorting the clips by their StartTime
        if config['MakeAmbs']:
            tape['Clips'].append({
            "__class": "SoundSetClip",
            "Id": Util.get_random_id(),
            "TrackId": Util.get_random_id(),
            "IsActive": 1,
            "StartTime":tape['Clips'][0]['StartTime'],
            "Duration": tape['Clips'][0]['Duration'],
            "SoundSetPath": f"world/maps/{map_name.lower()}/audio/amb/amb_{map_name.lower()}_intro.tpl",
            "SoundChannel": 0,
            "StartOffset": 0,
            "StopsOnEnd": 0,
            "AccountedForDuration": 0
        })
            Util.make_folder(f'output/{map_name}/amb')
            Util.save_file(f'output/{map_name}/amb/amb_{map_name.lower()}_intro.tpl.ckd', {
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
                    "name": f"amb_{map_name.lower()}_intro",
                    "volume": 0,
                    "category": "amb",
                    "limitCategory": "",
                    "limitMode": 0,
                    "maxInstances": 4294967295,
                    "files": [
                        f"world/maps/{map_name.lower()}/audio/amb/amb_{map_name.lower()}_intro.wav"
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
                        "fadeInTime": 0.500000,
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
})
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