import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QVBoxLayout, QWidget, QLabel, QGraphicsRectItem, QPushButton,
    QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor


class ImageViewer(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        # Zoom in/out with the mouse wheel
        zoom_factor = 1.25
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Convert the mouse position to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            # Emit the signal with the precise position
            self.parentWidget().add_point(scene_pos)
        super().mousePressEvent(event)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Point Selector")
        self.setGeometry(100, 100, 1000, 700)  # Увеличен размер окна для удобства

        self.scene = QGraphicsScene(self)
        self.view = ImageViewer(self.scene)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Кнопка для загрузки изображения
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image_dialog)
        self.clear_button = QPushButton("Clear Points")
        self.clear_button.clicked.connect(self.clear_points)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.clear_button)
        self.layout.addLayout(self.button_layout)

        self.layout.addWidget(self.view)

        self.coordinates_label = QLabel("Coordinates: ")
        self.layout.addWidget(self.coordinates_label)

        self.points = []  # List to store points as (number, x, y)

        self.image_item = None  # Placeholder for the image

    def add_point(self, scene_pos):
        # Добавляем точку напрямую используя координаты сцены
        point_number = len(self.points) + 1
        self.points.append((point_number, scene_pos.x(), scene_pos.y()))

        # Display the updated coordinates with precision up to one decimal place
        self.coordinates_label.setText(
            "Coordinates: " + ', '.join([f"({num}, {x:.1f}, {y:.1f})" for num, x, y in self.points])
        )

        # Add a small visual marker on the scene at the chosen point
        marker_size = 6
        rect_item = QGraphicsRectItem(QRectF(scene_pos.x() - marker_size / 2, scene_pos.y() - marker_size / 2, marker_size, marker_size))
        rect_item.setBrush(QColor(255, 0, 0, 150))
        self.scene.addItem(rect_item)

    def load_image_dialog(self):
        # Open a file dialog to select an image
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path):
        # Load the image into a QPixmap and add it to the scene
        image = QPixmap(image_path)
        if self.image_item:
            self.scene.removeItem(self.image_item)
        
        self.image_item = QGraphicsPixmapItem(image)
        self.scene.addItem(self.image_item)
        self.view.fitInView(self.image_item, Qt.KeepAspectRatio)
        
        # Reset points and clear the label
        self.clear_points()

    def clear_points(self):
        self.points.clear()
        self.coordinates_label.setText("Coordinates: ")
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
