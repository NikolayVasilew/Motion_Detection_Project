# Откриване на движение с OpenCV (MOG2)

## Съдържание
- `motion_detection.py` – основно приложение.
- `demo_motion.mp4` – синтетичен демонстрационен видеозапис.
- `requirements.txt` – зависимости.
- `motion_log.csv` – генерира се при изпълнение.

## Инсталиране (Windows)
1. Инсталирайте Python 3.10 или по-нова версия.
2. Отворете папката във Visual Studio Code.
3. Отворете Terminal -> New Terminal.
4. Изпълнете:
   ```powershell
   py -m venv .venv
   py -m venv .venv
   pip install -r requirements.txt
   ```

## Стартиране с демонстрационното видео
```powershell
python motion_detection.py --source demo_motion.mp4 --output result.mp4
```

## Стартиране с уебкамера
```powershell
python motion_detection.py --source 0
```
Натиснете `Q` или `Esc`, за да спрете обработката. За друга камера сменете `0` с `1`.

## Параметри
- `--min-area 700` – минимална площ на открит контур.
- `--history 500` – размер на историята на модела.
- `--var-threshold 16` – праг на MOG2.
- `--no-shadow` – изключва детекцията на сенки.
- `--csv motion_log.csv` – път до CSV статистиката.

## Бележка за демонстрационния запис
`demo_motion.mp4` е синтетично генериран тестов клип с движещи се геометрични обекти. Той служи за проверка на изпълнението на програмата, а не замества оценка върху реален публичен набор от данни.
