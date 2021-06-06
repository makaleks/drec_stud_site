from hamlpy.hamlpy_watcher import compile_file as ghtml
import os
import sass
import shutil, errno
from distutils.dir_util import copy_tree
gento = "../templates-gen/"
haml = {
    "core":[
        "base",
        "error",
        "login"
    ],
    "meeting_room":[
        "meeting_room_timetable"
    ],
    "news":[
        "archive_select",
        "news_list"
    ],
    "note":[
        "note_detail",
        "note_list",
        "qanda",
        "student_council"
    ],
    "reversion":[
        "revision_form"
    ],
    "service":[
        "service_base1",
        "service_list1",
        "service_timetable",
        "service_timetable_single"
    ],
    "service_base":[
        "service_base",
        "service_list"
    ],
    "service_document":[
        "service_document_timetable"
    ],
    "service_item":[
        "service_item_timetable"
    ],
    "survey":[
        "chart",
        "survey_detail",
        "survey_list",
        "survey_thanks"
    ],
    "user":[
        "long_logout",
        "uid_set"
    ],
    "washing":[
        "washing_timetable"
    ]
}

place = os.path.dirname(os.path.realpath(__file__))
compiled_folder = os.path.realpath(place + "/" + gento) + "/"
place = place + "/"

for folder in haml:
    if folder == "core":
        if not os.path.exists(compiled_folder + folder):
            os.makedirs(compiled_folder + folder)
    else:
        if not os.path.exists(compiled_folder + folder + "/templates"):
            os.makedirs(compiled_folder + folder + "/templates")

if not os.path.exists(compiled_folder + "static"):
    os.makedirs(compiled_folder + "static")
if not os.path.exists(compiled_folder + "static/css"):
    os.makedirs(compiled_folder + "static/css")
if not os.path.exists(compiled_folder + "static/js"):
    os.makedirs(compiled_folder + "static/js")

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def genhaml():
    hamlpath = [place + "templates/", "", ".haml"]
    htmlpath = [compiled_folder, "", ".html"]

    gargs = {'django_inline_style': True}

    for address in haml:
        for filename in haml[address]:
            hamlpath[1] = address + "/" + filename
            if address == "core":
                htmlpath[1] = address + "/" + filename
            else:
                htmlpath[1] = address + "/templates/" + filename
            ginput = ''.join(hamlpath)
            goutput = ''.join(htmlpath)
            ghtml(ginput, goutput, gargs)

def main():
    copy_tree(place + "static/img", compiled_folder + "static/img")
    copy_tree(place + "static/js", compiled_folder + "static/js")
    copy_tree(place + "static/web_copy", compiled_folder + "static/web_copy")
    if os.path.exists(place + "config/img"):
        copy_tree(place + "config/img", compiled_folder + "static/img")
    if not os.path.exists(place + "sass/config"):
        os.makedirs(place + "sass/config")
    open(place + "sass/config/_theme.sass", 'w').close()
    if os.path.isfile(place + "config/_theme.sass"):
        shutil.copyfile(place + "config/_theme.sass", place + "sass/config/_theme.sass")
    genhaml()
    sass.compile(dirname=(place + "sass", compiled_folder + "static/css"), output_style='compressed')

if __name__ == '__main__':
    main()
