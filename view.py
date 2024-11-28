from controller import MainController
from abc import ABC, abstractmethod

class InterfaceObject(ABC):
    @abstractmethod
    def setParams(self, len: float, height: float) -> None:
        pass

    @abstractmethod
    def process(self) -> None:
        pass

class Field(InterfaceObject):
    @abstractmethod
    def assignType(self, type) -> None:
        pass

class Table(InterfaceObject):
    @abstractmethod
    def initBase(self, rows: int, columns: int) -> None:
        pass

class Layer(InterfaceObject):
    @abstractmethod
    def assignType(self, type) -> None:
        pass

    @abstractmethod
    def add(self, obj: InterfaceObject, x: float, y: float) -> None:
        pass

class Button(InterfaceObject):
    @abstractmethod
    def assignAction(self, action) -> None:
        pass

class Window(InterfaceObject):
    @abstractmethod
    def addLayer(self, layer: Layer) -> None:
        pass

class InterfaceFabric(ABC):
    @abstractmethod
    def createWindow(self):
        pass

    @abstractmethod
    def createButton(self):
        pass

    @abstractmethod
    def createField(self):
        pass

    @abstractmethod
    def createTable(self):
        pass

    @abstractmethod
    def createLayer(self):
        pass

class DefaultInterface(InterfaceFabric):
    def createWindow(self) -> Window:
        return Window()

    def createButton(self) -> Button:
        return Button()

    def createField(self) -> Field:
        return Field()

    def createTable(self) -> Table:
        return Table()

    def createLayer(self) -> Layer:
        return Layer()

class Platform(ABC):
    def __init__(self):
        self.fabric: InterfaceFabric = DefaultInterface()
        self.windows: dict[str, Window] = {}

    def createInterface(self) -> None:
        pass

    def processInterface(self) -> None:
        pass

    def showWindow(self, name: str) -> None:
        if name in self.windows:
            print(f"show window {name}")
        else:
            print("Nothing to show!")

    def getWindows(self) -> dict[str, Window]:
        return self.windows

class RunPlatform(ABC):
    def __init__(self):
        self.controller = MainController()
        self.default_interface = DefaultInterface()
        self.platform = Platform()

    def runPlatform(self) -> None:
        print("Initializing platform...")
        self.platform.createInterface()
        self.platform.processInterface()
        print("Platform is running!")

