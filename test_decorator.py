

def laugh(original_class):
    original_init = original_class.__init__
    def laugh(self):
        print("Hahaha!")
    def __init__(self, quality, buttfart):
        self.quality = quality
        self.buttfart = buttfart

    original_class.laugh = laugh
    original_class.__init__ = __init__
    return original_class

@laugh
class Potato:
    def __init__(self, potato) -> None:
        self.potato = potato
    
    def boil(self):
        print(f"Boiling potato {self.potato}")


fatty = Potato("Rubadub")
fatty.laugh()