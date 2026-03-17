from __future__ import annotations

import time
from pathlib import Path

import serial
from psychopy import visual, event, core
from psychopy.visual.movies import MovieStim


# =========================
# CONFIGURAÇÃO
# =========================
VIDEO_PATH = r"video\Protocolo_10_repeticoes_final.mp4"
COM_PORT = "COM3"
BAUDRATE = 115200
TRIGGER_CODE = 1

WINDOW_SIZE = (1200, 800)
FULLSCREEN = False
SCREEN_INDEX = 1

PHOTODIODE_SIZE = 80
QUIT_KEYS = ["escape", "q"]


# =========================
# SERIAL
# =========================
def open_serial(port: str, baudrate: int = 115200):
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0,
        write_timeout=1,
    )
    time.sleep(0.1)
    return ser


def send_trigger(ser, code: int):
    if not 0 <= code <= 255:
        raise ValueError("TRIGGER_CODE deve estar entre 0 e 255.")
    ser.write(bytes([code]))
    ser.flush()


# =========================
# MAIN
# =========================
def main():
    video_file = Path(VIDEO_PATH)
    if not video_file.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {video_file}")

    ser = None
    win = None

    try:
        # abre COM
        ser = open_serial(COM_PORT, BAUDRATE)

        # abre janela
        win = visual.Window(
            size=WINDOW_SIZE,
            fullscr=FULLSCREEN,
            screen=SCREEN_INDEX,
            color=(-1, -1, -1),
            units="pix",
            allowGUI=True
        )
        win.mouseVisible = True

        mouse = event.Mouse(win=win)

        # UI inicial
        titulo = visual.TextStim(
            win,
            text="Player de Vídeo com Trigger BioSemi",
            pos=(0, 220),
            color="white",
            height=34,
            bold=True
        )

        subtitulo = visual.TextStim(
            win,
            text="Clique em PLAY para iniciar",
            pos=(0, 160),
            color="white",
            height=24
        )

        play_button = visual.Rect(
            win,
            width=260,
            height=100,
            pos=(0, 20),
            fillColor=(0.0, 0.45, 0.15),
            lineColor="white",
            lineWidth=2
        )

        play_label = visual.TextStim(
            win,
            text="PLAY",
            pos=(0, 20),
            color="white",
            height=32,
            bold=True
        )

        rodape = visual.TextStim(
            win,
            text=f"Vídeo: {video_file.name} | Porta: {COM_PORT} | Trigger: {TRIGGER_CODE}",
            pos=(0, -260),
            color="white",
            height=18
        )

        # marcador do fotodiodo no canto superior direito
        diode_x = WINDOW_SIZE[0] / 2 - PHOTODIODE_SIZE / 2 - 20
        diode_y = WINDOW_SIZE[1] / 2 - PHOTODIODE_SIZE / 2 - 20

        photodiode = visual.Rect(
            win,
            width=PHOTODIODE_SIZE,
            height=PHOTODIODE_SIZE,
            pos=(diode_x, diode_y),
            fillColor=(-1, -1, -1),
            lineColor=(-1, -1, -1)
        )

        # tela inicial
        started = False
        while not started:
            titulo.draw()
            subtitulo.draw()
            play_button.draw()
            play_label.draw()
            rodape.draw()
            photodiode.fillColor = (-1, -1, -1)
            photodiode.lineColor = (-1, -1, -1)
            photodiode.draw()
            win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                return

            if mouse.isPressedIn(play_button):
                started = True
                core.wait(0.2)

        # carrega vídeo
        movie = MovieStim(
            win=win,
            filename=str(video_file),
            size=win.size,
            pos=(0, 0),
            loop=False,
            noAudio=False
        )

        first_flip_done = False
        trigger_sent = False

        def trigger_callback():
            send_trigger(ser, TRIGGER_CODE)

        # loop do vídeo
        while not movie.isFinished:
            movie.draw()

            if not first_flip_done:
                photodiode.fillColor = (1, 1, 1)
                photodiode.lineColor = (1, 1, 1)
                photodiode.draw()

                if not trigger_sent:
                    win.callOnFlip(trigger_callback)
                    trigger_sent = True

                win.flip()
                first_flip_done = True
            else:
                photodiode.fillColor = (-1, -1, -1)
                photodiode.lineColor = (-1, -1, -1)
                photodiode.draw()
                win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                break

        # tela final
        fim = visual.TextStim(
            win,
            text="Fim da reprodução.\n\nPressione ESC para sair.",
            color="white",
            height=28
        )

        while True:
            fim.draw()
            photodiode.fillColor = (-1, -1, -1)
            photodiode.lineColor = (-1, -1, -1)
            photodiode.draw()
            win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                break

    finally:
        if ser is not None and ser.is_open:
            ser.close()

        if win is not None:
            win.close()

        core.quit()


if __name__ == "__main__":
    main()