from hamlpy.hamlpy_watcher import compile_file as ghtml
import os
import sass

place = os.path.dirname(os.path.realpath(__file__))

gento = "../gen/"

haml = ["core/base",
        "core/error",
        "core/login",
        "reversion/revision_form"
        ]

def pregen():
    compiled_folder = os.path.realpath(place + "/" + gento + "templates")
    if not os.path.exists(compiled_folder):
        os.makedirs(compiled_folder)
    if not os.path.exists(compiled_folder + "/core"):
        os.makedirs(compiled_folder + "/core")
    if not os.path.exists(compiled_folder + "/reversion"):
        os.makedirs(compiled_folder + "/reversion")

def genhaml():
    hamlpath = [os.path.realpath(place + "/" + "templates") + "/", "", ".haml"]
    htmlpath = [os.path.realpath(place + "/" + gento + "templates/") + "/", "", ".html"]

    gargs = {'django_inline_style': True}

    for address in haml:
        hamlpath[1] = address
        htmlpath[1] = address

        ginput = ''.join(hamlpath)
        goutput = ''.join(htmlpath)

        ghtml(ginput, goutput, gargs)

def main():
    pregen()
    genhaml()
    sass.compile(dirname=(os.path.realpath(place + "/" + "sass"), os.path.realpath(place + "/" + gento + "css")), output_style='compressed')

if __name__ == '__main__':
    main()
