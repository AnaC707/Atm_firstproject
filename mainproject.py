from logicproject import *
import sys

def main():
    application = QApplication(sys.argv)
    window = Logic()
    window.show()
    application.exec()

if __name__ == "__main__":
    main()