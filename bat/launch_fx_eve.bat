@echo off
call D:\rou\sync\tools\miniconda3\Scripts\activate.bat D:\rou\sync\tools\miniconda3
call conda activate foobar
D:
cd D:\rou\sync\pycharm_ws\foobar\eve
python svr_eve_fx.py
