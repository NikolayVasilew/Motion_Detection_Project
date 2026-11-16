"""
Откриване на движение във видео чрез адаптивно изваждане на фона (MOG2).
Използване:
    python motion_detection.py --source 0
    python motion_detection.py --source demo_motion.mp4 --output result.mp4
Натиснете Q или ESC за прекратяване.
"""
import argparse
import csv
import os
import time
from pathlib import Path

import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Откриване на движение с OpenCV MOG2")
    parser.add_argument("--source", default="0", help="Индекс на камера (0) или път до видео файл")
    parser.add_argument("--output", default="", help="Незадължителен път за запис на обработеното видео")
    parser.add_argument("--csv", default="motion_log.csv", help="CSV файл със статистика по кадри")
    parser.add_argument("--min-area", type=int, default=700, help="Минимална площ на контур в пиксели")
    parser.add_argument("--history", type=int, default=500, help="Брой кадри за модела на фона")
    parser.add_argument("--var-threshold", type=float, default=16.0, help="Праг на MOG2")
    parser.add_argument("--no-shadow", action="store_true", help="Изключва маркирането на сенки")
    return parser.parse_args()


def main():
    args = parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Грешка: източникът не може да бъде отворен: {args.source}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    if not input_fps or input_fps <= 0:
        input_fps = 20.0

    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=args.history,
        varThreshold=args.var_threshold,
        detectShadows=not args.no_shadow
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    video_writer = None
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        codec = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(str(output_path), codec, input_fps, (width, height))
        if not video_writer.isOpened():
            raise SystemExit("Грешка: не може да бъде създаден изходният видеофайл.")

    csv_file = open(args.csv, "w", newline="", encoding="utf-8-sig")
    log = csv.writer(csv_file)
    log.writerow(["frame", "moving_regions", "foreground_pixels", "processing_ms", "fps"])

    frame_index = 0
    total_regions = 0
    total_processing = 0.0
    max_regions = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            start = time.perf_counter()
            mask = subtractor.apply(frame)

            # Премахване на единични шумови пиксели и запълване на малки прекъсвания.
            _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            detections = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < args.min_area:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Motion: {int(area)} px",
                            (x, max(20, y-8)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 1, cv2.LINE_AA)
                detections += 1

            elapsed_ms = (time.perf_counter() - start) * 1000.0
            current_fps = 1000.0 / elapsed_ms if elapsed_ms > 0 else 0.0
            foreground_pixels = int(cv2.countNonZero(mask))
            frame_index += 1
            total_regions += detections
            total_processing += elapsed_ms
            max_regions = max(max_regions, detections)

            cv2.putText(frame, f"Frame: {frame_index} | Moving regions: {detections}",
                        (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
            log.writerow([frame_index, detections, foreground_pixels,
                          f"{elapsed_ms:.3f}", f"{current_fps:.2f}"])

            if video_writer is not None:
                video_writer.write(frame)

            cv2.imshow("Motion Detection - MOG2", frame)
            cv2.imshow("Foreground mask", mask)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        cap.release()
        if video_writer is not None:
            video_writer.release()
        csv_file.close()
        cv2.destroyAllWindows()

    avg_ms = total_processing / frame_index if frame_index else 0.0
    avg_fps = 1000.0 / avg_ms if avg_ms > 0 else 0.0
    print("Обработка приключи.")
    print(f"Кадри: {frame_index}")
    print(f"Средно време за кадър: {avg_ms:.3f} ms")
    print(f"Средна скорост: {avg_fps:.2f} кадъра/s")
    print(f"Максимален брой области в кадър: {max_regions}")
    print(f"CSV отчет: {args.csv}")


if __name__ == "__main__":
    main()
