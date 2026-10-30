# Script que simula múltiplos clientes concorrentes conectando-se ao servidor

import os
import sys
import time
import threading
import socket

# Garante que a pasta raiz do projeto esteja no Python Path para importar a classe Connection corretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.protocol import Connection

