# image-color-analysis
Szakdolgozat projekt

A `pictures` mappa a teszteléshez használt mintaképeket tartalmazza, de a program más képek elemzésére is alkalmas új képek hozzáadásával, illetve egy teljesen új, képekkel feltöltött mappa megadásával.

A `pictures.zip` kicsomagolásakor fontos, hogy a képfájlok közvetlenül a `pictures` mappába kerüljenek.

Helyes mappaszerkezet:

pictures/
  kep1.jpg
  kep2.jpg
  ...

Helytelen mappaszerkezet:

pictures/pictures/
  kep1.jpg
  kep2.jpg

A `train_dataset` mappa a tanítóképek kezelésére szolgál, amely lehetőséget biztosít a modell további tesztelésére és bővítésére.
A szakdolgozat során használt teljes tanító adatkészlet mérete miatt nem került feltöltésre a mellékletek közé. Az adatkészlet az alábbi linken letölthető:
https://drive.google.com/file/d/1wc_cSvTEd9FH31rJ4B76N8OAFudwJ0z4/view?usp=sharing

https://1drv.ms/u/c/94230f54b0e90d42/IQAyDst-2ddzTY2U1VtV4KV_AS6lQqZqH5XiSKC_0QVLOR8?e=bXO9Wj


Futtatás (Windows):

1) Nyiss Parancssort (CMD) abban a mappában,
   ahol a main.py található.

2) Virtuális környezet létrehozása:

   py -3.12 -m venv .venv

4) Virtuális környezet aktiválása:

   .\\.venv\Scripts\activate.bat

5) Csomagok telepítése:

   python -m pip install --upgrade pip

   python -m pip install -r requirements.txt

7) Program indítása:

   python main.py


Futtatás (Linux):

1) Nyiss egy terminált abban a mappában, ahol a main.py fájl található.

2) Virtuális környezet létrehozása:

   python3.12 -m venv .venv

4) Virtuális környezet aktiválása:

   source .venv/bin/activate

6) Csomagok telepítése:

   python -m pip install --upgrade pip

   python -m pip install -r requirements.txt

8) Program indítása:

   python main.py
