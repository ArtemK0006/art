import sys
print("Пути поиска модулей:")
for path in sys.path:
    print(f"  {path}")

print("\nПытаюсь импортировать qrcode...")
try:
    import qrcode
    print("✅ qrcode найден!")
    print(f"   Версия: {qrcode.__version__}")
except ImportError as e:
    print(f"❌ Ошибка: {e}")

print("\nПытаюсь импортировать PIL...")
try:
    from PIL import Image
    print("✅ PIL найден!")
except ImportError as e:
    print(f"❌ Ошибка: {e}")

input("\nНажмите Enter для выхода...")