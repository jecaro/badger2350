try:
    with open("hardware_test.txt", "r"):
        import hardware_test   # noqa F401
except OSError:
    pass

try:
    __import__("/main")
except ImportError:
    __import__("/system/main")
