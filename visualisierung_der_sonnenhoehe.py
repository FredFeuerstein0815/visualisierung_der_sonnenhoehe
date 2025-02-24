#!/usr/bin/env python

import datetime
import logging
import mysql.connector
from mysql.connector import errorcode
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_COLOR = (0, 0, 255)
#
# Needs to be adjusted to get a nice view/perspective...
#
HEIGHT_OVER_HORIZON_MAX = 90
HEIGHT_OVER_HORIZON_DEFAULT = 45
AZIMUTH_DEFAULT = 180  # south

TEXT_FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
TEXT_FONT_SIZE = 48
TEXT_COLOR = "black"
#
# Distance from top of image in pixels:
# Ascender line (top) of the first line of text, as defined by the font
# (See https://pillow.readthedocs.io/en/latest/handbook/text-anchors.html)
#
TEXT_POS_H = 0

class Layer:
    def __init__(self, image, calculate_position=None, extra_args=()):
        self.image = image
        self.calculate_position = calculate_position
        self.extra_args = extra_args

    @property
    def width(self):
        return self.image.width

    @property
    def height(self):
        return self.image.height

    def get_position(self, width, height, azimuth, height_over_horizon):
        if self.calculate_position:
            return self.calculate_position(
                self.image,
                width,
                height,
                azimuth,
                height_over_horizon,
                *self.extra_args
            )
        else:
            return (0, 0)

class Layers:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

    @property
    def width(self):
        return max(layer.width for layer in self)

    @property
    def height(self):
        return max(layer.height for layer in self)

    def create_image(self, azimuth, height_over_horizon, message=""):
        width, height = self.width, self.height
        image = Image.new("RGBA", (width, height), color=BACKGROUND_COLOR)
        # Paste the layers from bottom to top
        for layer in reversed(self):
            image.paste(
                layer.image,
                layer.get_position(
                    width, height, azimuth, height_over_horizon
                ),
                layer.image,
            )

        ImageDraw.Draw(image).text(
            (width // 2, TEXT_POS_H),
            message,
            fill=TEXT_COLOR,
            anchor="ma",
            font=ImageFont.truetype(TEXT_FONT, TEXT_FONT_SIZE),
        )
        return image


def get_relative_position(
    _image, width, height, _azimuth, _height_over_horizon, relative_position
):
    x, y = relative_position
    return (int(x * width), int(y * height))


def get_sun_position(image, width, height, azimuth, height_over_horizon):
    return (
        int((width - image.width) * (azimuth - 90) / 180),
        int(
            (height - image.height)
            * (1 - height_over_horizon / HEIGHT_OVER_HORIZON_MAX)
        ),
    )

def get_cloud_position(image, width, height, azimuth, height_over_horizon):
    # Note: azimuth and height_over_horizon are data from/for the sun!
    #
    # Just for testing/demo. Should be better some random position...
    # Something like this to not cover the sun
    azimuth = 360 - azimuth
    if 160 < azimuth < 200:
        azimuth = 160

    return get_sun_position(image, width, height, azimuth, height_over_horizon)

def load_image(filename):
    try:
        return Image.open(filename).convert("RGBA")
    except FileNotFoundError:
        logging.warning("Kein Bild %r gefunden !", filename)
        return Image.new("RGBA", (0, 0))

def main():
    msg=str((datetime.datetime.now().strftime('%d-%m-%Y %H:%M')))
    print(msg)
    db = mysql.connector.connect(user='user', password='password', host='127.0.0.1', database='database')
    cursor = db.cursor(prepared=True)
    sql = "SELECT sonnenhoehe, azimuth FROM daten WHERE `datumzeit` >= NOW() - INTERVAL 12 DAY_HOUR ORDER BY `daten`.`datumzeit` DESC LIMIT 1;"
    cursor.execute(sql)
    eintraege = cursor.fetchall()
    print("\nLetzter Eintrag aus der Datenbank:")
    for x in eintraege:
        sonnenhoehe = x[0]
        azimuth = x[1]
        print("Sonnenhöhe {0}\nAzimuth {1}\n".format(sonnenhoehe, azimuth))
        cursor.close()
        db.close()
    if sonnenhoehe < 2:
        Layers(
            [
                Layer(load_image("pferd_nachts.png"), calculate_position=get_relative_position, extra_args=[(0.6, 0.8)]),
                Layer(load_image("wiese_haus_dunkel.png")),
#                Layer(load_image("wolke.png"), calculate_position=get_cloud_position),
                Layer(load_image("sonne_25px.png"), calculate_position=get_sun_position),
                Layer(load_image("sterne.png")),
            ]
        ).create_image(azimuth, sonnenhoehe, msg).save("/dev/shm/sonnenstand_zenit_azimuth_freiburg.png")

    else:
        Layers(
            [
                Layer(load_image("pferd_tags.png"), calculate_position=get_relative_position, extra_args=[(0.6, 0.8)]),
                Layer(load_image("wiese_haus_sonnig.png")),
#                Layer(load_image("wolke.png"), calculate_position=get_cloud_position),
                Layer(load_image("sonne_25px.png"), calculate_position=get_sun_position),
                Layer(load_image("blauer_himmel.png")),
            ]
        ).create_image(azimuth, sonnenhoehe, msg).save("new.png")


if __name__ == "__main__":
    main()
