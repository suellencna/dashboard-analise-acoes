curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-Hotmart-Hottok: s4TwuTnlY0Vdi0tMhleCntIFOfcDA5ef2c8e6b-58b6-4d60-bbf1-eaed0bac4a35" \
     -d '{
         "event": "PURCHASE_APPROVED",
         "data": {
             "buyer": {
                 "email": "test@example.com",
                 "name": "Teste Comprador"
             }
         }
     }' \
     https://analise-acoes-api-webhook.onrender.com/webhook/hotmart