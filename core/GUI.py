import glfw
import numpy as np

import Reference
from core.Loader import TextureAtlas, RawModel


class GUI:
    def __init__(self):
        self.components = []

    def addComponent(self, c):
        self.components.append(c)

    def getComponents(self):
        return [b.getComponent() for b in self.components]

    def update(self):
        for component in self.components:
            component.update()

    def setup(self):
        for c in self.components:
            c.setTrueCoords(1, 1)

class GUIComponent:
    model = None

    def __init__(self, x, y, width, height):
        # defined as percentages from 0.0 - 1.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.trueX = None
        self.trueY = None
        self.trueWidth = None
        self.trueHeight = None

    def setTrueCoords(self, multiplierX, multiplierY):
        self.trueX = self.x * multiplierX
        self.trueY = self.y * multiplierY
        self.trueWidth = self.width * multiplierX
        self.trueHeight = self.height * multiplierY


    def update(self):
        pass

    # needed for recursion
    def getComponent(self):
        return self

    def genModel(self):
        self.model = [
            self.trueX, self.trueY,
            self.trueX + self.trueWidth, self.trueY,
            self.trueX + self.trueWidth, self.trueY + self.trueHeight,
            self.trueX, self.trueY + self.trueHeight
        ]
        self.model = np.array(self.model, dtype=np.float32)


class GUIDivision(GUIComponent):
    indices = np.array([0, 1, 3, 1, 2, 3], dtype=np.uint8)

    display = False

    def __init__(self, rect):
        super().__init__(*rect)

        self.components = []

    def addComponent(self, c):

        self.components.append(c)

    def setDisplayed(self, display, colour):
        self.display = True
        self.genModel()
        self.colour = colour

    def getComponent(self):
        a = []
        if self.display:
            a.append(self)
        a.extend([b.getComponent() for b in self.components])
        return a

    def setTrueCoords(self, multiplierX, multiplierY):
        self.trueX = self.x * multiplierX
        self.trueY = self.y * multiplierY
        self.trueWidth = self.width * multiplierX
        self.trueHeight = self.height * multiplierY

        for c in self.components:
            c.setTrueCoords(self.trueWidth, self.trueHeight)

    def update(self):
        for component in self.components:
            component.update()


class GUIText(GUIComponent):
    def __init__(self, font, model, rect, scale, colour):
        super().__init__(*rect)

        self.model = model
        self.scale = scale
        self.font = font
        self.colour = colour

    def getWidth(self):
        return self.width * self.scale

    def getHeight(self):
        return self.height * self.scale


class GUIButton(GUIComponent):
    def __init__(self, rect, baseColour, window):
        super().__init__(*rect)
        self.baseColour = baseColour
        self.colour = baseColour
        self.window = window
        self.hovered = False
        self.click = False

    def update(self):
        mousePos = self.window.getCursorPos()
        leftClick = self.window.getMouseState(glfw.MOUSE_BUTTON_LEFT)
        if 0 <= mousePos[0] <= Reference.WINDOW_WIDTH and 0 <= mousePos[1] <= Reference.WINDOW_HEIGHT:
            normX = mousePos[0] / (0.5 * Reference.WINDOW_WIDTH) - 1
            normY = -(mousePos[1] / (0.5 * Reference.WINDOW_HEIGHT) - 1)
            maxX = self.trueX + self.trueWidth
            maxY = self.trueY + self.trueHeight
            self.hovered = self.trueX <= normX <= maxX and self.trueY <= normY <= maxY
            self.click = self.hovered and leftClick == glfw.PRESS





# Holds information about a font
class FontType:
    separator = " "

    charTable = {}

    rectIndices = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uint8)

    def __init__(self, filepath):
        self.filepath = filepath
        aspectRatio = Reference.WINDOW_WIDTH / Reference.WINDOW_HEIGHT
        self.fontSheetTexture = TextureAtlas(filepath + ".png", 1, flipped=False)

        with open(filepath + ".fnt", "r") as file:
            for line in file:
                fragments = line.split(self.separator)
                if fragments[0] == "char":
                    character = Character(fragments)
                    character.normalise(self.fontSheetTexture.width, self.fontSheetTexture.height, aspectRatio)
                    self.charTable[character.ID] = character

    def constructGuiText(self, text, scale, pos, lineSpacing, colour):
        vertices = []
        textureCoords = []
        indices = np.array([], dtype=np.uint8)  # may be too small
        iboCounter = 0
        lines = text.split("\n")
        for lineNo, line in enumerate(lines):
            cursor = 0
            lineOffset = lineNo * lineSpacing
            for charNo, char in enumerate(line):
                charInfo = self.charTable[ord(char)]
                charVertexData = [
                    cursor + charInfo.normXoffset, -charInfo.normYoffset - lineOffset,
                    cursor + charInfo.normXoffset + charInfo.normWidth2, -charInfo.normYoffset - lineOffset,
                    cursor + charInfo.normXoffset + charInfo.normWidth2,
                    -charInfo.normYoffset - charInfo.normHeight - lineOffset,
                    cursor + charInfo.normXoffset, -charInfo.normYoffset - charInfo.normHeight - lineOffset,
                ]
                vertices.extend(charVertexData)
                charTexCoords = [
                    charInfo.normX, charInfo.normY,
                    charInfo.normX + charInfo.normWidth, charInfo.normY,
                    charInfo.normX + charInfo.normWidth, charInfo.normY + charInfo.normHeight,
                    charInfo.normX, charInfo.normY + charInfo.normHeight,
                ]
                textureCoords.extend(charTexCoords)
                cursor += charInfo.normXadvance
                newIndices = self.rectIndices + 4 * iboCounter
                indices = np.append(indices, newIndices)
                iboCounter += 1

        vertices = np.array(vertices, dtype=np.float32)
        textureCoords = np.array(textureCoords, dtype=np.float32)

        width = vertices[0::2].max()
        height = vertices[1::2].min()

        model = RawModel.loadPTI(vertices, textureCoords, indices)

        return GUIText(self, model, (*pos, width, height), scale, colour)


class Character:
    ID = 0
    x = 0
    y = 0
    width = 0
    height = 0
    xoffset = 0
    yoffset = 0
    xadvance = 0

    def __init__(self, lineFragments):
        for fragment in lineFragments:
            if fragment.startswith("id"):
                self.ID = int(fragment.split("=")[1])
            elif fragment.startswith("xoffset"):
                self.xoffset = int(fragment.split("=")[1])
            elif fragment.startswith("yoffset"):
                self.yoffset = int(fragment.split("=")[1])
            elif fragment.startswith("xadvance"):
                self.xadvance = int(fragment.split("=")[1])
            elif fragment.startswith("width"):
                self.width = int(fragment.split("=")[1])
            elif fragment.startswith("height"):
                self.height = int(fragment.split("=")[1])
            elif fragment.startswith("x"):
                self.x = int(fragment.split("=")[1])
            elif fragment.startswith("y"):
                self.y = int(fragment.split("=")[1])

    def normalise(self, imgWidth, imgHeight, aspectRatio):
        self.normX = self.x / imgWidth
        self.normY = self.y / imgHeight
        self.normWidth = self.width / imgWidth
        self.normHeight = self.height / imgHeight  # for tex coords
        self.normWidth2 = (self.width / imgWidth) / aspectRatio
        self.normXoffset = (self.xoffset / imgWidth) / aspectRatio
        self.normYoffset = self.yoffset / imgWidth
        self.normXadvance = (self.xadvance / imgWidth) / aspectRatio
