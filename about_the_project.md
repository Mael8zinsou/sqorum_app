# Exportation

Parfait, là on voit clairement **le nœud du problème** : ta “V1 exportable” est aujourd’hui **couplée à Supabase + authentification** dès l’écran d’accueil. Donc tu as deux produits possibles :

1. **Produit “démo/public”** (n’importe qui ouvre, charge un CSV, obtient un scoring)
2. **Produit “SaaS”** (comptes, stockage, multi-users via Supabase)

Les deux sont valides. Mais **pas la même exportation**.

Si ton objectif immédiat = “utilisable par n’importe qui”, alors **tu dois avoir un mode “Demo / Offline”** qui ne dépend pas de Supabase. Sinon tu vas te battre avec des secrets, des comptes, et de l’infra — et tu perdras la vitesse MVP.

---

## 1) Ton `requirements.txt` : corriger maintenant

## 2) Ton `Home.py` : 2 soucis à régler

### A) `sys.path.append(...)` : c’est du bricolage (acceptable en V0), mais pas exportable proprement

Quand tu packages, ce hack devient une source d’ennuis.

**Solution propre :** transformer le repo en package installable et importer normalement.

### B) Supabase obligatoire au démarrage : ça bloque l’export “pour n’importe qui”

Aujourd’hui, sans variables d’environnement Supabase, ton app est soit inutilisable, soit casse.

---

## 3) La stratégie gagnante : “Dual mode”

Tu gardes ton SaaS (Supabase) **ET** tu ajoutes un mode démo/offline.

### Règle

* Si `SQUORUM_MODE=demo` → pas d’auth, pas de supabase, on bosse sur CSV local.
* Si `SQUORUM_MODE=saas` → auth supabase + données par user.

Tu peux même faire : *si les clés Supabase sont absentes → fallback demo*.

---

## 4) Modif concrète à faire dans `Home.py`

Idée simple : tu ne changes pas toute ton app, tu changes juste **l’entrée**.

Pseudo-structure :

* détecter le mode (`os.getenv`)
* si demo → écran “Importer CSV / Utiliser data/dataset_50…”
* sinon → ton auth supabase actuel

Tu gagnes :

* export web public sans secrets
* export offline sans DB
* tu gardes la version SaaS prête pour V2

---

## 5) Rendre “exportable” proprement : packaging du core

Tu as déjà `squorum_core/`. Nickel. Maintenant, au lieu de bidouiller `sys.path`, tu fais :

### A) Ajouter un `pyproject.toml` minimal à la racine

Objectif : pouvoir faire `pip install -e .` et importer `squorum_core` partout.

Structure :

* `squorum_core` = package
* `app` = UI (pas forcément un package)

Ensuite, dans `Home.py`, tu importes `from squorum_core...` directement.

### B) Ajouter une CLI

C’est LA feature qui rend ton moteur “exportable” même sans UI.

Exemple d’usage :

```bash
python -m squorum_core score --input data/dataset_50_partenaires.csv --output scored.csv
```

Ça te donne :

* outil utilisable par n’importe qui (même sans Streamlit)
* base future pour FastAPI, exe, automatisations…

---

## 6) Trois options d’export, dans l’ordre “ROI”

### Option 1 — Web public (le plus simple)

* Streamlit Community Cloud (démo)
* Mode demo activé par défaut
* Zéro secrets nécessaires

### Option 2 — Docker (portable + quasi-offline)

* `docker build` / `docker run`
* marche sur n’importe quelle machine avec Docker

### Option 3 — Exe (le plus chiant)

* possible mais tu vas souffrir avec Streamlit + assets + chemins
* à garder pour plus tard, quand l’UX est figée

---

## 7) Ta prochaine action (très concrète)

Tu fais ces 3 choses dans cet ordre :

1. **Ajouter un mode demo** dans `Home.py` (pas d’auth obligatoire)
2. **Stopper `sys.path.append`** via `pyproject.toml` + `pip install -e .`
3. **Ajouter une CLI minimale** dans `squorum_core`

---

## Point important (je te le dis cash)

Tant que ton app dépend de Supabase au démarrage, “exportable pour n’importe qui” = faux.
Ça marche pour toi parce que tu as ton environnement. Pas pour un utilisateur externe.

Avec un mode demo, tu transformes Squorum en vrai produit testable par tous, immédiatement.


# État de Squorum : Docker + Render / Déploiement : 

Test local avant Render
docker build -t squorum .

docker run -p 8501:8501 -e SQUORUM_MODE=demo squorum

## Déploiement Render : ordre conseillé
Push GitHub
Test Docker local
Crée un Web Service Render connecté au repo
Render détecte le Dockerfile
Mets SQUORUM_MODE=demo pour commencer
Vérifie le flow complet : Import → Scoring → Partenaires → Décisions

Render peut auto-déployer à chaque push GitHub.