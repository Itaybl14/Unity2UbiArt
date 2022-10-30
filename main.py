# Unity2Ubiart by Rama and Itay

import json, os
from random import randint

print('Unity2Ubiart by Rama and Itay')

def hextoubiart(hex):
    # hex2ubiart by WorteJD, source: https://github.com/WorteJD/HEX-to-UbiArt-Color
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    output = []
    output.append(str(float(100) / 100)[:8])
    output.append(str(rgb[0] / 255)[:8])
    output.append(str(rgb[1] / 255)[:8])
    output.append(str(rgb[2] / 255)[:8])
    uac = []
    for color in output:
        uac.append(float(color))
    return uac

for filename in os.listdir('input'):
    mainjson = json.load(open('input/' + filename, encoding='UTF-8')) # loading the json file
    MapName = mainjson['m_Name']
    tape = {"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":MapName,"SoundwichEvent":""}
    print(f'[CONVERTING] {MapName}')
    try:
        os.mkdir('output/' + MapName)
    except:
        pass
    # karaokeData Tape
    words = mainjson['m_karaokeData']['Clips'] # load words from mainjson
    for type in words:
        word = type['KaraokeClip']
        word["__class"] = 'KaraokeClip'
        tape['Clips'].append(word)
    open(f'output/{MapName}/{MapName.lower()}_tml_karaoke.ktape.ckd', 'w', encoding="utf-8").write(json.dumps(tape))

    # DanceData Tape
    tape['Clips'] = []
    dancedata = mainjson['m_danceData']['MotionClips']
    GoldEffectClips = []
    for move in dancedata:
        move['__class'] = 'MotionClip'
        move['Color'] = hextoubiart(move['Color'].replace('0xFF', '')) # for some reason it uses hex colors with 0xFF in the start just like Just Dance Now
        move['MotionPlatformSpecifics'] = {"X360":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1},"ORBIS":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":-0.200000,"HighThreshold":0.600000},"DURANGO":{"__class":"MotionPlatformSpecific","ScoreScale":1,"ScoreSmoothing":0,"LowThreshold":0.200000,"HighThreshold":1}}
        if move['GoldMove'] == 1 and move['StartTime'] not in GoldEffectClips: # making Gold Move Effect
            GoldEffectClips.append(move['StartTime']) # adding the StartTime to a list for not making multiple effects at the same time
            # were adding 12 to the starttime unless it will come too early
            tape['Clips'].append({"__class":"GoldEffectClip","IsActive":1,"Duration":24,"EffectType":0,"Id":randint(1000000000, 9999999999),"TrackId":randint(1000000000, 9999999999),"StartTime":move['StartTime'] + 12})
        if f'world/maps/{MapName.lower()}/timeline/moves/' not in move['ClassifierPath']:
            move['ClassifierPath'] = f'world/maps/{MapName.lower()}/timeline/moves/{move["ClassifierPath"]}'
        tape['Clips'].append(move)

    for picto in mainjson['m_danceData']['PictoClips']:
        picto['PictoPath'] = f"world/maps/{MapName.lower()}/timeline/pictos/{picto['PictoPath'] + '.png'}" # your picto has to be named pictoname.png.ckd !!
        picto['__class'] = 'PictogramClip'
        tape['Clips'].append(picto)
    
    tape['Clips'].sort(key=lambda x: x["StartTime"]) # sorting the clips by their StartTime
    open(f'output/{MapName}/{MapName.lower()}_tml_dance.dtape.ckd', 'w', encoding="utf-8").write(json.dumps(tape))

    # MusicTrack
    mt = {"__class":"Actor_Template","WIP":0,"LOWUPDATE":0,"UPDATE_LAYER":0,"PROCEDURAL":0,"STARTPAUSED":0,"FORCEISENVIRONMENT":0,"COMPONENTS":[{"__class":"MusicTrackComponent_Template","trackData":{"__class":"MusicTrackData","structure":{"__class":"MusicTrackStructure","markers":[],"signatures":[{"__class":"MusicSignature","marker":0,"beats":4}],"sections":[]},"path":f"world/maps/{MapName.lower()}/audio/{MapName.lower()}.wav","url":f"jmcs://jd-contents/{MapName}/{MapName}.ogg"}}]}
    MusicTrackStructure = mainjson['m_trackData']['m_structure']['MusicTrackStructure']
    for data in MusicTrackStructure:
        if data == 'videoStartTime':
            time = str(MusicTrackStructure['videoStartTime']).replace('.', '').replace('0', '')
            if int(time)/1000 > -1: # for some reason some maps needs it, probably a beta bug
                mt['COMPONENTS'][0]['trackData']['structure']['videoStartTime'] = MusicTrackStructure['videoStartTime']
            else:
                mt['COMPONENTS'][0]['trackData']['structure']['videoStartTime'] = float(int(time) / 1000.0)
        elif data == 'markers':
            for beat in MusicTrackStructure['markers']:
                mt['COMPONENTS'][0]['trackData']['structure']['markers'].append(beat['VAL'])
        elif data == 'comments' or data == 'sections' or data == 'signatures':
            pass
        else:
            mt['COMPONENTS'][0]['trackData']['structure'][data] = MusicTrackStructure[data]
    
    open(f'output/{MapName}/{MapName.lower()}_musictrack.tpl.ckd', 'w', encoding="utf-8").write(json.dumps(mt))

    # songDesc
    m_songDesc = mainjson['m_songDesc']
    NumCoach = m_songDesc['NumCoach']
    songdesc = {"__class":"Actor_Template","WIP":0,"LOWUPDATE":0,"UPDATE_LAYER":0,"PROCEDURAL":0,"STARTPAUSED":0,"FORCEISENVIRONMENT":0,"COMPONENTS":[{"__class":"JD_SongDescTemplate","MapName":MapName,"JDVersion":m_songDesc['JDVersion'],"OriginalJDVersion":m_songDesc['OriginalJDVersion'],"Artist":m_songDesc['Artist'],"DancerName":"Unknown Dancer","Title":m_songDesc['Title'],"Credits":m_songDesc['Credits'],"PhoneImages":{"cover":f"world/maps/{MapName.lower()}/menuart/textures/{MapName.lower()}_cover_phone.jpg"},"NumCoach":NumCoach,"MainCoach":-1,"Difficulty":m_songDesc['Difficulty'],"SweatDifficulty":m_songDesc['SweatDifficulty'],"backgroundType":0,"LyricsType":0,"Tags":["main"],"Status":3,"LocaleID":4294967295,"MojoValue":0,"CountInProgression":1,"DefaultColors":{"lyrics":[1,1,0,0],"theme":[1,1,1,1]},"VideoPreviewPath":""}]}
    for i in range(NumCoach):
        i += 1
        songdesc['COMPONENTS'][0]['PhoneImages'][f'coach{i}'] = f"world/maps/{MapName.lower()}/menuart/textures/{MapName.lower()}_coach_{i}_phone.png"

    open(f'output/{MapName}/songdesc.tpl.ckd', 'w', encoding="utf-8").write(json.dumps(songdesc))
    print(f"{m_songDesc['Title']} by {m_songDesc['Artist']}")
