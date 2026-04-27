from flask import Flask, jsonify
import serial

app = Flask(__name__)

COM_PORT = "COM4"
BAUDRATE = 115200
START_BYTE = bytes([0x01])
STOP_BYTE = bytes([0x00])


def send_bytes(payload: bytes):
    with serial.Serial(
        port=COM_PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        write_timeout=1,
    ) as ser:
        ser.write(payload)
        ser.flush()


@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "message": f"Bridge ativo em {COM_PORT} @ {BAUDRATE} baud."
        }
    )


@app.post("/trigger")
def trigger():
    try:
        send_bytes(START_BYTE)
        return jsonify(
            {
                "ok": True,
                "message": "Trigger 0x01 enviado com sucesso."
            }
        )
    except Exception as e:
        return jsonify(
            {
                "ok": False,
                "message": f"Erro ao enviar trigger 0x01: {e}"
            }
        ), 500


@app.post("/stop")
def stop():
    try:
        send_bytes(STOP_BYTE)
        return jsonify(
            {
                "ok": True,
                "message": "Trigger 0x00 enviado com sucesso."
            }
        )
    except Exception as e:
        return jsonify(
            {
                "ok": False,
                "message": f"Erro ao enviar trigger 0x00: {e}"
            }
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False)