from psychopy import visual, event, core

win = visual.Window(
    size=(1000, 700),
    fullscr=False,
    screen=0,
    color=(-1, -1, -1),
    units="pix",
    allowGUI=True
)

texto = visual.TextStim(
    win,
    text="Janela do PsychoPy aberta com sucesso.\n\nPressione ESC para sair.",
    color="white",
    height=28
)

while True:
    texto.draw()
    win.flip()

    keys = event.getKeys()
    if "escape" in keys:
        break

win.close()
core.quit()