rem py -3 ./dig_decoder.py 
rem for %%a in (%*) do %~dp0dig_decoder.exe "%%a" -ND
cd %~dp0
for %%a in (%*) do %~dp0dig_decoder.exe "%%a" -ND
pause