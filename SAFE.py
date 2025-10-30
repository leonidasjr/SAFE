# -*- coding: utf-8 -*-
import os, subprocess, shutil, glob, datetime, time

#Function to replace non a-z/A-Z letter.
def replace_chars(text_value):
    replacements = {
        "á": "a", "â": "a", "ã": "a", "à": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "Á": "A", "Â": "A", "Ã": "A", "À": "A",
        "É": "E", "Ê": "E",
        "Í": "I",
        "Ó": "O", "Ô": "O", "Õ": "O",
        "Ú": "U",
        "ç": "c", "Ç": "C",
        "WEBVTT": "", "0": "", "1": "", "2": "", "3": "", "4": "", "5": "", "6": "", "7": "", "8": "", "9": "",
        ",": "", "!": "", "?": "", ":": "", ";": "", '"': "", ">": "", "_": "", "-": "", "'": "", "\n\n": "", "--": "", ".": ""
    }
    for old, new in replacements.items():
        text_value = text_value.replace(old, new)
    return text_value.strip()

#Procedure to show information to the user.
def log(verbose,text):
    if verbose:
        ts = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        print(ts + ' -> ' + text)

#Function to print time in a specific format.
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

#Function to totalize all data from "analytics" files.
def totalizeSummary(path):
    analyticsFileNames = []
    for file in os.listdir(path):
        if file.endswith('_analytics.txt'):
            analyticsFileNames.append(file)
    globalSummaryVowels = 0
    globalSummaryConsonants = 0
    globalSummaryPauses = 0
    globalSummaryVV_units = 0
    globalSummaryWords = 0
    for file in analyticsFileNames:
        fh = open(path+file)
        fc = fh.read()
        fh.close()
        lines = fc.splitlines()
        globalSummaryVowels = globalSummaryVowels + int(lines[3].split(' ')[0])
        globalSummaryConsonants = globalSummaryConsonants + int(lines[4].split(' ')[0])
        globalSummaryPauses = globalSummaryPauses + int(lines[5].split(' ')[0])
        globalSummaryVV_units = globalSummaryVV_units + int(lines[6].split(' ')[0])
        globalSummaryWords = globalSummaryWords + int(lines[7].split(' ')[0])
    return globalSummaryVowels, globalSummaryConsonants, globalSummaryPauses, globalSummaryVV_units, globalSummaryWords


#Procedure to retag all input files.
def retagFiles():
    rootDirectory = os.getcwd()
    # create a list of 'FEM' ('Female')  and 'MAL' ('Male') speakers as long as the number of files
    lans = ['AmE', 'BPT']
    sexes = ['FEM', 'MAL']
    # specify the type of file (file pattern) of your old file names
    sound_types = ["*.wav", "*.flac"]
    file_types = [".TextGrid", ".wav", ".flac", ".txt", ".vtt"]
    # main loop
    for lan in lans:
        for sex in sexes:
            i = 0
            # specify the directory you want to rename files in
            directory = '.\\'+lan+'\\'+sex
            # get a list of all file names in the directory that match the pattern
            old_sound_names = []
            os.chdir(directory)
            # get a list of all sound names
            for sound_type in sound_types:
                old_sound_names = old_sound_names + glob.glob(os.path.join('.', sound_type))
            old_sound_names = [os.path.splitext(osn)[0] for osn in old_sound_names]
            old_sound_names = list( dict.fromkeys(old_sound_names) )
            old_sound_names.sort()
            os.chdir(rootDirectory)
            # create new file name based on old file name
            # here we add a prefix 'LAN_SEX_' (which stands for speaker language and sex), 
            # and a counter to all files matching the file types (i.e, ~01.wav/.TextGrid, ~02.wav/.TextGrid...)
            for old_sound_name in old_sound_names:
                i = i + 1
                for file_type in file_types:
                    old_file_name = old_sound_name+file_type
                    if os.path.isfile( os.path.join(directory,old_file_name) ):
                        new_file_name = f'{lan}_{sex}_{i:03d}' + file_type
                        shutil.copy2(os.path.join(directory,old_file_name), new_file_name)

verbose = True
print('=========================================================================')
print('Python script that:')
print('    1. prepares transcription data,')
print('    2. calls AudioTrimmer.praat script file by file to trim sound signal,')
print('    3. calls MFA to align sound and text, returning TextGrid files.')
print('=========================================================================')
log(verbose,'Script started.')

#----- Retag Files -----
log(verbose,'Retag file process started.')
retagFiles()
log(verbose,'Retag file process concluded.')
#--- End Retag Files ---

fileNames_aux = os.listdir("./")

fileNames = []
for fileName in fileNames_aux:
    if fileName.find('.flac') > -1:
        fileNames.append(fileName[:-5])

if not os.path.isdir('output'):
    log(verbose,'\output dir does not exist.')
    os.mkdir('output')
    log(verbose,'output dir created.')
else:
    shutil.rmtree('output')
    os.mkdir('output')
    log(verbose,'output dir cleaned.')
if not os.path.isdir('output\\temp'):
    log(verbose,'output\\temp dir does not exist.')
    os.mkdir('output\\temp')
    log(verbose,'output\\temp dir created.')
else:
    shutil.rmtree('output\\temp')
    os.mkdir('output\\temp')
    log(verbose,'output\\temp dir cleaned.')

rnd = 0
dt_total = 0
for fileName in fileNames:
    ti = time.time()
    rnd = rnd + 1
    print('\n')
    print('------------------ Round %d / %d -------------------'%(rnd,len(fileNames)))
    log(verbose,'Running %d / %d [%s].'%(rnd,len(fileNames),fileName))

    #----- DataPreparator -----
    log(verbose,'Data preparation started.')
    print('')
    print('+++++ Data Preparation - Round %d +++++'%(rnd))
    
    fh = open(fileName+'.vtt','r',encoding="utf-8")
    fc = fh.read()
    fh.close()

    vttLines = fc.splitlines()
    
    vttList = []
    i_fix = -1
    for i in range(0,len(vttLines)):
        if (len(vttLines[i]) == 29) and ((vttLines[i].find('-->') > -1)):
            i_fix = i_fix + 1
            vttList.append([vttLines[i],''])
        elif (i_fix > -1):
            if (vttLines[i] != '') and (i<len(vttLines)-1):
                vttList[i_fix][1] = vttList[i_fix][1] + vttLines[i] + '\n'
            else:
                vttList[i_fix][1] = vttList[i_fix][1].rstrip("\n")
    startTimeH = float(vttList[1][0][0:2])
    startTimeM = float(vttList[1][0][3:5])
    startTimeS = float(vttList[1][0][6:12])
    endTimeH = float(vttList[-3][0][17:19])
    endTimeM = float(vttList[-3][0][20:22])
    endTimeS = float(vttList[-3][0][23:])

    textFileContent = ''
    for i in range(0,len(vttList)):
        if (i >= 1) and (i <= len(vttList)-3):
            textFileContent = textFileContent + vttList[i][1] + '\n'
    textFileContent = textFileContent.rstrip('\n')
    textFileContent = replace_chars(textFileContent)
    fh = open('.\\output\\temp\\'+fileName+'_trimmed.txt','w')
    fh.write(textFileContent)
    fh.close()
    log(verbose,'Text file created.')

    soundName = fileName+'.flac'
    startTime = str(startTimeH*3600 + startTimeM*60 + startTimeS) # sec.
    endTime = str(endTimeH*3600 + endTimeM*60 + endTimeS) # sec.
    silence = '0.5' # sec.

    print('····· Praat script call - Round %d ·····'%(rnd))
    resp = subprocess.call(['..\\Praat.exe', '--run', 'AudioTrimmer.praat', soundName, startTime, endTime, silence])
    print('········································')
    if resp == 0:
        if os.path.isfile('.\\output\\temp\\'+fileName+'_trimmed.flac'):
            os.remove('.\\output\\temp\\'+fileName+'_trimmed.flac')
        os.rename('.\\'+fileName+'_trimmed.flac','.\\output\\temp\\'+fileName+'_trimmed.flac')
        log(verbose,'Trimmed sound file created.')
    else:
        log(verbose,"Praat script execution error.")
    print('+++++++++++++++++++++++++++++++++++++++')
    print('')
    log(verbose,'Data preparation concluded.')
    #----- End DataPreparator -----
    
    #----- Aligner -----
    log(verbose,'Alignment started.')
    print('')
    print('+++++ Alignment - Round %d +++++'%(rnd))
    soundAndTextDirectory = 'C:\\Praat\\Aligner\\output\\temp'
    dictionary = 'portuguese_brazil_mfa'
    acustic = 'portuguese_mfa'
    textGridDirectory = 'C:\\Praat\\Aligner\\output\\temp'
    print('····· MFA call - Round %d ·····'%(rnd))
    resp = os.system('Aligner.bat '+soundAndTextDirectory+' '+dictionary+' '+acustic+' '+textGridDirectory)
    print('·······························')
    if resp == 0:
        log(verbose,'TextGrid file created.')
    else:
        log(verbose,"MFA execution error.")
    log(verbose,'Alignment concluded.')
    print('++++++++++++++++++++++++++++++++')
    print('')
    #----- End Aligner -----

    #----- Reprocessor -----
    log(verbose,'TextGrid Reprocessing started.')
    print('')
    print('+++++ TextGrid Reprocessing - Round %d +++++'%(rnd))
    path = 'output\\temp\\'
    soundName = fileName+'_trimmed.flac'
    pauseDetection = '0.65' # sec.

    print('····· Praat script call - Round %d ·····'%(rnd))
    resp = subprocess.call(['..\\Praat.exe', '--run', 'VVunitAligner.praat', path, soundName, pauseDetection])
    print('········································')
    if resp == 0:
        log(verbose,'TextGrid and result files created.')
    else:
        log(verbose,"Praat script execution error.")
    print('+++++++++++++++++++++++++++++++++++++++')
    print('')
    log(verbose,'TextGrid Reprocessing concluded.')
    #----- End Reprocessor -----

    #----- File transfer -----
    if resp == 0:
        for ext in ['.flac','.txt','.TextGrid', '_MFA.TextGrid', '_MFA_VV.TextGrid', '_analytics.txt']:
            if os.path.isfile('.\\output\\'+fileName+'_trimmed'+ext):
                os.remove('.\\output\\'+fileName+'_trimmed'+ext)
            os.rename('.\\output\\temp\\'+fileName+'_trimmed'+ext,'.\\output\\'+fileName+'_trimmed'+ext)
        log(verbose,'Files transfered to \\output directory.')
    #----- File transfer -----

    tf = time.time()
    dt = tf-ti
    dt_total = dt_total + dt
    log(verbose,'Round %d concluded. [Time of this round = %s]'%(rnd,printTime(dt)))
    print('-------------------------------------------------------')
    print('\n')
    log(verbose,'Elapsed time: %s. [Progress: %d%%]'%(printTime(dt_total), 100*rnd/len(fileNames)))
    if rnd < len(fileNames):
        log(verbose,'Estimated time to finish: %s. [Remaining: %d%%]'%(printTime(dt_total/rnd * (len(fileNames)-rnd)), 100 - 100*rnd/len(fileNames)))

#----- Summary -----
globalSummaryVowels, globalSummaryConsonants, globalSummaryPauses, globalSummaryVV_units, globalSummaryWords = totalizeSummary('output\\')
strInfo =         '---------------------------------'+'\n'
strInfo = strInfo+'Global Summary from TextGrid Data'+'\n'
strInfo = strInfo+'---------------------------------'+'\n'
strInfo = strInfo+str(globalSummaryVowels)+' vowels'+'\n'
strInfo = strInfo+str(globalSummaryConsonants)+' consonants'+'\n'
strInfo = strInfo+str(globalSummaryPauses)+' pauses'+'\n'
strInfo = strInfo+str(globalSummaryVV_units)+' VV_units'+'\n'
strInfo = strInfo+str(globalSummaryWords)+' words'+'\n'
strInfo = strInfo+'---------------------------------'
log(verbose,'Global Summary.\n'+strInfo)
ts = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
fh = open('output\\Global_Sumary_Analytics.txt','w')
fh.write(ts+'\n'+strInfo)
#----- End Summary -----

log(verbose,'Script ended.')
print('=========================================================================')