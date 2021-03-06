import glfw
import pyrr
from OpenGL.GL import *

from core import Audio, GUI, DisplayManager, RenderEngine
from core.Camera import Camera
from entities import Entities
from islands import IslandGenerator

window = DisplayManager.Window()

cam = Camera(window)

masterRenderer = RenderEngine.MasterRenderer()

entities = []
ellipsoid = Entities.Ellipsoid()
entities.append(ellipsoid)

tree = Entities.Tree()
entities.append(tree)
tree.position = pyrr.Vector3([0, 0, -10])

island = IslandGenerator.generateMeshForIsland(0, 0)
print(island)

# LIGHTING
lights = []
light1 = RenderEngine.Light(pyrr.Vector3([0, 5, -5]), [1, 1, 1], [0.5, 0.5, 0.5])
lights.append(light1)

# GUI
font = GUI.FontType("res/font/arial")
myGUI = GUI.GUI()
div1 = GUI.GUIDivision((0, 0, 1, 1))
div1.display = True
text = font.constructGuiText("Hello World!", 1, (0, 0), 0.15, [1, 0, 0])
div1.addComponent(text)
button = GUI.GUIButton((0, 0, 0.1, 0.05), (0, 0.7, 0.8), window)
div1.addComponent(button)
# div2 = GUI.GUIDivision(0, 0, 1, 1)
# text2 = GUI.GUIText(0, 0, 0, 0, 1, (1, 1, 1))
# div2.addComponent(text1)
myGUI.addComponent(div1)
myGUI.setup()

# AUDIO
audioContext = Audio.createContext()
Audio.setListenerData(0, 0, 0)
buffer = Audio.loadSound("res/sounds/bounce.wav")
source = Audio.Source()

glClearColor(0.0, 0.0, 0.0, 1.0)
while not window.shouldClose():
    window.startFrame()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cam.handleKeyboardInput()

    masterRenderer.renderScene(cam, entities, [island], lights)
    masterRenderer.renderGUI(myGUI)

    if window.getKeyState(glfw.KEY_M) == glfw.PRESS:
        if not source.isPlaying():
            source.play(buffer)

    if window.getKeyState(glfw.KEY_P) == glfw.PRESS:
        print(cam.position)

    if window.getKeyState(glfw.KEY_ESCAPE) == glfw.PRESS:
        window.setCursorLock(False)

    myGUI.update()
    window.updateDisplay()

# renderEngine.cleanUp() TODO: reminder to fix this
source.delete()
Audio.cleanUp(audioContext)
glfw.terminate()
exit(0)
