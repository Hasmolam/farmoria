import os
import sys

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root) 