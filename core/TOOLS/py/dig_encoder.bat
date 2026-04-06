rem py -3 ./dig_decoder.py 
rem for %%a in (%*) do %~dp0dig_encoder.exe "%%a"
cd %~dp0
for %%a in (%*) do py -3 ./dig_encoder.py "%%a"
pause