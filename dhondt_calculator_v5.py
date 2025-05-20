import sys
import csv
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog, QMessageBox, QScrollArea, QSizePolicy,
                             QSpinBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QBrush, QIntValidator


class DHondtCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D'Hondt Method Seat Calculator")
        self.setMinimumSize(900, 600)  # Reduced minimum window size
        
        # Variables
        self.max_parties = 12
        self.divisors = 20
        self.party_names = ["Party " + str(i+1) for i in range(self.max_parties)]
        self.votes = [0] * self.max_parties
        self.dark_mode = False  # Dark mode state
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header controls
        self.create_header_controls(main_layout)
        
        # Create the table
        self.create_table(main_layout)
        
        # Initial calculation
        self.update_calculations()
        
    def create_header_controls(self, main_layout):
        header_layout = QHBoxLayout()
        
        # Election name
        header_layout.addWidget(QLabel("Election Name:"))
        self.election_name_edit = QLineEdit("Election")
        self.election_name_edit.setMinimumWidth(300)  # Make election name box wider
        header_layout.addWidget(self.election_name_edit)
        
        # Seats to distribute
        header_layout.addWidget(QLabel("Seats to Distribute:"))
        self.seats_spin = QSpinBox()
        self.seats_spin.setRange(0, 1000)
        self.seats_spin.setValue(7)
        self.seats_spin.setMaximumWidth(80)
        self.seats_spin.valueChanged.connect(self.update_calculations)
        header_layout.addWidget(self.seats_spin)
        
        # Sort button
        self.sort_button = QPushButton("Sort by Votes")
        self.sort_button.setStyleSheet("background-color: #ffcc99;")
        self.sort_button.clicked.connect(self.sort_by_votes)
        header_layout.addWidget(self.sort_button)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Dark mode toggle
        self.dark_mode_button = QPushButton("Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        header_layout.addWidget(self.dark_mode_button)
        
        # Save and Load buttons
        self.save_button = QPushButton("Save to CSV")
        self.save_button.setStyleSheet("background-color: #add8e6;")
        self.save_button.clicked.connect(self.save_data)
        header_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load from CSV")
        self.load_button.setStyleSheet("background-color: #90ee90;")
        self.load_button.clicked.connect(self.load_data)
        header_layout.addWidget(self.load_button)
        
        main_layout.addLayout(header_layout)
    
    def create_table(self, main_layout):
        # Create a scroll area for the table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create the table widget with rows for each party and columns for divisors
        self.table = QTableWidget(self.max_parties, self.divisors + 3)
        self.table.setHorizontalHeaderLabels(["Seats", "Party", "Votes"] + 
                                              [f"÷{i+1}" if i > 0 else "Votes" for i in range(self.divisors)])
        
        # Set up the table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.table.horizontalHeader().setStyleSheet("background-color: #e0e0e0;")
        
        # Configure column widths - reduced for smaller screens
        self.table.setColumnWidth(0, 50)   # Seats column - smaller
        self.table.setColumnWidth(1, 80)   # Party name column - much smaller
        self.table.setColumnWidth(2, 70)   # Votes column - smaller
        
        # Set minimum section size for scrollable divisor columns
        for i in range(3, self.divisors + 3):
            self.table.setColumnWidth(i, 60)  # Divisors - smaller
        
        # Create table items
        self.seat_items = []
        self.party_name_edits = []
        self.vote_edits = []
        self.division_items = []
        
        for row in range(self.max_parties):
            # Seat count (will be updated by calculations)
            seat_item = QTableWidgetItem("0")
            seat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            seat_item.setFlags(seat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, seat_item)
            self.seat_items.append(seat_item)
            
            # Party name edit
            party_edit = QLineEdit(self.party_names[row])
            party_edit.setPlaceholderText("Party name")
            self.table.setCellWidget(row, 1, party_edit)
            self.party_name_edits.append(party_edit)
            
            # Votes edit
            vote_edit = QLineEdit("0")
            vote_edit.setValidator(QIntValidator(0, 999999999))
            vote_edit.setPlaceholderText("Votes")
            vote_edit.textChanged.connect(self.update_calculations)
            self.table.setCellWidget(row, 2, vote_edit)
            self.vote_edits.append(vote_edit)
            
            # Division result cells
            row_items = []
            for col in range(self.divisors):
                div_item = QTableWidgetItem("0")
                div_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                div_item.setFlags(div_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col + 3, div_item)
                row_items.append(div_item)
            self.division_items.append(row_items)
            
        scroll_area.setWidget(self.table)
        main_layout.addWidget(scroll_area)
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Dark mode styles
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QTableWidget {
                    gridline-color: #555555;
                    color: #e0e0e0;
                    background-color: #383838;
                    selection-background-color: #4a4a9e;
                }
                QHeaderView::section {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    padding: 4px;
                    border: 1px solid #555555;
                }
                QPushButton {
                    background-color: #444444;
                    color: #e0e0e0;
                    padding: 6px 12px;
                    border-radius: 4px;
                    border: 1px solid #666666;
                }
                QLineEdit, QSpinBox {
                    background-color: #444444;
                    color: #e0e0e0;
                    padding: 4px;
                    border: 1px solid #666666;
                    border-radius: 3px;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """)
            
            # Update button styling
            self.sort_button.setStyleSheet("background-color: #825e33;")
            self.save_button.setStyleSheet("background-color: #386077;")
            self.load_button.setStyleSheet("background-color: #336633;")
            self.dark_mode_button.setText("Light Mode")
            
            # Update table cell colors for calculations
            self.update_calculations()
        else:
            # Light mode styles
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QTableWidget {
                    gridline-color: #d0d0d0;
                    selection-background-color: #c2dbf5;
                }
                QHeaderView::section {
                    background-color: #e0e0e0;
                    padding: 4px;
                    border: 1px solid #c0c0c0;
                }
                QPushButton {
                    padding: 6px 12px;
                    border-radius: 4px;
                    border: 1px solid #c0c0c0;
                }
                QLineEdit, QSpinBox {
                    padding: 4px;
                    border: 1px solid #c0c0c0;
                    border-radius: 3px;
                }
            """)
            
            # Reset button styling
            self.sort_button.setStyleSheet("background-color: #ffcc99;")
            self.save_button.setStyleSheet("background-color: #add8e6;")
            self.load_button.setStyleSheet("background-color: #90ee90;")
            self.dark_mode_button.setText("Dark Mode")
            
            # Update table cell colors for calculations
            self.update_calculations()
    
    def update_calculations(self):
        # Get the number of seats
        num_seats = self.seats_spin.value()
        
        # Get votes for each party
        vote_values = []
        for vote_edit in self.vote_edits:
            try:
                votes = max(0, int(vote_edit.text()))
            except:
                votes = 0
            vote_values.append(votes)
        
        # Calculate all division results
        all_values = []
        
        for party_idx, votes in enumerate(vote_values):
            for div in range(1, self.divisors + 1):
                if votes == 0:
                    result = 0
                else:
                    result = votes / div
                all_values.append((result, party_idx, div))
                
                # Update division label
                item = self.division_items[party_idx][div-1]
                if votes > 0:
                    item.setText(f"{result:.1f}")
                else:
                    item.setText("0")
                
                # Reset background - considering dark mode
                if self.dark_mode:
                    item.setBackground(QBrush(QColor(56, 56, 56)))  # Dark background
                else:
                    item.setBackground(QBrush(QColor(255, 255, 255)))  # White background
        
        # Sort quotients in descending order
        all_values.sort(reverse=True)
        
        # Reset seat counts
        seat_counts = [0] * self.max_parties
        
        # Assign seats and highlight the cells
        for s in range(min(num_seats, len(all_values))):
            if s < len(all_values):
                value, party_idx, divisor = all_values[s]
                if value > 0:  # Only assign if the value is positive
                    item = self.division_items[party_idx][divisor-1]
                    # Use darker green in dark mode
                    if self.dark_mode:
                        item.setBackground(QBrush(QColor(0, 100, 0)))  # Dark green
                    else:
                        item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
                    seat_counts[party_idx] += 1
        
        # Highlight the next potential seat in a different color
        if num_seats < len(all_values) and all_values[num_seats][0] > 0:
            next_value, next_party_idx, next_divisor = all_values[num_seats]
            next_item = self.division_items[next_party_idx][next_divisor-1]
            # Use darker orange in dark mode
            if self.dark_mode:
                next_item.setBackground(QBrush(QColor(204, 85, 0)))  # Dark orange
            else:
                next_item.setBackground(QBrush(QColor(255, 165, 0)))  # Orange
        
        # Update seat count labels
        for i, count in enumerate(seat_counts):
            self.seat_items[i].setText(str(count))
    
    def sort_by_votes(self):
        # Get the party names and votes
        parties_data = []
        for i in range(self.max_parties):
            try:
                vote_count = int(self.vote_edits[i].text())
            except ValueError:
                vote_count = 0
            
            parties_data.append({
                'index': i,
                'name': self.party_name_edits[i].text(),
                'votes': vote_count
            })
        
        # Sort by votes (descending)
        parties_data.sort(key=lambda x: x['votes'], reverse=True)
        
        # Update the UI with sorted data
        for i, party_data in enumerate(parties_data):
            self.party_name_edits[i].setText(party_data['name'])
            self.vote_edits[i].setText(str(party_data['votes']))
        
        # Update calculations with the new order
        self.update_calculations()
    
    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Election Data",
            "",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:  # If user cancels the save dialog
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row with metadata
                writer.writerow(['Election Name', self.election_name_edit.text()])
                writer.writerow(['Seats', str(self.seats_spin.value())])
                
                # Write column headers for party data
                writer.writerow(['Party', 'Votes'])
                
                # Write party data
                for i in range(self.max_parties):
                    writer.writerow([
                        self.party_name_edits[i].text(),
                        self.vote_edits[i].text()
                    ])
                
            QMessageBox.information(self, "Success", f"Data saved to {os.path.basename(file_path)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Election Data",
            "",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:  # If user cancels the dialog
            return
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Read election name
                row = next(reader)
                if len(row) >= 2 and row[0] == 'Election Name':
                    self.election_name_edit.setText(row[1])
                
                # Read seats
                row = next(reader)
                if len(row) >= 2 and row[0] == 'Seats':
                    try:
                        self.seats_spin.setValue(int(row[1]))
                    except ValueError:
                        self.seats_spin.setValue(0)
                
                # Skip the column headers
                next(reader)
                
                # Read party data
                for i in range(self.max_parties):
                    try:
                        row = next(reader)
                        if len(row) >= 2:
                            self.party_name_edits[i].setText(row[0])
                            self.vote_edits[i].setText(row[1])
                        else:
                            # Clear any remaining rows
                            self.party_name_edits[i].setText("")
                            self.vote_edits[i].setText("0")
                    except StopIteration:
                        # Clear any remaining rows
                        self.party_name_edits[i].setText("")
                        self.vote_edits[i].setText("0")
            
            # Update calculations with new data
            self.update_calculations()
            QMessageBox.information(self, "Success", f"Data loaded from {os.path.basename(file_path)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern cross-platform style
    
    # Set application stylesheet for a more modern look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QTableWidget {
            gridline-color: #d0d0d0;
            selection-background-color: #c2dbf5;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #c0c0c0;
        }
        QPushButton {
            padding: 6px 12px;
            border-radius: 4px;
            border: 1px solid #c0c0c0;
        }
        QLineEdit, QSpinBox {
            padding: 4px;
            border: 1px solid #c0c0c0;
            border-radius: 3px;
        }
    """)
    
    window = DHondtCalculator()
    window.show()
    sys.exit(app.exec())