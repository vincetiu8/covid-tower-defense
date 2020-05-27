How to create the .exe:
1. Install pyinstaller
2. Navigate to the download folder with `sergeant_t_cell.py`
3. Run the command:
`pyinstaller --onefile -w --add-data 'data;data' sergeant_t_cell.py` (Windows)
or `pyinstaller sergeant_t_cell.py --onefile --hidden-import 'packaging.requirements' --hidden-import 'pkg_resources.py2_warn' -w --add-data 'data:data'` (Linux)
4. This will create a folder called `dist` among other folders.  
Open this folder to get the exe.
5. Enjoy the game!
