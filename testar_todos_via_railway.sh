#!/bin/bash

echo "========================================================================"
echo "📧 TESTE COMPLETO DE EMAILS VIA RAILWAY"
echo "========================================================================"

echo ""
echo "⏰ Aguardando 45 segundos para deploy do Railway..."
sleep 45

echo ""
echo "📤 Enviando emails de teste para TODOS os provedores..."
echo "------------------------------------------------------------------------"

# Array de emails
emails=(
    "suellencna@gmail.com:Gmail 1"
    "suellencna@yahoo.com.br:Yahoo"
    "suellencna@hotmail.com:Hotmail"
    "aaisuellen@gmail.com:Gmail 2"
    "jorgehap@outlook.com:Outlook"
)

for entry in "${emails[@]}"; do
    IFS=':' read -r email nome <<< "$entry"
    
    echo ""
    echo "📧 $nome ($email)"
    
    response=$(curl -s -X POST https://web-production-e66d.up.railway.app/criar-usuario-teste \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"nome\":\"$nome\"}")
    
    if echo "$response" | grep -q '"status":"success"'; then
        echo "   ✅ ENVIADO"
        link=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('link_ativacao', 'N/A'))" 2>/dev/null || echo "N/A")
        echo "   🔗 $link"
    else
        echo "   ❌ FALHOU"
        error=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Erro desconhecido')[:100])" 2>/dev/null || echo "$response" | head -c 100)
        echo "   ⚠️  $error"
    fi
    
    sleep 3
done

echo ""
echo "========================================================================"
echo "📊 TESTE CONCLUÍDO"
echo "========================================================================"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo "1. Aguarde 2-3 minutos"
echo "2. Verifique a caixa de entrada + SPAM de TODOS os emails"
echo "3. Me informe quais emails CHEGARAM e em qual pasta"
echo ""
echo "========================================================================"
