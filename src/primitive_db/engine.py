#
import prompt


def welcome ():

    """Основной цикл"""


    name = ''

    while name != 'quit':
        name = prompt.string('ВВедите что нибудь - ')
