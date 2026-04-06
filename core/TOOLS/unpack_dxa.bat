chcp 932
echo "Drag a file to this bat to extract dxa!"
%~dp0LocaleEmu/LEProc.exe %~dp0DxaDecode.exe -K:whisperkeizo777 "%~1"
echo "Finished!"
