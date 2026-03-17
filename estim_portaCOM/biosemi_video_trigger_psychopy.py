from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Optional

import serial
from psychopy import core, event, visual, logging


# =========================================================
# CONFIGURAÇÕES
# =========================================================
VIDEO_PATH = r"video\Protocolo_10_repeticoes_final.mp4"
COM_PORT = "COM3"
BAUDRATE = 115200
TRIGGER_CODE = 1                  # 0-255
FULLSCREEN = True
SCREEN_INDEX = 1
WINDOW_SIZE = (1280, 720)         # usado se FULLSCREEN=False
BACKGROUND_COLOR = (-1, -1, -1)   # preto em escala PsychoPy
LOG_CSV = "video_trigger_log.csv"

# Fotodiodo: quadrado em um canto da tela
PHOTODIODE_ENABLED = True
PHOTODIODE_SIZE_PX = 80
PHOTODIODE_POS = (900, -480)      # ajuste conforme sua tela / canto desejado
PHOTODIODE_OFF_COLOR = (-1, -1, -1)  # preto
PHOTODIODE_ON_COLOR = (1, 1, 1)      # branco

# Controles
START_KEYS = ["space", "return"]
QUIT_KEYS = ["escape", "q"]


# =========================================================
# UTILIDADES SERIAL / TRIGGER
# =========================================================
def open_serial(port: str, baudrate: int = 115200) -> serial.Serial:
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


def send_trigger_byte(ser: serial.Serial, code: int) -> None:
    if not 0 <= code <= 255:
        raise ValueError("TRIGGER_CODE deve estar entre 0 e 255.")
    ser.write(bytes([code]))
    ser.flush()


# =========================================================
# LOG
# =========================================================
def init_log_file(log_path: str) -> None:
    path = Path(log_path)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date_time",
                "video_path",
                "com_port",
                "trigger_code",
                "button_press_time_monotonic",
                "first_flip_time_monotonic",
                "trigger_send_time_monotonic",
                "movie_start_time_clock",
                "movie_end_time_clock",
                "duration_s",
                "aborted",
                "notes",
            ])


def append_log_row(
    log_path: str,
    video_path: str,
    com_port: str,
    trigger_code: int,
    button_press_time: Optional[float],
    first_flip_time: Optional[float],
    trigger_send_time: Optional[float],
    movie_start_time_clock: Optional[float],
    movie_end_time_clock: Optional[float],
    aborted: bool,
    notes: str = "",
) -> None:
    duration_s = None
    if (
        movie_start_time_clock is not None
        and movie_end_time_clock is not None
    ):
        duration_s = movie_end_time_clock - movie_start_time_clock

    with Path(log_path).open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            video_path,
            com_port,
            trigger_code,
            button_press_time,
            first_flip_time,
            trigger_send_time,
            movie_start_time_clock,
            movie_end_time_clock,
            duration_s,
            aborted,
            notes,
        ])


# =========================================================
# EXPERIMENTO
# =========================================================
def main() -> None:
    video_file = Path(VIDEO_PATH)
    if not video_file.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {video_file}")

    init_log_file(LOG_CSV)

    logging.console.setLevel(logging.INFO)

    ser = None
    win = None
    aborted = False

    button_press_time = None
    first_flip_time = None
    trigger_send_time = None
    movie_start_time_clock = None
    movie_end_time_clock = None

    experiment_clock = core.Clock()

    try:
        # -------------------------------------------------
        # 1) Porta serial
        # -------------------------------------------------
        ser = open_serial(COM_PORT, BAUDRATE)
        print(f"[INFO] Porta serial aberta: {COM_PORT}")

        # -------------------------------------------------
        # 2) Janela
        # -------------------------------------------------
        win = visual.Window(
            size=WINDOW_SIZE,
            fullscr=FULLSCREEN,
            screen=SCREEN_INDEX,
            color=BACKGROUND_COLOR,
            units="pix",
            allowGUI=False,
        )
        win.mouseVisible = True

        # -------------------------------------------------
        # 3) Elementos de interface
        # -------------------------------------------------
        title = visual.TextStim(
            win,
            text="Reprodução de Vídeo com Trigger BioSemi",
            pos=(0, 200),
            height=38,
            color="white",
            bold=True,
        )

        instructions = visual.TextStim(
            win,
            text=(
                "Clique no botão PLAY ou pressione ESPAÇO/ENTER para iniciar.\n"
                "ESC ou Q para sair."
            ),
            pos=(0, 120),
            height=26,
            color="white",
        )

        play_button = visual.Rect(
            win,
            width=260,
            height=90,
            pos=(0, -20),
            fillColor=(0.1, 0.4, 0.1),
            lineColor="white",
            lineWidth=2,
        )

        play_label = visual.TextStim(
            win,
            text="PLAY",
            pos=(0, -20),
            height=34,
            color="white",
            bold=True,
        )

        footer = visual.TextStim(
            win,
            text=f"Vídeo: {video_file.name} | COM: {COM_PORT} | Trigger: {TRIGGER_CODE}",
            pos=(0, -240),
            height=18,
            color="white",
        )

        mouse = event.Mouse(win=win)

        # -------------------------------------------------
        # 4) Fotodiodo
        # -------------------------------------------------
        photodiode = visual.Rect(
            win,
            width=PHOTODIODE_SIZE_PX,
            height=PHOTODIODE_SIZE_PX,
            pos=PHOTODIODE_POS,
            fillColor=PHOTODIODE_OFF_COLOR,
            lineColor=PHOTODIODE_OFF_COLOR,
        )

        # -------------------------------------------------
        # 5) Tela inicial
        # -------------------------------------------------
        started = False
        while not started:
            title.draw()
            instructions.draw()
            play_button.draw()
            play_label.draw()
            footer.draw()

            if PHOTODIODE_ENABLED:
                photodiode.fillColor = PHOTODIODE_OFF_COLOR
                photodiode.lineColor = PHOTODIODE_OFF_COLOR
                photodiode.draw()

            win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                return

            if any(k in START_KEYS for k in keys):
                button_press_time = time.perf_counter()
                started = True
                break

            if mouse.isPressedIn(play_button):
                button_press_time = time.perf_counter()
                started = True
                core.wait(0.15)  # debounce simples
                break

        # -------------------------------------------------
        # 6) Carrega vídeo
        # -------------------------------------------------
        movie = visual.MovieStim3(
            win=win,
            filename=str(video_file),
            noAudio=False,
            loop=False,
        )

        # Tela preta curta antes do vídeo
        if PHOTODIODE_ENABLED:
            photodiode.fillColor = PHOTODIODE_OFF_COLOR
            photodiode.lineColor = PHOTODIODE_OFF_COLOR
            photodiode.draw()
        win.flip()
        core.wait(0.2)

        # -------------------------------------------------
        # 7) Primeiro frame: trigger no callOnFlip()
        # -------------------------------------------------
        first_frame_presented = False
        trigger_scheduled = False
        movie_start_time_clock = experiment_clock.getTime()

        def trigger_callback():
            nonlocal trigger_send_time
            send_trigger_byte(ser, TRIGGER_CODE)
            trigger_send_time = time.perf_counter()

        while movie.status != visual.FINISHED:
            movie.draw()

            # No mesmo primeiro flip:
            # - o fotodiodo passa para branco
            # - o trigger é enviado pela COM
            if not first_frame_presented:
                if PHOTODIODE_ENABLED:
                    photodiode.fillColor = PHOTODIODE_ON_COLOR
                    photodiode.lineColor = PHOTODIODE_ON_COLOR
                    photodiode.draw()

                if not trigger_scheduled:
                    win.callOnFlip(trigger_callback)
                    trigger_scheduled = True

                first_flip_time = win.flip()
                first_frame_presented = True
                print(f"[INFO] Primeiro frame apresentado em {first_flip_time:.6f}")
                continue

            # Frames seguintes: fotodiodo volta para preto
            if PHOTODIODE_ENABLED:
                photodiode.fillColor = PHOTODIODE_OFF_COLOR
                photodiode.lineColor = PHOTODIODE_OFF_COLOR
                photodiode.draw()

            win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                aborted = True
                break

        movie_end_time_clock = experiment_clock.getTime()

        # Tela final
        end_text = visual.TextStim(
            win,
            text="Fim da reprodução.\nPressione ESC para sair.",
            height=28,
            color="white",
        )
        while True:
            end_text.draw()
            if PHOTODIODE_ENABLED:
                photodiode.fillColor = PHOTODIODE_OFF_COLOR
                photodiode.lineColor = PHOTODIODE_OFF_COLOR
                photodiode.draw()
            win.flip()

            keys = event.getKeys()
            if any(k in QUIT_KEYS for k in keys):
                break

    finally:
        append_log_row(
            log_path=LOG_CSV,
            video_path=str(video_file) if "video_file" in locals() else VIDEO_PATH,
            com_port=COM_PORT,
            trigger_code=TRIGGER_CODE,
            button_press_time=button_press_time,
            first_flip_time=first_flip_time,
            trigger_send_time=trigger_send_time,
            movie_start_time_clock=movie_start_time_clock,
            movie_end_time_clock=movie_end_time_clock,
            aborted=aborted,
            notes="",
        )

        if ser is not None and ser.is_open:
            ser.close()
            print("[INFO] Porta serial fechada.")

        if win is not None:
            win.close()

        core.quit()


if __name__ == "__main__":
    main()