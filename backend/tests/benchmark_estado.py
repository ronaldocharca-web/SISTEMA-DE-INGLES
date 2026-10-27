"""Prueba de carga de solo lectura para ejecutar contra el backend local."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from urllib.request import urlopen


def solicitar(url: str) -> tuple[int, float]:
    inicio = perf_counter()
    with urlopen(url, timeout=15) as respuesta:
        return respuesta.status, perf_counter() - inicio


def main() -> None:
    parser = argparse.ArgumentParser(description="Mide consultas de estado sin modificar datos.")
    parser.add_argument("--url", default="http://127.0.0.1:8001/api/v1/estudiantes/inscripciones/estado")
    parser.add_argument("--solicitudes", type=int, default=100)
    parser.add_argument("--concurrencia", type=int, default=10)
    args = parser.parse_args()

    if args.solicitudes < 1 or args.concurrencia < 1:
        raise SystemExit("Las solicitudes y la concurrencia deben ser mayores que cero.")

    inicio = perf_counter()
    resultados: list[tuple[int, float]] = []
    with ThreadPoolExecutor(max_workers=args.concurrencia) as executor:
        futuros = [executor.submit(solicitar, args.url) for _ in range(args.solicitudes)]
        for futuro in as_completed(futuros):
            try:
                resultados.append(futuro.result())
            except Exception:
                resultados.append((0, 0.0))

    duracion = perf_counter() - inicio
    correctas = [latencia for estado, latencia in resultados if estado == 200]
    print(f"Solicitudes: {args.solicitudes}")
    print(f"Concurrencia: {args.concurrencia}")
    print(f"Correctas: {len(correctas)}")
    print(f"Fallidas: {args.solicitudes - len(correctas)}")
    print(f"Rendimiento: {len(correctas) / duracion:.1f} solicitudes/segundo")
    if correctas:
        print(f"Latencia promedio: {sum(correctas) / len(correctas) * 1000:.1f} ms")


if __name__ == "__main__":
    main()
