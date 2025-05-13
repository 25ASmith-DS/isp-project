class Debug:
    def __init__(self, obj: dict):
        self.messages: list[str] = [str(s) for s in obj['messages']]
        self.renderables = [eval(s) for s in obj['renderables']]


class Line:
    def __init__(self, p1, p2, width, color):
        self.p1 = p1
        self.p2 = p2
        self.width = width
        self.color = color


class Circle:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color
