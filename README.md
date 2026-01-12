# image-color-analysis
Szakdolgozat projekt

(Megjegyzés: ha a virtuális környezet már létezik és tartalmazza a csomagokat,
a 4. lépés kihagyható.)

A pictures mappa a teszteléshez használt mintaképeket tartalmazza, de a program más képek elemzésére is alkalmas új képek hozzáadásával, illetve egy teljesen új, képekkel feltöltött mappa megadásával.
A train_dataset mappa a tanítóképek kezelésére szolgál, amely lehetőséget biztosít a modell további tesztelésére és bővítésére.


Futtatás (Windows):

1) Nyiss Parancssort (CMD) abban a mappában,
   ahol a main.py található.

2) Virtuális környezet létrehozása:
   py -3.12 -m venv .venv

3) Virtuális környezet aktiválása:
   .\.venv\Scripts\activate.bat

4) Csomagok telepítése:
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt

5) Program indítása:
   python main.py


Futtatás (Linux):

1) Nyiss egy terminált abban a mappában, ahol a main.py fájl található.

2) Virtuális környezet létrehozása:
   python3.12 -m venv .venv

3) Virtuális környezet aktiválása:
   source .venv/bin/activate

4) Csomagok telepítése:
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt

5) Program indítása:
   python main.py
