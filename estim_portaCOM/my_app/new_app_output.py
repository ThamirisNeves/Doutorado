import base64
import time
import sys
from pathlib import Path

import serial
from serial.tools import list_ports
import streamlit as st


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


VIDEO_PATH = resource_path("video/Protocolo_10_repeticoes_final.mp4")
BAUDRATE = 115200
TRIGGER_CODE = 0x01
TRIGGER_DURATION_S = 0.008


def load_video_bytes(video_path) -> bytes:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {path.resolve()}")
    return path.read_bytes()


def get_available_ports():
    return list(list_ports.comports())


def open_serial_port(com_port: str, baudrate: int = 115200):
    return serial.Serial(
        port=com_port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        write_timeout=1,
    )


def close_serial_port():
    ser = st.session_state.get("serial_conn")
    if ser is not None:
        try:
            if ser.is_open:
                ser.close()
        except Exception:
            pass
    st.session_state.serial_conn = None
    st.session_state.connected = False


def send_serial_bytes(payload: bytes):
    ser = st.session_state.get("serial_conn")
    if ser is None or not ser.is_open:
        return False, "Porta serial não está conectada."

    try:
        ser.write(payload)
        ser.flush()
        return True, f"Enviado: {payload.hex()} (hex)"
    except Exception as e:
        return False, f"Erro ao enviar dados: {e}"


def send_biosemi_trigger(trigger_code: int):
    if not 0 <= trigger_code <= 255:
        return False, "O TRIGGER_CODE deve estar entre 0 e 255."

    ok, msg = send_serial_bytes(bytes([trigger_code]))
    if ok:
        time.sleep(TRIGGER_DURATION_S)
        return True, f"Trigger 0x{trigger_code:02X} enviado com sucesso."
    return ok, msg


def send_stop_signal():
    return send_serial_bytes(b"f")


def read_serial_available() -> str:
    ser = st.session_state.get("serial_conn")
    if ser is None or not ser.is_open:
        return ""

    try:
        waiting = ser.in_waiting
        if waiting and waiting > 0:
            data = ser.read(waiting)
            return data.decode("utf-8", errors="replace")
        return ""
    except Exception as e:
        return f"\n[ERRO DE LEITURA] {e}\n"


if "play_requested" not in st.session_state:
    st.session_state.play_requested = False

if "last_status" not in st.session_state:
    st.session_state.last_status = ""

if "last_trigger_time" not in st.session_state:
    st.session_state.last_trigger_time = None

if "serial_conn" not in st.session_state:
    st.session_state.serial_conn = None

if "connected" not in st.session_state:
    st.session_state.connected = False

if "serial_log" not in st.session_state:
    st.session_state.serial_log = ""


st.set_page_config(page_title="Reprodução de Vídeo com Trigger BioSemi", layout="centered")

st.title("Reprodução de Vídeo com Trigger BioSemi")

ports = get_available_ports()
port_options = [p.device for p in ports]

selected_port = st.selectbox(
    "Selecione a porta COM",
    options=port_options,
    index=0 if port_options else None,
    placeholder="Nenhuma porta detectada",
)

st.markdown("### Configuração atual")
st.write(f"**Vídeo:** `{VIDEO_PATH}`")
st.write(f"**Baudrate:** `{BAUDRATE}`")
st.write(f"**Trigger:** `0x{TRIGGER_CODE:02X}`")
st.write(f"**Conectado:** `{'Sim' if st.session_state.connected else 'Não'}`")

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    if st.button("Conectar", use_container_width=True):
        try:
            if not selected_port:
                st.session_state.last_status = "Selecione uma porta COM."
            else:
                close_serial_port()
                st.session_state.serial_conn = open_serial_port(selected_port, BAUDRATE)
                st.session_state.connected = True
                st.session_state.last_status = f"Conectado à porta {selected_port}."
        except Exception as e:
            st.session_state.connected = False
            st.session_state.serial_conn = None
            st.session_state.last_status = f"Erro ao conectar: {e}"

with col_b:
    if st.button("Play", use_container_width=True):
        ok, msg = send_biosemi_trigger(TRIGGER_CODE)
        st.session_state.last_status = msg
        st.session_state.last_trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.play_requested = ok

with col_c:
    if st.button("Parar (f)", use_container_width=True):
        ok, msg = send_stop_signal()
        st.session_state.last_status = f"{msg} | comando de parada enviado."
        st.session_state.last_trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")

with col_d:
    if st.button("Desconectar", use_container_width=True):
        close_serial_port()
        st.session_state.last_status = "Porta serial desconectada."

if st.session_state.last_status:
    st.info(st.session_state.last_status)

if st.session_state.last_trigger_time:
    st.info(f"Último envio em: {st.session_state.last_trigger_time}")


# =========================================================
# VÍDEO PRIMEIRO
# =========================================================
st.markdown("### Vídeo")

try:
    video_bytes = load_video_bytes(VIDEO_PATH)
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    if st.session_state.play_requested:
        st.components.v1.html(
                f"""
                <div style="
                display:flex;
                justify-content:center;
                align-items:center;
                width:100%;
                height:780px;
                background-color:black;
                overflow:hidden;
                border-radius:12px;
            ">
                <video
                    controls
                    autoplay
                    style="
                        width:100%;
                        height:100%;
                        object-fit:contain;
                        background-color:black;
                    "
                >
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Seu navegador não suporta vídeo HTML5.
                </video>
            </div>
            """,
            height=820,
                        )
    else:
        st.video(video_bytes)

except Exception as e:
    st.error(f"Erro ao carregar/exibir vídeo: {e}")