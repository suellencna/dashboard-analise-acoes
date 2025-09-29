# 📧 Email de Boas-vindas - Ponto Ótimo Invest

## 🎯 **Texto para Configurar no Hotmart**

### **Assunto:**
```
🎉 Bem-vindo ao Ponto Ótimo Invest - Sua carteira ideal te espera!
```

### **Conteúdo do Email:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo ao Ponto Ótimo Invest</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; background-color: #f8f9fa;">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px 30px; text-align: center; border-radius: 15px 15px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold;">🎯 PONTO ÓTIMO INVEST</h1>
        <p style="color: #e0e0e0; margin: 15px 0 0 0; font-size: 18px; font-weight: 300;">A carteira ideal ao seu alcance</p>
    </div>
    
    <!-- Conteúdo Principal -->
    <div style="background: white; padding: 40px 30px; border-radius: 0 0 15px 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        
        <!-- Saudação -->
        <h2 style="color: #2c3e50; margin-top: 0; font-size: 24px;">Olá, {{buyer.name}}! 👋</h2>
        
        <p style="font-size: 18px; color: #555; margin-bottom: 30px;">
            <strong>🎉 Sua compra foi aprovada com sucesso! 🎉</strong>
        </p>
        
        <p style="font-size: 16px; color: #666; margin-bottom: 30px;">
            Estamos super animados em lhe dar as boas-vindas a bordo! Seu acesso à nossa 
            <strong style="color: #1e3c72;">plataforma profissional de análise de carteiras</strong> 
            já está todo configurado e pronto para você mergulhar no mundo dos investimentos.
        </p>
        
        <!-- Dados de Acesso -->
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 12px; border-left: 5px solid #28a745; margin: 30px 0;">
            <h3 style="color: #28a745; margin-top: 0; font-size: 20px;">🔑 Seus Dados de Acesso</h3>
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 15px 0;">
                <p style="margin: 10px 0; font-size: 16px;"><strong>📧 Email:</strong> {{buyer.email}}</p>
                <p style="margin: 10px 0; font-size: 16px;"><strong>🔐 Senha:</strong> <code style="background: #e9ecef; padding: 6px 12px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 16px; color: #1e3c72; font-weight: bold;">123456</code></p>
            </div>
        </div>
        
        <!-- Botão de Acesso -->
        <div style="text-align: center; margin: 35px 0;">
            <a href="https://streamlit-analise-acoes.onrender.com/" style="display: inline-block; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3); transition: all 0.3s ease;">
                🚀 Acesse Sua Plataforma Agora
            </a>
        </div>
        
        <!-- Recursos -->
        <div style="background: #e7f3ff; padding: 25px; border-radius: 12px; border-left: 5px solid #007bff; margin: 30px 0;">
            <h4 style="color: #007bff; margin-top: 0; font-size: 18px;">💼 O que você pode fazer na plataforma:</h4>
            <ul style="color: #004085; margin: 15px 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;"><strong>Análise Markowitz e Monte Carlo</strong> - Otimização científica de carteiras</li>
                <li style="margin-bottom: 8px;"><strong>Métricas em tempo real</strong> - Acompanhe performance instantaneamente</li>
                <li style="margin-bottom: 8px;"><strong>Otimização de portfólio</strong> - Encontre o ponto ótimo de risco/retorno</li>
                <li style="margin-bottom: 8px;"><strong>Interface intuitiva</strong> - Fácil de usar, poderoso nos resultados</li>
            </ul>
        </div>
        
        <!-- Aviso de Segurança -->
        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 25px 0;">
            <h4 style="color: #856404; margin-top: 0; font-size: 16px;">⚠️ Importante - Segurança</h4>
            <p style="color: #856404; margin-bottom: 0; font-size: 14px;">
                Esta é uma senha temporária. Por segurança, recomendamos que você altere sua senha no primeiro acesso à plataforma.
            </p>
        </div>
        
        <!-- Mensagem Final -->
        <div style="text-align: center; margin: 40px 0 20px 0;">
            <p style="font-size: 16px; color: #666; margin-bottom: 20px;">
                <strong>Pronto para explorar?</strong> Sua plataforma de análise de carteiras espera por você, 
                cheia de possibilidades para descobrir e aproveitar.
            </p>
            
            <p style="font-size: 16px; color: #666; margin-bottom: 30px;">
                Estamos empolgados para ver onde essa nova jornada de investimentos vai levar você! 🚀
            </p>
            
            <div style="border-top: 2px solid #e9ecef; padding-top: 25px;">
                <p style="font-size: 14px; color: #888; margin: 0;">
                    <strong>Equipe Ponto Ótimo Invest</strong><br>
                    <em>Transformando dados em decisões inteligentes</em>
                </p>
            </div>
        </div>
        
    </div>
    
    <!-- Footer -->
    <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
        <p style="margin: 0;">
            © 2024 Ponto Ótimo Invest. Todos os direitos reservados.<br>
            Este é um email automático, não responda a esta mensagem.
        </p>
    </div>
    
</body>
</html>
```

---

## 🎯 **Como Configurar no Hotmart:**

### **1. Acesse Configurações do Produto:**
- Vá em "Meus Produtos" no Hotmart
- Selecione "Ponto Ótimo Invest"
- Clique em "Configurações"

### **2. Configure Email de Boas-vindas:**
- **Assunto:** `🎉 Bem-vindo ao Ponto Ótimo Invest - Sua carteira ideal te espera!`
- **Conteúdo:** Cole o HTML acima
- **Ativar:** Email automático

### **3. Variáveis do Hotmart:**
- `{{buyer.name}}` - Nome do comprador
- `{{buyer.email}}` - Email do comprador
- `{{product.name}}` - Nome do produto

### **4. Link de Acesso:**
- Substitua `https://seu-app.onrender.com` pelo seu link real
- Exemplo: `https://analise-acoes.onrender.com`

---

## 🎨 **Características do Email:**

### ✅ **Design Profissional:**
- **Gradiente azul** da marca
- **Layout responsivo** para mobile
- **Tipografia moderna** e legível

### ✅ **Conteúdo Claro:**
- **Dados de acesso** destacados
- **Botão de ação** chamativo
- **Recursos da plataforma** listados

### ✅ **Segurança:**
- **Aviso sobre senha** temporária
- **Instruções claras** de acesso
- **Orientação** para trocar senha

### ✅ **Marca Ponto Ótimo:**
- **Cores da marca** (azul e verde)
- **Tom profissional** e confiável
- **Espírito** de análise de investimentos

---

## 🚀 **Resultado:**

**Email lindo, profissional e no espírito do Ponto Ótimo Invest!**

- ✅ **Visual atrativo** e moderno
- ✅ **Informações claras** e organizadas
- ✅ **Call-to-action** efetivo
- ✅ **Marca consistente** e profissional

**🎯 Pronto para configurar no Hotmart!**
