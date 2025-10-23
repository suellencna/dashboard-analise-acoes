#!/usr/bin/env python3
"""
Servidor temporário para testar página de ativação
Funciona independentemente do Railway
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Servir a página de ativação
            self.path = '/ativacao_funcional.html'
        return super().do_GET()

def iniciar_servidor():
    """Iniciar servidor local para testar"""
    
    # Mudar para o diretório atual
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Configurar servidor
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, CustomHandler)
    
    print("=" * 60)
    print("🚀 SERVIDOR TEMPORÁRIO INICIADO")
    print("=" * 60)
    print(f"📱 URL: http://localhost:{port}")
    print(f"🔗 Página de ativação: http://localhost:{port}/")
    print("=" * 60)
    print("📝 INSTRUÇÕES:")
    print("1. Abra o navegador em: http://localhost:8000")
    print("2. Teste a página de ativação")
    print("3. Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    
    # Abrir navegador automaticamente
    try:
        webbrowser.open(f'http://localhost:{port}')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
        httpd.shutdown()

if __name__ == "__main__":
    iniciar_servidor()
