#!/usr/bin/env python3
"""
Script para capturar dados CSV do MPU6050 via serial (ESP32).

Uso:
    python3 serial_capture.py                          # porta e nome padrão
    python3 serial_capture.py -p /dev/ttyUSB0          # especificar porta
    python3 serial_capture.py -o teste_vibracao.csv     # especificar arquivo de saída
    python3 serial_capture.py -d 30                     # capturar por 30 segundos
    python3 serial_capture.py -p /dev/ttyACM0 -d 60 -o meu_teste.csv

Pressione Ctrl+C a qualquer momento para parar e salvar.
"""

import serial
import argparse
import time
import sys
import os


def find_serial_port():
    """Tenta encontrar a porta serial do ESP32 automaticamente."""
    candidates = [
        "/dev/ttyACM0", "/dev/ttyACM1",
    ]
    for port in candidates:
        if os.path.exists(port):
            return port
    return "/dev/ttyUSB0"  # fallback


def capture(port, baudrate, output_file, duration):
    """Captura dados CSV do serial e salva em arquivo."""
    print(f"📡 Conectando em {port} @ {baudrate} baud...")

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"❌ Erro ao abrir porta {port}: {e}")
        print("   Dica: verifique a porta com `ls /dev/ttyUSB* /dev/ttyACM*`")
        sys.exit(1)

    print(f"📁 Salvando em: {output_file}")
    if duration:
        print(f"⏱️  Duração: {duration}s")
    print(f"   Pressione Ctrl+C para parar.\n")

    line_count = 0
    header_written = False
    start_time = time.time()

    try:
        with open(output_file, "w") as f:
            while True:
                # verificar duração
                if duration and (time.time() - start_time) >= duration:
                    print(f"\n⏱️  Tempo atingido ({duration}s).")
                    break

                # ler linha do serial
                raw = ser.readline()
                if not raw:
                    continue

                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                except UnicodeDecodeError:
                    continue

                # filtrar apenas linhas CSV
                if not line.startswith("CSV:"):
                    # mostrar outros logs normalmente
                    if line:
                        print(f"  [LOG] {line}")
                    continue

                # remover prefixo "CSV:"
                csv_line = line[4:]

                # header
                if csv_line.startswith("timestamp_ms"):
                    if not header_written:
                        f.write(csv_line + "\n")
                        header_written = True
                        print(f"  ✅ Header: {csv_line}")
                    continue

                # dado
                f.write(csv_line + "\n")
                line_count += 1

                # feedback a cada 10 linhas
                if line_count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"  📊 {line_count} amostras | {elapsed:.1f}s | último: {csv_line}")

    except KeyboardInterrupt:
        print(f"\n\n🛑 Captura interrompida pelo usuário.")

    finally:
        ser.close()
        print(f"\n✅ {line_count} amostras salvas em '{output_file}'")


def main():
    parser = argparse.ArgumentParser(description="Captura dados CSV do MPU6050 via serial")
    parser.add_argument("-p", "--port", default=None,
                        help="Porta serial (ex: /dev/ttyUSB0). Auto-detecta se omitido.")
    parser.add_argument("-b", "--baud", type=int, default=115200,
                        help="Baudrate (padrão: 115200)")
    parser.add_argument("-o", "--output", default=None,
                        help="Arquivo CSV de saída (padrão: mpu6050_YYYYMMDD_HHMMSS.csv)")
    parser.add_argument("-d", "--duration", type=float, default=None,
                        help="Duração da captura em segundos (padrão: até Ctrl+C)")

    args = parser.parse_args()

    port = args.port or find_serial_port()

    # solicitar nome do teste
    test_name = input("📝 Nome do teste (será usado como diretório e arquivo): ").strip()
    if not test_name:
        test_name = time.strftime("mpu6050_%Y%m%d_%H%M%S")
        print(f"   Nome vazio, usando: {test_name}")

    test_dir = os.path.join("data", test_name)
    os.makedirs(test_dir, exist_ok=True)

    output_file = os.path.join(test_dir, f"{test_name}.csv")

    capture(port, args.baud, output_file, args.duration)


if __name__ == "__main__":
    main()
