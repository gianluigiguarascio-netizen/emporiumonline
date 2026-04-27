# Product Marketing Context — EmporiumOnline

## Product Overview
- **One-line:** EmporiumOnline è un sito di affiliazione Amazon che presenta ogni giorno le offerte più colorate e di tendenza.
- **What it does:** Aggrega e mostra prodotti Amazon selezionati nelle categorie moda, scarpe, borse, accessori, casa, gadget, beauty, bambini e idee regalo. Ogni click porta all'acquisto diretto su Amazon tramite link affiliato. Guadagna commissioni Amazon tramite il programma Amazon Associates con tag `prezzotop08-21`.
- **Category:** Sito affiliato Amazon / e-commerce vetrina / blog di offerte
- **Type:** Sito statico (HTML/CSS/JS) hostato su GitHub Pages

## Business Model
- 100% affiliazione Amazon (tag: prezzotop08-21)
- Commissioni dal 3% al 10% sugli acquisti generati
- Nessun magazzino, nessuna spedizione — pura mediazione
- Target geografico: Italia

## Target Audience
- **Primario:** Donne italiane 25–45 anni interessate a moda colorata e accessori
- **Secondario:** Acquirenti alla ricerca di offerte e sconti su Amazon.it
- **Interessi:** Moda, colori, tendenze, offerte del giorno, Amazon Prime
- **Device:** Forte uso mobile (smartphone)
- **ICP:** Donna italiana 30–40 anni, ama i colori e cerca offerte Amazon senza perdere tempo

## Positioning
- **Differenziatore:** Focus sui prodotti *colorati* — non generici. L'estetica è vivace, pop, ispirata.
- **Tone of voice:** Allegro, entusiasta, femminile, accessibile
- **Valore percepito:** "Trovo offerte belle e colorate senza sfogliare Amazon da sola"

## Current Site Structure
- **URL:** https://emporiumonline.it (GitHub Pages)
- **Homepage:** Single-page app con sezioni: Offerte Pazze 🔥, Bambini, Categorie (scarpe, abbigliamento, accessori, borse, casa, gadget, beauty, idee-regalo)
- **Pagine statiche:** affiliate.html, privacy.html
- **Sitemap:** /sitemap.xml (auto-generata, 220+ URL)
- **Schema:** JSON-LD ItemList + BreadcrumbList iniettati via JS

## SEO Current State
- Dominio giovane (recente lancio)
- No traffico organico significativo ancora
- Sitemap presente e corretta
- Schema JSON-LD implementato
- Meta title e description presenti
- Canonical tag su homepage
- OG tags presenti
- Solo una pagina indicizzabile (SPA single-page, tutte le sezioni sono anchor #)
- Non ci sono pagine dedicate per categoria o prodotto (tutto su homepage)
- Non collegato a Google Search Console
- Nessun backlink esterno noto

## Competitors
- Trovaprezzi.it
- Kelkoo.it
- Blog di moda/offerte su Instagram e Pinterest
- Altri siti affiliati Amazon Italia

## Content
- ~209 prodotti nel catalogo (dati in JS)
- Categorie: scarpe(32+), abbigliamento(50+), accessori(21+), beauty, borse, casa, gadget, idee-regalo, bambini(17+)
- Sezione "Offerte Pazze" con 54 prodotti a prezzo ribassato
- Aggiornamento manuale + script Python per scraping

## Social/Distribution
- Pinterest agent configurato (agent_pinterest.py)
- Nessuna presenza Instagram/TikTok ancora
- Nessuna newsletter

## Tech Stack
- HTML5, CSS3, JavaScript vanilla
- GitHub Pages (deploy automatico via GitHub Actions su push main)
- Python scripts per automazione: agent_seo.py, agent_pinterest.py, import scripts
