# -*- coding: utf-8 -*-
import os, subprocess, shutil, glob, datetime, time

#Function to replace non a-z/A-Z letter.
def replace_chars(text_value):
    replacements = {
        "á": "a", "â": "a", "ã": "a", "à": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u", "Á": "A", "Â": "A", "Ã": "A", "À": "A",
        "É": "E", "Ê": "E",
        "Í": "I",
        "Ó": "O", "Ô": "O", "Õ": "O",
        "Ú": "U",
        "ç": "c", "Ç": "C",
        "WEBVTT": "", "0": "", "1": "", "2": "", "3": "", "4": "",
        "5": "", "6": "", "7": "", "8": "", "9": "",
        ",": "", "!": "", "?": "", ":": "", ";": "",
        '"': "", ">": "", "_": "", "-": "", "'": "",
        "\n\n": "", "--": "", ".": ""
    }
    for old, new in replacements.items():
        text_value = text_value.replace(old, new)
    return text_value.strip()

def log(verbose,text):
    if verbose:
        ts = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        print(ts + ' -> ' + text)

def printTime(time):
    if time < 60:
        return '%d sec'%(time)
    elif time < 3600:
        M = int(time/60)
        S = time - M*60
        return '%d min and %d sec'%(M,S)
    else:
        H = int(time/3600)
        M = int((time - H*3600)/60)
        S = time - H*3600 - M*60
        return '%d hours %d min and %d sec'%(H,M,S)

def totalizeSummary(path):
    analyticsFileNames = []
    for file in os.listdir(path):
        if file.endswith('_analytics.txt'):
            analyticsFileNames.append(file)
    V = C = P = VV = W = 0
    for file in analyticsFileNames:
        fh = open(path+file)
        lines = fh.read().splitlines()
        fh.close()
        V += int(lines[3].split(' ')[0])
        C += int(lines[4].split(' ')[0])
        P += int(lines[5].split(' ')[0])
        VV += int(lines[6].split(' ')[0])
        W += int(lines[7].split(' ')[0])
    return V, C, P, VV, W

def retagFiles():
    rootDirectory = os.getcwd()
    lans = ['AmE', 'BPT']
    sexes = ['FEM', 'MAL']
    sound_types = ["*.wav", "*.flac"]
    file_types = [".TextGrid", ".wav", ".flac", ".txt", ".vtt"]
    for lan in lans:
        for sex in sexes:
            i = 0
            directory = '.\\'+lan+'\\'+sex
            old_sound_names = []
            os.chdir(directory)
            for sound_type in sound_types:
                old_sound_names += glob.glob(os.path.join('.', sound_type))
            old_sound_names = list(dict.fromkeys([os.path.splitext(osn)[0] for osn in old_sound_names]))
            old_sound_names.sort()
            os.chdir(rootDirectory)
            for old_sound_name in old_sound_names:
                i += 1
                for file_type in file_types:
                    old_file_name = old_sound_name+file_type
                    if os.path.isfile(os.path.join(directory,old_file_name)):
                        new_file_name = f'{lan}_{sex}_{i:03d}' + file_type
                        shutil.copy2(os.path.join(directory,old_file_name), new_file_name)

verbose = True
print('=====================================================================')
print('++++++++++++++++++++++++ SAFE - Speech Alignment & Feature Extraction ++++++++++++++++++++++++')
print('An end2end-based Python script that prepares data, aligns speech and extracts acoustic features')
print('=====================================================================')
log(verbose,'Script started.')

#----- Retag Files -----
retagFiles()

fileNames = [f[:-5] for f in os.listdir("./") if f.endswith('.flac')]

if os.path.isdir('output'):
    shutil.rmtree('output')
os.mkdir('output')
os.mkdir('output\\temp')

rnd = 0
dt_total = 0

for fileName in fileNames:
    ti = time.time()
    rnd += 1

    # ----- Data Preparation -----
    fh = open(fileName+'.vtt','r',encoding="utf-8")
    vttLines = fh.read().splitlines()
    fh.close()

    vttList = []
    i_fix = -1
    for i in range(len(vttLines)):
        if (len(vttLines[i]) == 29) and ('-->' in vttLines[i]):
            i_fix += 1
            vttList.append([vttLines[i],''])
        elif i_fix > -1:
            if vttLines[i] != '' and i < len(vttLines)-1:
                vttList[i_fix][1] += vttLines[i] + '\n'
            else:
                vttList[i_fix][1] = vttList[i_fix][1].rstrip("\n")

    startTimeH = float(vttList[1][0][0:2])
    startTimeM = float(vttList[1][0][3:5])
    startTimeS = float(vttList[1][0][6:12])
    endTimeH = float(vttList[-3][0][17:19])
    endTimeM = float(vttList[-3][0][20:22])
    endTimeS = float(vttList[-3][0][23:])

    text = ''
    for i in range(1,len(vttList)-2):
        text += vttList[i][1] + '\n'
    text = replace_chars(text.rstrip('\n'))

    fh = open('.\\output\\temp\\'+fileName+'_trimmed.txt','w')
    fh.write(text)
    fh.close()

    subprocess.call(['..\\Praat.exe','--run','AudioTrimmer.praat',
                     fileName+'.flac',
                     str(startTimeH*3600+startTimeM*60+startTimeS),
                     str(endTimeH*3600+endTimeM*60+endTimeS),
                     '0.5'])

    os.rename('.\\'+fileName+'_trimmed.flac',
              '.\\output\\temp\\'+fileName+'_trimmed.flac')

    # ----- MFA Aligner -----
    os.system('Aligner.bat C:\\Praat\\Aligner\\output\\temp '
              'portuguese_brazil_mfa portuguese_mfa '
              'C:\\Praat\\Aligner\\output\\temp')

    # ----- VV-unit Reprocessor -----
    subprocess.call(['..\\Praat.exe','--run','VVunitAligner.praat',
                     'output\\temp\\',
                     fileName+'_trimmed.flac',
                     '0.65'])

    # ----- Speech Rhythm Extraction -----
    subprocess.call(['..\\Praat.exe','--run','SpeechRhythmExtractor.praat',
                     'output\\temp\\', 
                     fileName+'_trimmed.flac',
                    '00_prosodic_features',  # Output_file
                    '75',                    # left_F0_threshold
                    '500',                   # right_F0_threshold
                    '1',                     # V_to_V_tier
                    '2',                     # V_C_Pause_tier
                    '4'])                    # Chunk_tier

    # ----- File transfer -----
    for ext in ['.flac','.txt','.TextGrid',
                '_MFA.TextGrid','_MFA_VV.TextGrid','_analytics.txt']:
        if os.path.isfile('.\\output\\'+fileName+'_trimmed'+ext):
            os.remove('.\\output\\'+fileName+'_trimmed'+ext)
        os.rename('.\\output\\temp\\'+fileName+'_trimmed'+ext,
                  '.\\output\\'+fileName+'_trimmed'+ext)

    dt_total += (time.time()-ti)

#----- Summary -----
V,C,P,VV,W = totalizeSummary('output\\')
log(verbose,'Script ended.')
print('=====================================================================')
