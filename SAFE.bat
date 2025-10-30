@echo off
call C:\ProgramData\Miniconda3\Library\bin\conda activate aligner
call mfa align --clean %1 %2 %3 %4
call C:\ProgramData\Miniconda3\Library\bin\conda deactivate