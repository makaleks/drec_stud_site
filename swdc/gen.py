from hamlpy.hamlpy_watcher import compile_file as ghtml
import os
import sass

place = os.path.dirname(os.path.realpath(__file__))

gento = "../gen/"

haml = ["core/base",
        "core/error",
        "core/login",
        "comment/admin/comment/comment/change_form",
        "meeting_room/admin/meeting_room/meetingroom/change_form",
        "meeting_room/meeting_room_timetable",
#        "news/admin/news/news/change_form",
#        "news/archive_select",
#        "news/news_list",
        "note/admin/note/question/change_form",
        "note/admin/note/note/change_form",
        "note/note_detail",
        "note/note_list",
        "note/qanda",
#        "note/student_council",
        "reversion/revision_form",
        "service/admin/service/service/change_form"#,
#        "service_base/service_base",
#        "service_base/service_list",
#        "service_document/service_document_timetable",
#        "service_item/service_item_timetable",
#        "service/service_base1",
#        "service/service_list1",
#        "service/service_timetable",
#        "service/service_timetable_single",
#        "survey/admin/survey/survey/change_form",
#        "survey/chart",
#        "survey/survey_detail",
#        "survey/survey_list",
#        "survey/survey_thanks",
#        "user/admin/user/user/change_form",
#        "user/long_logout",
#        "user/uid_set",
#        "washing/admin/washing/washing/change_form",
#        "washing/washing_timetable"
        ]

def pregen():
    compiled_folder = os.path.realpath(place + "/" + gento + "templates")
    if not os.path.exists(compiled_folder):
        os.makedirs(compiled_folder)
    if not os.path.exists(compiled_folder + "/core"):
        os.makedirs(compiled_folder + "/core")
    if not os.path.exists(compiled_folder + "/comment/admin/comment/comment"):
        os.makedirs(compiled_folder + "/comment/admin/comment/comment")
    if not os.path.exists(compiled_folder + "/meeting_room/admin/meeting_room/meetingroom"):
        os.makedirs(compiled_folder + "/meeting_room/admin/meeting_room/meetingroom")
    if not os.path.exists(compiled_folder + "/note/admin/note/question"):
        os.makedirs(compiled_folder + "/note/admin/note/question")
    if not os.path.exists(compiled_folder + "/note/admin/note/note"):
        os.makedirs(compiled_folder + "/note/admin/note/note")
    if not os.path.exists(compiled_folder + "/service/admin/service/service"):
        os.makedirs(compiled_folder + "/service/admin/service/service")
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
