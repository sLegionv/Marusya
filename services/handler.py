import pytz
import pymorphy2
from datetime import datetime
from . import dbwrapper, convertNumber
morph = pymorphy2.MorphAnalyzer()
MONTHS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
          "август", "сентябрь", "октябрь", "ноябрь:", "декабрь"]

MONTHS_AMOUNT_DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

MONTHS_CASE = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
               "сентября", "октября", "ноября", "декабря"]

DAYS = ["первое", "второе", "третье",  "четвертое", "пятое", "шестое", "седьмое", "восьмое", "девятое", "десятое",
        "одиннадцатое", "двеннадцатое", "триннадцатое", "четырнадцатое", "пятнадцатое", "шестнадцатое",
        "семнадцатое", "восемнадцатое", "девятнадцатое", "двадцатое", "двадцать первое", "двадцать второе",
        "двадцать третье", "двадцать четвертое", "двадцать пятое", "двадцать шестое", "двадцать седьмое", "двадцать восьмое",
        "двадцать девятое", "тридцатое", "тридцать первое"]

DAYS_GENT = ["первого", "второго", "третьего",  "четвертого", "пятого", "шестого", "седьмого", "восьмого", "девятого", "десятого",
        "одиннадцатого", "двеннадцатого", "триннадцатого", "четырнадцатого", "пятнадцатого", "шестнадцатого",
        "семнадцатого", "восемнадцатого", "девятнадцатого", "двадцатого", "двадцать первого", "двадцать второго",
        "двадцать третьего", "двадцать четвертого", "двадцать пятого", "двадцать шестого", "двадцать седьмого", "двадцать восьмого",
        "двадцать девятого", "тридцатого", "тридцать первого"]

DATES_1 = ["{} {}".format(j + 1, MONTHS_CASE[i]) for i in range(len(MONTHS_AMOUNT_DAYS)) for j in range(MONTHS_AMOUNT_DAYS[i])]
DATES_2 = ["{} {}".format(str(j + 1).rjust(2, "0"), str(i + 1).rjust(2, "0")) for i in range(len(MONTHS_AMOUNT_DAYS)) for j in range(MONTHS_AMOUNT_DAYS[i])]
DATES_3 = ["{} {}".format(DAYS[j], MONTHS_CASE[i]) for i in range(len(MONTHS_AMOUNT_DAYS)) for j in range(MONTHS_AMOUNT_DAYS[i])]


class Handler:
    def __init__(self):
        self.listed_events = None
        self.date = 1, 1
        self.number_iteration_event = 0
        self.say_importance_event = True
        self.wait_importance = False
        self.additive = "Сегодня"

    def handle_dialog(self, request, response):
        date_user = self.receiving_date_user(request["meta"]["timezone"])
        response_user = response["response"]
        request_user = request["request"]
        words_user = self.transform_words(request_user)
        if request["session"]["new"]:
            self.start_conversation(response_user, date_user)
            self.edit_response(response_user)
            return
        if request_user["command"] == "on_interrupt":
            self.end_conversation(response_user)
            return
        self.continuation_conservation(response_user, words_user, date_user)
        self.edit_response(response_user)

    def start_conversation(self, response, date_user):
        response["text"] += "Добрый вечер, я историк-диспетчер."
        response["tts"] += "Добрый вечер, я историк-диспетчер."
        self.date = date_user.day, date_user.month
        self.listed_events = dbwrapper.get_events(date_user.day, date_user.month)
        count_events = self.listed_events.count()
        if count_events == 0:
            self.tell_about_lack_events(response, additive=self.additive)
            return
        first_event = self.listed_events.first()
        self.tell_event(response, first_event, additive=self.additive)
        self.offer_set_importance_event(response)
        self.say_importance_importance_event(response)
        self.offer_disenable_importance_event(response)

    def continuation_conservation(self, response, words_user, date_user):
        self.check_enable_importance_event(response, words_user)
        if self.wait_importance:
            receive_value = self.receive_importance(words_user)
            if receive_value is not None:
                self.wait_importance = False
                event = self.listed_events[self.number_iteration_event - 1]
                self.set_value_importance_event(event, receive_value)
            else:
                response["text"] += "Я ожидаю важность события. Нужно лишь число!"
                response["tts"] += "Я ожидаю важность события. Нужно лишь число!"
                return
        if self.check_new_date(words_user, date_user):
            count_events = self.listed_events.count()
            if count_events == 0:
                self.tell_about_lack_events(response, additive=self.additive)
                return
            self.number_iteration_event = 0
            event = self.listed_events.first()
            self.tell_event(response, event, additive=self.additive)
            if self.say_importance_event:
                self.offer_set_importance_event(response)
                return
            return
        if self.listed_events is None:
            self.wait_command(response)
            return
        if self.listed_events.count() - self.number_iteration_event == 0:
            self.tell_about_end_events(response, additive=self.additive)
            return
        if self.check_request_for_continue(words_user):
            event = self.listed_events[self.number_iteration_event]
            self.tell_event(response, event, additive=self.additive)
            if self.say_importance_event:
                self.offer_set_importance_event(response)
                return
        self.offer_to_continue(response)

    def end_conversation(self, response):
        response["text"] = "До связи, друг мой."
        response["tts"] = "До связи, друг мой."
        response["end_session"] = True

    def transform_words(self, request_user):
        words_user = []
        for word in request_user["nlu"]["tokens"]:
            try:
                words_user.append(morph.parse(word.lower())[0].normal_form)
            except Exception:
                words_user.append(word)
        return words_user

    def receiving_date_user(self, time_zone):
        time_zone_user = pytz.timezone(time_zone)
        time_user = datetime.now(tz=time_zone_user)
        date_user = time_user.now().date()
        return date_user

    def edit_response(self, response):
        response["text"] = ". ".join(response["text"].split("."))
        response["tts"] = ". ".join(response["tts"].split("."))

    def offer_to_continue(self, response):
        response["text"] += "Желаете продолжить список или выбрать другое число?"
        response["tts"] += "Желаете продолжить список или выбрать другое число?"

    def wait_command(self, response):
        response["text"] += "Прости, я не понимаю тебя. Я диспетчер-историк, назови день и месяц и получишь все события произошедшие в этот день!"
        response["tts"] += "Прости, я не понимаю тебя. Я диспетчер-историк, назови день и месяц и получишь все события произошедшие в этот день!"

    def tell_event(self, response, event, additive=None):
        day, month = self.date
        if additive is None:
            additive = "{} {}".format(day, MONTHS_CASE[month - 1])
            additive_tts = "{} {}".format(DAYS_GENT[day - 1], MONTHS_CASE[month - 1])
        else:
            additive = "В {}шнее число".format(additive)
            additive_tts = additive
        response["text"] += "{} в {} году {}".format(additive, str(event.year), event.description)
        response["tts"] += "{} в {} году {}".format(additive_tts, self.apply_convert_number(event.year), event.description)
        self.number_iteration_event += 1

    def apply_convert_number(self, number):
        number_str = convertNumber.num2text(number)
        if list(str(number))[-1] == "0":
            number_str += "ом"
        else:
            number_str = number_str.split()
            number_str[-1] = morph.parse(number_str[-1])[0].inflect({"ADJF", "Anum", "masc", "sing", "loct"}).word
            number_str = " ".join(number_str)
        return number_str

    def tell_about_lack_events(self, response, additive=None):
        day, month = self.date
        if additive is None:
            additive = "{} {}".format(day, MONTHS_CASE[month - 1])
            additive_tts = "{} {}".format(DAYS_GENT[day - 1], MONTHS_CASE[month - 1])
        else:
            additive = "В {}шнее число".format(additive)
            additive_tts = additive
        response["text"] += "{} не происходило никаких событий! Выбери любое другое число на твой вкус.".format(additive)
        response["tts"] += "{} не происходило никаких событий! Выбери любое другое число на твой вкус.".format(additive_tts)

    def tell_about_end_events(self, response, additive=None):
        day, month = self.date
        if additive is None:
            additive = "{} {}".format(day, MONTHS_CASE[month - 1])
            additive_tts = "{} {}".format(DAYS_GENT[day - 1], MONTHS_CASE[month - 1])
        else:
            additive = "В {}шнее число".format(additive)
            additive_tts = additive
        response["text"] += "{} больше не происходило никаких событий! Выбери другое число".format(additive)
        response["tts"] += "{} больше не происходило никаких событий! Выбери другое число".format(additive_tts)
        self.listed_events = None
        self.number_iteration_event = 0

    def offer_set_importance_event(self, response):
        response["text"] += "Оцените важность этого события от 0 до 3."
        response["tts"] += "Оцените важность этого события от нуля до трех."
        self.wait_importance = True

    def say_importance_importance_event(self, response):
        response["text"] += "Выставляя важность, я узнаю мнение общества о тех или иных событиях."
        response["tts"] += "Выставляя важность, я узнаю мнение общества о тех или иных событиях."

    def offer_disenable_importance_event(self, response):
        response["text"] += "Вы можете в любой момент попросить выключить или включить подобную опцию."
        response["tts"] += "Вы можете в любой момент попросить выключить или включить подобную опцию."

    def check_enable_importance_event(self, response, words_user):
        enable_words = ["включить", "врубить", "включение"]
        disenable_words = ["выключить", "вырубить", "выключение", "отключить", "отключение"]
        importance_word = "важность"
        if importance_word not in words_user:
            return False
        if any(word in enable_words for word in words_user):
            self.enable_importance_event(response, True)
        elif any(word in disenable_words for word in words_user):
            self.enable_importance_event(response, False)
            self.wait_importance = False
        else:
            return False
        return True

    def enable_importance_event(self, response, enable):
        value = "включена" if enable else "выключена"
        if enable == self.say_importance_event:
            response["text"] += "Важность событий уже {}.".format(value)
            response["tts"] += "Важность событий уже {}.".format(value)
            return
        self.say_importance_event = enable
        response["text"] += "Важность событий {}.".format(value)
        response["tts"] += "Важность событий {}.".format(value)

    def receive_importance(self, words_user):
        words = ["ноль", "один", "два", "три"]
        for i in range(len(words)):
            if words[i] in words_user or str(i) in words_user:
                return i
        return None

    def set_value_importance_event(self, event, value):
        dbwrapper.set_importance_event(event.id, value)

    def check_new_date(self, words_user, date_user):
        if "Сегодня" in words_user:
            self.additive = "Сегодня"
            self.date = date_user.day, date_user.month
            self.listed_events = dbwrapper.get_events(date_user.day, date_user.month)
            return True
        for i in range(len(DATES_1) - 1, -1, -1):
            date_1, date_2, date_3 = DATES_1[i], DATES_2[i], DATES_3[i]
            if date_1 in " ".join(words_user):
                day, month = date_1.split()
                month = MONTHS_CASE.index(month) + 1
                self.date = day, month
                self.listed_events = dbwrapper.get_events(day, month)
                self.additive = None
                return True
            elif date_2 in " ".join(words_user):
                day, month = map(int, date_2.split())
                self.date = day, month
                self.listed_events = dbwrapper.get_events(day, month)
                self.additive = None
                return True
            elif date_3 in " ".join(words_user):
                day, month = date_3.split()
                day, month = DAYS.index(day) + 1, MONTHS_CASE.index(month) + 1
                self.date = day, month
                self.listed_events = dbwrapper.get_events(day, month)
                self.additive = None
                return True
        return False

    def check_request_for_continue(self, words_user):
        words = ["продолжить", "дальше"]
        for word in words_user:
            if word in words:
                return True
        return False
