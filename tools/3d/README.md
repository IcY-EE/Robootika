# 3D-failide generaator

Kõik prindifailid, 3D-mudel ja 1:1 joonis on tehtud ühest geomeetriast.

1. `python3 geom.py` – arvutab osade asukohad, juhtmeteed ja LED-riba tee → `geom.json`
2. `python3 parts.py` – kirjutab iga prinditava osa CSG-käsufailiks kausta `csg/`
3. `csg.cpp` – loeb käsufaili ja teeb [manifold](https://github.com/elalish/manifold) teegiga STL-i:
   ```
   g++ -O2 -std=c++17 csg.cpp -I<manifold>/include -L<manifold>/build/src -lmanifold -o csg
   for f in csg/*.csg; do ./csg "$f" "../../hardware/3d/$(basename "$f" .csg).stl"; done
   ```
Mõõtude muutmiseks muuda konstante failide `geom.py` ja `parts.py` alguses.
