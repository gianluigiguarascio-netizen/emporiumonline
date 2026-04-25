#!/bin/zsh
cd /Users/admin/emporiumonline

links=$(osascript -e 'text returned of (display dialog "🛍️ Incolla i link Amazon (uno per riga):" default answer "" with title "EmporiumOnline — Aggiungi Prodotti" buttons {"Annulla","Aggiungi tutti"} default button "Aggiungi tutti")')

if [ -z "$links" ]; then
  exit 0
fi

echo "$links" | while IFS= read -r url; do
  url=$(echo "$url" | tr -d '[:space:]')
  [ -z "$url" ] && continue
  echo ""
  python3 scripts/aggiungi.py "$url"
done

echo ""
echo "📤 Push in corso..."
git add data/products.json js/products.js
git commit -m "feat: aggiungi prodotti $(date '+%Y-%m-%d')"
git push

echo ""
echo "✅ Fatto! Il sito si aggiorna in ~2 minuti."
read -p "Premi INVIO per chiudere..."
