chcp 932
echo "Drag a folder to this bat to pack to dxa!"
%~dp0DxaEncode.exe -K:whisperkeizo777 "%~1"
echo "Finished!"
pause