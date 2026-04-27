import cv2
import pandas as pd
import numpy as np
from pathlib import Path


# ============================
# CONFIGURAÇÕES
# ============================

VIDEO_PATH = r"C:\Users\admin\Documents\Doutorado\estim_portaCOM\my_app\video\Protocolo_10_repeticoes_final.mp4"
OUTPUT_CSV = "instantes_mudanca_video.csv"

# Para evitar detectar várias mudanças muito próximas
TEMPO_MINIMO_ENTRE_MUDANCAS = 0.300  # segundos

# Reduz o tamanho do frame para acelerar o processamento
LARGURA_PROCESSAMENTO = 320


# ============================
# FUNÇÕES
# ============================

def formatar_tempo(segundos: float) -> str:
    minutos = int(segundos // 60)
    seg = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{minutos:02d}:{seg:02d}.{ms:03d}"


def preprocessar_frame(frame):
    """
    Reduz, converte para cinza e aplica leve suavização.
    """
    h, w = frame.shape[:2]
    proporcao = LARGURA_PROCESSAMENTO / w
    nova_altura = int(h * proporcao)

    frame = cv2.resize(frame, (LARGURA_PROCESSAMENTO, nova_altura))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    return gray


# ============================
# ABRIR VÍDEO
# ============================

video_path = Path(VIDEO_PATH)

if not video_path.exists():
    raise FileNotFoundError(f"Vídeo não encontrado: {video_path.resolve()}")

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    raise RuntimeError("Não foi possível abrir o vídeo.")

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duracao_video = total_frames / fps

print(f"FPS do vídeo: {fps}")
print(f"Total de frames: {total_frames}")
print(f"Duração aproximada: {duracao_video:.3f} segundos")


# ============================
# PRIMEIRA PASSAGEM: MEDIR DIFERENÇAS
# ============================

ret, frame_anterior = cap.read()

if not ret:
    raise RuntimeError("Não foi possível ler o primeiro frame.")

frame_anterior = preprocessar_frame(frame_anterior)

diferencas = []
frames = []
tempos = []

frame_idx = 1

while True:
    ret, frame_atual = cap.read()

    if not ret:
        break

    frame_atual = preprocessar_frame(frame_atual)

    diff = cv2.absdiff(frame_anterior, frame_atual)
    media_diferenca = diff.mean()

    tempo_atual = frame_idx / fps

    diferencas.append(media_diferenca)
    frames.append(frame_idx)
    tempos.append(tempo_atual)

    frame_anterior = frame_atual
    frame_idx += 1

cap.release()

diferencas = np.array(diferencas)

print("\nEstatísticas das diferenças entre frames:")
print(f"Mínimo: {diferencas.min():.4f}")
print(f"Média: {diferencas.mean():.4f}")
print(f"Mediana: {np.median(diferencas):.4f}")
print(f"Máximo: {diferencas.max():.4f}")
print(f"Percentil 95: {np.percentile(diferencas, 95):.4f}")
print(f"Percentil 99: {np.percentile(diferencas, 99):.4f}")
print(f"Percentil 99.5: {np.percentile(diferencas, 99.5):.4f}")


# ============================
# LIMIAR AUTOMÁTICO
# ============================

# Detecta apenas diferenças muito acima do comportamento normal do vídeo
threshold = np.percentile(diferencas, 99.5)

print(f"\nThreshold automático usado: {threshold:.4f}")


# ============================
# DETECTAR MUDANÇAS
# ============================

mudancas = []
ultimo_tempo_detectado = -999

for frame_idx, tempo_atual, media_diferenca in zip(frames, tempos, diferencas):

    if media_diferenca >= threshold:
        if tempo_atual - ultimo_tempo_detectado >= TEMPO_MINIMO_ENTRE_MUDANCAS:

            mudancas.append({
                "frame": frame_idx,
                "tempo_segundos": round(tempo_atual, 3),
                "tempo_formatado": formatar_tempo(tempo_atual),
                "diferenca_media": round(float(media_diferenca), 4)
            })

            ultimo_tempo_detectado = tempo_atual


# ============================
# SALVAR RESULTADO
# ============================

df = pd.DataFrame(mudancas)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("\nMudanças detectadas:")
print(df)

print(f"\nTotal de mudanças detectadas: {len(df)}")
print(f"Arquivo salvo em: {OUTPUT_CSV}")