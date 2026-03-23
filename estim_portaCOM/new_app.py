import time
import base64
from pathlib import Path

import streamlit as st
import serial
from serial.tools import list_ports


VIDEO_PATH = r"video\Protocolo_10_repeticoes_final.mp4"
BAUDRATE = 115200
TRIGGER_CODE = 115
TRIGGER_DURATION_S = 0.008

#deixar explicito que a variável é binária ou caractere de 1 byte (int8)

def get_available_ports():
    return list(list_ports.comports())


def send_biosemi_trigger(
    com_port: str,
    trigger_code: int,
    baudrate: int = 115200,
    duration_s: float = 0.008,
) -> tuple[bool, str]:
    try:
        if not com_port:
            return False, "Nenhuma porta COM foi selecionada."

        if not 0 <= trigger_code <= 255:
            return False, "O TRIGGER_CODE deve estar entre 0 e 255."

        with serial.Serial(
            port=com_port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0,
            write_timeout=1,
        ) as ser:
            time.sleep(0.1)
            ser.write(bytes([trigger_code]))
            ser.flush()
            time.sleep(duration_s)

        return True, f"Trigger {trigger_code} enviado com sucesso pela porta {com_port}."

    except Exception as e:
        return False, f"Erro ao enviar trigger: {e}"


def load_video_bytes(video_path: str) -> bytes:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {path.resolve()}")
    return path.read_bytes()


if "play_requested" not in st.session_state:
    st.session_state.play_requested = False

if "last_status" not in st.session_state:
    st.session_state.last_status = ""

if "last_trigger_time" not in st.session_state:
    st.session_state.last_trigger_time = None


st.set_page_config(page_title="Reprodução de Vídeo com Trigger BioSemi", layout="centered")
st.title("Reprodução de Vídeo com Trigger BioSemi")

ports = get_available_ports()
port_options = [p.device for p in ports]

selected_port = st.selectbox(
    "Selecione a porta COM do BioSemi",
    options=port_options,
    index=0 if port_options else None,
    placeholder="Nenhuma porta detectada"
)

if ports:
    with st.expander("Portas detectadas"):
        for p in ports:
            st.write(f"{p.device} | {p.description} | {p.hwid}")

st.write(f"**Vídeo:** `{VIDEO_PATH}`")
st.write(f"**Baudrate:** `{BAUDRATE}`")
st.write(f"**Trigger:** `{TRIGGER_CODE}`")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Play", use_container_width=True):
        ok, msg = send_biosemi_trigger(
            com_port=selected_port,
            trigger_code=TRIGGER_CODE,
            baudrate=BAUDRATE,
            duration_s=TRIGGER_DURATION_S,
        )
        st.session_state.last_status = msg
        st.session_state.last_trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.play_requested = ok

with col2:
    if st.button("Testar trigger", use_container_width=True):
        ok, msg = send_biosemi_trigger(
            com_port=selected_port,
            trigger_code=TRIGGER_CODE,
            baudrate=BAUDRATE,
            duration_s=TRIGGER_DURATION_S,
        )
        st.session_state.last_status = msg
        st.session_state.last_trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")

with col3:
    if st.button("Resetar", use_container_width=True):
        st.session_state.play_requested = False
        st.session_state.last_status = ""
        st.session_state.last_trigger_time = None

if st.session_state.last_status:
    if "sucesso" in st.session_state.last_status.lower():
        st.success(st.session_state.last_status)
    else:
        st.error(st.session_state.last_status)

if st.session_state.last_trigger_time:
    st.info(f"Último trigger enviado em: {st.session_state.last_trigger_time}")

st.markdown("### Vídeo")

try:
    video_bytes = load_video_bytes(VIDEO_PATH)
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    if st.session_state.play_requested:
        st.components.v1.html(
            f"""
            <div style="display:flex; justify-content:center;">
                <video width="900" controls autoplay>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Seu navegador não suporta vídeo HTML5.
                </video>
            </div>
            """,
            height=550,
        )
    else:
        st.video(video_bytes)

except Exception as e:
    st.error(f"Erro ao carregar/exibir vídeo: {e}")