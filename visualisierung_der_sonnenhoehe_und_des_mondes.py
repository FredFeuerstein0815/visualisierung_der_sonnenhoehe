#!/usr/bin/env python
# coding=utf-8

import mysql.connector
from PIL import Image, ImageDraw, ImageFont
import datetime

TEXT_FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
TEXT_FONT_SIZE = 16
TEXT_COLOR = "grey"
TEXT_POS_H = 0
offset = 90
max_hoehe = 90
px_sonne = 25
px_mond = 25
px_horizont = 75
width = 1024
height = 650


def main():
    db = mysql.connector.connect(
        host='127.0.0.1',
        user='mondphase',
        password='mondphase',
        database='mondphase'
    )
    cursor = db.cursor()
    cursor.execute("SELECT mondphase FROM daten WHERE `datumzeit` >= NOW() - INTERVAL 24 DAY_HOUR ORDER BY `daten`.`datumzeit` DESC LIMIT 1;")
    eintraege = cursor.fetchall()
    for x in eintraege:
        mondphase = x[0]
    cursor.close()
    db.close()
    print("Mondphase {}".format(mondphase))

    db = mysql.connector.connect(
        host='127.0.0.1',
        user='sonne',
        password='sonne',
        database='sonne'
    )
    cursor = db.cursor()
    cursor.execute("SELECT sonnenhoehe, azimuth FROM daten WHERE `datumzeit` >= NOW() - INTERVAL 24 DAY_HOUR ORDER BY `daten`.`datumzeit` DESC LIMIT 1;")
    eintraege = cursor.fetchall()
    for x in eintraege:
        sonnenhoehe = x[0]
        azimuth = x[1]
        print("Sonnenhöhe {0}\nAzimuth {1}\n".format(sonnenhoehe, azimuth))
    cursor.close()
    db.close()

    db = mysql.connector.connect(
        host='127.0.0.1',
        user='mond',
        password='mond',
        database='mond'
    )
    cursor = db.cursor()
    cursor.execute("SELECT mondhoehe, mondazimuth FROM daten WHERE `datumzeit` >= NOW() - INTERVAL 24 DAY_HOUR ORDER BY `daten`.`datumzeit` DESC LIMIT 1;")
    eintraege = cursor.fetchall()
    for x in eintraege:
        mondhoehe = x[0]
        mondazimuth = x[1]
        print("Mondhöhe {0}\nMondazimuth {1}\n".format(mondhoehe, mondazimuth))
    cursor.close()
    db.close()

    print("Breite: {0}".format(width))
    print("Höhe: {0}".format(height))

    if sonnenhoehe >= 4:
        print("Bilder für Tags")
        pferdbild_pfad = "pferd_tags.png"
        vordergrund_pfad = "wiese_haus.png"
        hintergrund_pfad = "blauer_himmel.png"
        sonnenbild_pfad = "sonne.png"
        mondbild_pfad = "/mondphasen_25x25/"+ str(mondphase) +".png"
    elif sonnenhoehe <=4:
        if mondphase >=8 and mondphase <=16:
            pferdbild_pfad = "wolf.png"
            vordergrund_pfad = "wiese_haus.png"
            hintergrund_pfad = "sterne.png"
            sonnenbild_pfad = "1px_transparent.png"
            mondbild_pfad = "/mondphasen_25x25/"+ str(mondphase) +".png"
        else:
            pferdbild_pfad = "pferd_mit_fackel.png"
            vordergrund_pfad = "wiese_haus.png"
            hintergrund_pfad = "sterne.png"
            sonnenbild_pfad = "1px_transparent.png"
            mondbild_pfad = "/mondphasen_25x25/"+ str(mondphase) +".png"
    else:
        print("Fehler")
    hintergrund = Image.open(hintergrund_pfad).resize((width, height))
    vordergrund = Image.open(vordergrund_pfad).resize((width, height))
    sonnenbild = Image.open(sonnenbild_pfad).convert("RGBA")
    mondbild = Image.open(mondbild_pfad).convert("RGBA")
    pferdbild = Image.open(pferdbild_pfad).convert("RGBA")

    if sonnenhoehe >= 4 and mondhoehe >= 4 and mondazimuth >= 90 and mondazimuth <= 270:
        print("Sonne und Mond über dem Horizont und Mondazimut zw. 90 und 270")
        sonne_x = int(((azimuth - offset)*(width/180))+(px_sonne))
        sonne_y = int((sonnenhoehe*(height/max_hoehe) - height)*-1)
        mond_x = int(((mondazimuth - offset)*(width/180))+(px_mond))
        mond_y = int((mondhoehe*(height/max_hoehe) - height)*-1)
    else:
        print("Sonne oder Mond unter dem Horizont")
        if mondhoehe <= 4:
            print("Mond unter dem Horizont: {}".format(mondhoehe))
            mond_x = 1
            mond_y = 1
            if sonnenhoehe >= 4:
                sonne_x = int(((azimuth - offset)*(width/180))+(px_sonne))
                sonne_y = int((sonnenhoehe*(height/max_hoehe) - height)*-1)
            else:
                sonne_x = 1
                sonne_y = 1
        elif mondhoehe >= 4:
            print("Mond über 4: {}".format(mondhoehe))
            mond_y = int(((mondhoehe*(height/max_hoehe) - height)*-1)+(px_mond))
            if mondazimuth >= 90 and mondazimuth <= 270:
                mond_x = int(((mondazimuth - offset)*(width/180))+(px_mond))
                sonne_x = 1
                sonne_y = 1
            elif mondazimuth <= 90 or mondazimuth >= 270:
                print("Mond vor Osten oder über Westen hinaus: {}".format(mondazimuth))
                mond_x = 1
                mond_y = 1
                if sonnenhoehe >= 4:
                    print("aber Sonnenhoehe über 4 : {}".format(sonnenhoehe))
                    sonne_x = int(((azimuth - offset)*(width/180))+(px_sonne))
                    sonne_y = int((sonnenhoehe*(height/max_hoehe) - height)*-1)
                else:
                    print("aber Sonnenhoehe unter 4 : {}".format(sonnenhoehe))
                    sonne_x = 1
                    sonne_y = 1
        else:
            print("Fehler")
            mond_x = 1
            mond_y = 1
    print("Mond_x {}".format(mond_x))
    print("Mond_y {}".format(mond_y))
    print("Sonne_x {}".format(sonne_x))
    print("Sonne_y {}".format(sonne_y))

    neues_bild = Image.new("RGBA", (width, height))
    neues_bild.paste(hintergrund, (0, 0))
    if sonne_x == 1 and sonne_y == 1:
        sonnenbild = Image.open("1px_transparent.png").convert("RGBA")
    else:
        neues_bild.paste(sonnenbild, (int(sonne_x), int(sonne_y)), sonnenbild)
    if mond_x == 1 and mond_y == 1:
        mondbild = Image.open("1px_transparent.png").convert("RGBA")
    else:
        neues_bild.paste(mondbild, (int(mond_x), int(mond_y)), mondbild)
    neues_bild.paste(vordergrund, (0, 0), vordergrund)
    neues_bild.paste(pferdbild, (width-450, height-120), pferdbild)
    zeichne = ImageDraw.Draw(neues_bild)
    datumzeit = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(datumzeit)
    font = ImageFont.truetype(TEXT_FONT, TEXT_FONT_SIZE)
    zeichne.text((50, 0), datumzeit, fill="grey", font=font)

    neues_bild.save("neu.png")

if __name__ == "__main__":
    main()
