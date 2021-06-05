# This should not be used for critical code, utility only

from background_task import background
from .models import Question
import datetime

#print('found!\n')

@background()
def clear_old_questions():
    # lookup user by id and send them a message
    print('clear_old_questions: {0}\n'.format((str(datetime.datetime.now()))))
    Question.objects.all().filter(is_approved = False, created__lt = datetime.datetime.now() - datetime.timedelta(days = 14)).delete()


clear_old_questions(repeat=3600*24)
