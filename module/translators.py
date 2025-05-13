class BaseEntity:
    def __init__(self, code: str, name: str):
        self.__code = code
        self.__name = name

    @property
    def code(self) -> str:
        return self.__code

    @property
    def name(self) -> str:
        return self.__name


class Translator(BaseEntity):
    def __init__(self, code: str, name: str):
        super().__init__(code, name)


class Language(BaseEntity):
    def __init__(self, code: str, name: str):
        super().__init__(code, name)
