from aiogram.fsm.state import State, StatesGroup

# Группа состояний для процесса регистрации
class Registration(StatesGroup):
    email = State()
    password = State()

# Группа состояний для процесса распознавания дефектов
class DefectRecognition(StatesGroup):
    printer = State()
    quality = State()
    photo = State()

# Группа состояний для обратной связи
class FeedbackStates(StatesGroup):
    name = State()
    email = State()
    message = State()
