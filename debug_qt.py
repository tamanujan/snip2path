import sys
print("--- Check 1: Starting ---")
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    print("--- Check 2: Import Success ---")
    app = QApplication(sys.argv)
    print("--- Check 3: App Instance Created ---")
    msg = QMessageBox()
    msg.setText("Hello! If you see this, Qt is working!")
    msg.show()
    print("--- Check 4: Dialog Shown (Waiting for close) ---")
    sys.exit(app.exec())
except Exception as e:
    print(f"--- ERROR: {e} ---")
