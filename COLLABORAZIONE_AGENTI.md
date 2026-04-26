# Collaborazione tra agenti (Goose + Claude Code)

Obiettivo: lavorare in parallelo su `emporiumonline` senza conflitti.

## Stato attuale (Goose)
- Modifiche già fatte da Goose:
  - `data/products.json`
  - `js/products.js`
- Tipo modifica: aggiunta nuovi prodotti al catalogo.

## Regole di collaborazione

### 1) Ownership file (anti-conflitto)
- **Goose**: file catalogo prodotti
  - `data/products.json`
  - `js/products.js`
- **Claude**: tutti gli altri file (oppure concordare esplicitamente eccezioni)

> Se Claude deve toccare i file prodotti, avvisare prima e lavorare a turno.

### 2) Branch dedicati
- Goose branch consigliato: `feature/prodotti-goose`
- Claude branch consigliato: `feature/claude-<task>`

### 3) Flusso consigliato
1. Pull da `main`
2. Lavoro nel proprio branch
3. Commit piccoli e descrittivi
4. Push del branch
5. Merge in `main` solo dopo controllo conflitti

### 4) Commit message convenzione
- `feat(products): ...` per catalogo
- `fix(ui): ...`, `refactor(...): ...`, `docs(...): ...` per resto

### 5) Se c'è conflitto su `products.json` / `products.js`
- Tenere come base il file più aggiornato in ordine cronologico.
- Riapplicare manualmente le modifiche mancanti (no merge cieco).
- Verificare sempre:
  - JSON valido in `data/products.json`
  - array `window.products` valido in `js/products.js`
  - nessun ASIN duplicato

## Istruzioni per Claude Code
Ciao Claude 👋

Per evitare conflitti, per favore:
1. Non modificare `data/products.json` e `js/products.js` finché non concordato.
2. Se devi farlo, segnala prima e procedi su branch separato.
3. Mantieni commit piccoli e facili da rebase/merge.
4. Prima del merge finale, esegui un controllo rapido del sito (`index.html`) per verificare che le card prodotto renderizzino correttamente.

Grazie!

---

## Checklist rapida prima del merge in main
- [ ] `git status` pulito
- [ ] Nessun conflitto aperto
- [ ] `data/products.json` valido
- [ ] `js/products.js` valido
- [ ] Verifica homepage (`index.html`) ok
