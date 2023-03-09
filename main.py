# Unity2Ubiart v1.1 by Itay, Worte and Rama.
import json, os, math, random, shutil, UnityPy
from PIL import Image, ImageColor
from colorama import Fore, Style

class Bundle:
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
            rgb = ImageColor.getcolor(input, 'RGB')
        except:
            return [1, 1, 0, 0]
        output = []

        output.append(float(str(float(100) / 100)[:8]))
        output.append(float(str(rgb[0] / 255)[:8]))
        output.append(float(str(rgb[1] / 255)[:8]))
        output.append(float(str(rgb[2] / 255)[:8]))

        return output
    
    def get_random_id():
        return random.randint(1000000000, 9999999999)
    
    def load_file(input_path):
        return json.load(open(input_path, encoding='UTF-8'))
    
    def save_file(path, jsonText, sortClips): # לשמור קובץ
        if sortClips:
            jsonText['Clips'].sort(key=lambda x: x["StartTime"])
        open(path, 'wb').write(json.dumps(jsonText, separators=(',', ':')).encode() + b'\x00')
    
    def make_folder(input_folder):
        os.makedirs(input_folder, exist_ok=True)
    
    def log(author, message):
        print(f'{Fore.MAGENTA}[{author}]:{Style.RESET_ALL} {Fore.BLUE}{message}{Style.RESET_ALL}')
    
    def error(message, toExit):
        print(f'{Fore.MAGENTA}[ERROR]:{Style.RESET_ALL} {Fore.RED}{message}{Style.RESET_ALL}')
        if toExit:
            exit()

    def filePath(path, altpath, errmsg, toExit):
        if (os.path.isfile(path)) or (os.path.isdir(path)):
            return path
        elif (os.path.isfile(altpath)) or (os.path.isdir(altpath)):
            return altpath
        Util.error(errmsg, toExit)
    
    def mapDB(songdb, mapName):
        for mapId in songdb:
            if songdb[mapId]['mapName'] == mapName:
                return songdb[mapId]
        return False
    
        

config = Util.load_file('config.json')

def main(mapName, filesPath, config):
    Util.make_folder(f'output/{mapName}')
    music_track = Util.load_file(Util.filePath(f'{filesPath}/MonoBehaviour/MusicTrack.json', f'{filesPath}/MusicTrack.json', 'Cannot find your MusicTrack file', True))
    map_json = Util.load_file(Util.filePath(f'{filesPath}/MonoBehaviour/{mapName}.json', f'{filesPath}/{mapName}.json', 'Cannot find your MainJson file', True))

    tape = {"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":mapName,"SoundwichEvent":""}

    # ---- KaraokeData Tape ----
    for clip in map_json['KaraokeData']['Clips']:
        karaoke_clip = clip['KaraokeClip']
        karaoke_clip['__class'] = 'KaraokeClip'
        tape['Clips'].append(karaoke_clip)
    
    Util.save_file(f'output/{mapName}/{mapName.lower()}_tml_karaoke.ktape.ckd', tape, True)
    Util.log(mapName, f'Successfully generated KaraokeData tape.')

    # ---- DanceData Tape ----
    tape['Clips'] = []

    for motion_clip in map_json['DanceData']['MotionClips']:
        motion_clip['__class'] = 'MotionClip'
        motion_clip['MoveType'] = 0
        
        motion_clip['Color'] = Util.convert_color(motion_clip['Color'][4:]) # for some reason it uses hex colors with 0xFF in the start just like Just Dance Now

        if f'world/maps/{mapName.lower()}/timeline/moves' and '.gesture' not in motion_clip['MoveName']:
            motion_clip['ClassifierPath'] = f"world/maps/{mapName.lower()}/timeline/moves/{motion_clip['MoveName']}.msm"
            motion_clip.pop('MoveName')
            motion_clip['MotionPlatformSpecifics'] = {"X360":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1},"ORBIS":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":-0.200000,"HighThreshold":0.600000},"DURANGO":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1}}
            tape['Clips'].append(motion_clip)

    if 'GoldEffectClips' in map_json['DanceData']:
        for gold_move in map_json['DanceData']['GoldEffectClips']:
            gold_move['__class'] = "GoldEffectClip" 
            gold_move['EffectType'] = 1
            tape['Clips'].append(gold_move)

    # Picto Clips
    for picto_clips in map_json['DanceData']['PictoClips']:
        picto_clips['PictoPath'] = f"world/maps/{mapName.lower()}/timeline/pictos/{picto_clips['PictoPath']}.png"
        picto_clips['__class'] = 'PictogramClip'

        tape['Clips'].append(picto_clips)

    Util.save_file(f'output/{mapName}/{mapName.lower()}_tml_dance.dtape.ckd', tape, True)
    Util.log(mapName, 'Successfully generated DanceData tape.')

    # ---- MusicTrack Tape ----
    music_track_structure = music_track['m_structure']['MusicTrackStructure']
    markers = []

    for marker in music_track_structure['markers']:
        markers.append(marker['VAL'])

    
    Util.save_file(f'output/{mapName}/{mapName.lower()}_musictrack.tpl.ckd', {
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
                "path": f"world/maps/{mapName.lower()}/audio/{mapName.lower()}.ogg",
                "url": f"jmcs://jd-contents/{mapName}/{mapName}.ogg"
            }
        }
    ]
}, False)
    Util.log(mapName, 'Successfully generated MusicTrack tpl.')

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
    pictos_path = Util.filePath(f'{filesPath}/pictos', f'{filesPath}/Sprite', 'Cannot find your pictograms path', False)
    if pictos_path:
        Util.log(mapName, 'Input pictograms folder found, resizing...')
        Util.make_folder(f'output/{mapName}/pictos')

        for file_name in os.listdir(pictos_path):
            Util.convert_pictogram(f'{pictos_path}/{file_name}', f'output/{mapName}/pictos/{file_name}', NumCoach)
            
    # renaming moves files
    msm_path = Util.filePath(f'{filesPath}/moves', f'{filesPath}/TextAsset', 'Cannot find your moves path', False)
    if msm_path:
        Util.log(mapName, 'Input moves folder found, renaming...')
        Util.make_folder(f'output/{mapName}/moves')
        for filename in os.listdir(msm_path):
            shutil.copyfile(f'{msm_path}/{filename.lower()}', f'output/{mapName}/moves/{filename.lower()}')
    
    Util.log('tool', 'Done!')