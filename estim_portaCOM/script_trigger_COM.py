from psychopy import visual, core, event
import serial
import time
from pathlib import Path

# =========================================================
# CONFIGURAÇÕES
# =========================================================
VIDEO_PATH = r"video\Protocolo_10_repeticoes_final.mp4"   # ajuste aqui
COM_PORT = "COM3"                               # ajuste aqui
BAUDRATE = 115200
TRIGGER_CODE = 1                                # 0-255
TRIGGER_DURATION_S = 0.008                      # 8 ms (BioSemi faz auto-reset, mas mantemos explícito)
FULLSCREEN = False
SCREEN_INDEX = 1                                # 0 = monitor principal

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def open_serial(port: str, baudrate: int = 115200) -> serial.Serial:
    """
    Abre a porta serial para envio de triggers ao BioSemi USB Trigger Interface.
    """
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0,
        write_timeout=0
    )
    time.sleep(0.1)  # pequena estabilização
    return ser


def send_trigger(ser: serial.Serial, code: int, duration_s: float = 0.008):
    """
    Envia 1 byte pela COM.
    """
    if not 0 <= code <= 255:
        raise ValueError("TRIGGER_CODE deve estar entre 0 e 255.")

    ser.write(bytes([code]))
    ser.flush()

    # Opcional:
    # O USB Trigger Interface da BioSemi já mantém o trigger por ~8 ms e depois zera.
    # Mesmo assim, deixamos um pequeno intervalo por segurança lógica.
    core.wait(duration_s)


# =========================================================
# SCRIPT PRINCIPAL
# =========================================================
def main():
    video_file = Path(VIDEO_PATH)
    if not video_file.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {video_file}")

    ser = None
    win = None

    try:
        # 1) Abre COM
        ser = open_serial(COM_PORT, BAUDRATE)
        print(f"[INFO] Porta serial aberta em {COM_PORT}")

        # 2) Cria janela
        win = visual.Window(
            size=[1280, 720],
            fullscr=FULLSCREEN,
            screen=SCREEN_INDEX,
            color=[0, 0, 0],
            units="pix"
        )

        # 3) Carrega vídeo
        movie = visual.MovieStim3(
            win=win,
            filename=str(video_file),
            noAudio=False,
            loop=False
        )

        # Mensagem inicial opcional
        msg = visual.TextStim(
            win,
            text="Pressione ESPAÇO para iniciar o vídeo\nESC para sair",
            color="white",
            height=28
        )
        msg.draw()
        win.flip()

        keys = event.waitKeys(keyList=["space", "escape"])
        if "escape" in keys:
            return

        # Pequena pausa antes de iniciar
        core.wait(0.5)

        # 4) Início da reprodução
        trigger_sent = False
        clock = core.Clock()
        clock.reset()

        while movie.status != visual.FINISHED:
            movie.draw()

            # flip() apresenta o frame na tela
            flip_time = win.flip()

            # envia o trigger no primeiro frame realmente exibido
            if not trigger_sent:
                send_trigger(ser, TRIGGER_CODE, TRIGGER_DURATION_S)
                trigger_sent = True
                print(f"[INFO] Trigger {TRIGGER_CODE} enviado em t={clock.getTime():.6f}s | flip={flip_time:.6f}")

            # permite abortar com ESC
            if "escape" in event.getKeys(["escape"]):
                break

        # Tela preta no final
        win.flip()
        core.wait(0.2)

    finally:
        if ser is not None and ser.is_open:
            ser.close()
            print("[INFO] Porta serial fechada.")

        if win is not None:
            win.close()

        core.quit()


if __name__ == "__main__":
    main()