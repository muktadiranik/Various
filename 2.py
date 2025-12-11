from abc import ABC, abstractmethod


class InvalidOperationError(Exception):
    pass


class Stream(ABC):
    def __init__(self):
        self.__stream = False
        super().__init__()

    def open(self):
        if self.__stream:
            raise InvalidOperationError("Stream is already open")
        self.__stream = True
        print("Stream opened")

    def close(self):
        if not self.__stream:
            raise InvalidOperationError("Stream is already closed")
        self.__stream = False
        print("Stream closed")

    @abstractmethod
    def read(self):
        pass


class FileStream(Stream):
    def __init__(self):
        super().__init__()

    def read(self):
        print("Reading data from file stream")


class NetworkStream(Stream):
    def __init__(self):
        super().__init__()

    def read(self):
        print("Reading data from network stream")
