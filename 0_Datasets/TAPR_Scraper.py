"""
GUI for TAPR Scraper. This code allows you to download data on your specified level.
The code automatically gives you clean and raw data
"""
#Importing necessary files: 
from scraping import tea_scraper
from wrangling import process_and_save_all_data
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                            QPushButton, QTextEdit, QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from functools import partial
import ast

# Creating a class to store GUI in 
class ScraperWorker(QThread):
    """Worker thread to run the scraper and data processing without blocking the GUI."""
    progress = pyqtSignal(str)  # Signal for progress updates
    finished = pyqtSignal()  # Signal emitted when work is done

    def __init__(self, directory, years, variables, level):
        super().__init__()
        self.directory = directory  # Directory where data will be saved
        self.years = years  # List of years to scrape
        self.variables = variables  # List of variables to scrape
        self.level = level  # Data granularity level (C, D, R, S)

    def run(self):
        """Run the scraping and data processing in a separate thread."""
        import builtins
        original_print = builtins.print  # Store original print function
        
        def custom_print(*args, **kwargs):
            """Custom print function to emit progress updates to GUI."""
            text = ' '.join(map(str, args))
            self.progress.emit(text)  # Send progress to GUI
            original_print(*args, **kwargs)  # Maintain console output

        builtins.print = custom_print  # Override built-in print with custom_print

        try:
            self.progress.emit("Starting TEA Scraper...")
            tea_scraper(self.directory, self.years, self.variables, self.level)  # Run scraper
            self.progress.emit("Scraping completed. Starting data processing...")

            process_and_save_all_data(self.directory, self.level)  # Run data processing
            self.progress.emit("Data processing completed successfully!")
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")  # Display errors in GUI
        finally:
            builtins.print = original_print  # Restore original print function
            self.finished.emit()  # Signal that processing is complete

class MainWindow(QMainWindow):
    """Main GUI window for the TEA Data Scraper application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEA Data Scraper")  # Set window title
        self.setMinimumWidth(600)  # Set minimum width
        self.setMinimumHeight(400)  # Set minimum height

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Directory selection layout
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()  # Input field for directory
        dir_button = QPushButton("Browse...")  # Button to browse for directory
        dir_button.clicked.connect(self.browse_directory)  # Connect button to function
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)

        # Years input layout
        years_layout = QHBoxLayout()
        self.years_input = QLineEdit()
        self.years_input.setPlaceholderText("e.g., [2020, 2021, 2022]")  # Placeholder example
        years_layout.addWidget(QLabel("Years:"))
        years_layout.addWidget(self.years_input)
        layout.addLayout(years_layout)

        # Variables input layout
        vars_layout = QHBoxLayout()
        self.vars_input = QLineEdit()
        self.vars_input.setPlaceholderText("e.g., ['GRAD', 'PROF', 'STAAR1']")  # Placeholder example
        vars_layout.addWidget(QLabel("Variables:"))
        vars_layout.addWidget(self.vars_input)
        layout.addLayout(vars_layout)

        # Level selection layout
        level_layout = QHBoxLayout()
        self.level_combo = QComboBox()
        self.level_combo.addItems(['Campus (C)', 'District (D)', 'Region (R)', 'State (S)'])  # Drop-down menu
        level_layout.addWidget(QLabel("Level:"))
        level_layout.addWidget(self.level_combo)
        layout.addLayout(level_layout)

        # Progress display field
        self.progress_display = QTextEdit()
        self.progress_display.setReadOnly(True)  # Make it read-only
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress_display)

        # Run button
        self.run_button = QPushButton("Run Scraper")
        self.run_button.clicked.connect(self.run_scraper)  # Connect button to function
        layout.addWidget(self.run_button)

    def browse_directory(self):
        """Opens a dialog for the user to select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)  # Update directory input field

    def run_scraper(self):
        """Validates input and starts the scraper in a separate thread."""
        try:
            # Get and validate inputs
            directory = self.dir_input.text()
            years = ast.literal_eval(self.years_input.text())  # Convert string to list
            variables = ast.literal_eval(self.vars_input.text())  # Convert string to list
            level = self.level_combo.currentText()[0]  # Extract first character (C, D, R, or S)

            # Disable run button to prevent duplicate runs
            self.run_button.setEnabled(False)
            
            # Clear previous progress messages
            self.progress_display.clear()

            # Create and start worker thread for scraping
            self.worker = ScraperWorker(directory, years, variables, level)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.scraping_finished)
            self.worker.start()
        except Exception as e:
            self.progress_display.append(f"Error: {str(e)}")  # Display error message
            self.run_button.setEnabled(True)  # Re-enable run button

    def update_progress(self, message):
        """Updates the progress display with messages from the scraper worker."""
        self.progress_display.append(message)
        self.progress_display.verticalScrollBar().setValue(
            self.progress_display.verticalScrollBar().maximum()
        )  # Auto-scroll to bottom

    def scraping_finished(self):
        """Re-enables the run button and signals completion."""
        self.run_button.setEnabled(True)
        self.progress_display.append("Scraping completed!")


# Run the GUI application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())