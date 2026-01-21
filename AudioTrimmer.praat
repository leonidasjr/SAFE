## AudioTrimmer.praat

form input Parameters
    sentence soundName
    positive startTime
	positive endTime
    positive silence
endform

Read from file... 'soundName$'
sound_file$ = selected$ ("Sound")
Extract all channels
select Sound 'sound_file$'_ch1

## cut-aligning with the audio
startTime = startTime - silence
endTime = endTime + silence
Extract part: startTime, endTime, "rectangular", 1, "yes"

select Sound 'sound_file$'_ch1_part
Save as FLAC file... 'sound_file$'_trimmed.flac

writeInfoLine: "Praat script successfully concluded."