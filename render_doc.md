# 🧠 Render, c’est quoi (version claire)

**Render = un serveur sur Internet + automatisation de déploiement**

👉 Tu lui donnes :

* ton code (GitHub)
* comment lancer ton app (Dockerfile)

👉 Il te donne :

* une **URL publique**
* une app qui tourne **24/7**
* un **redéploiement automatique** à chaque update

---

# ⚙️ Dans TON cas (Squorum)

Render va faire exactement ça :

1. Récupérer ton repo GitHub
2. Construire ton image Docker
3. Lancer ton app Streamlit
4. L’exposer sur une URL du type :

👉 `https://squorum-demo.onrender.com`

---

# 🔁 Le flow complet (important)

## Toi

Tu fais :

```bash
git push
```

## Render fait automatiquement :

1. pull du repo
2. build Docker
3. run du container
4. remplace l’ancienne version

👉 Résultat : ton app est mise à jour en ligne

---

# 🧱 Comment Render comprend ton projet

Il lit 3 choses :

## 1. Dockerfile

👉 “comment lancer ton app”

```dockerfile
CMD ["streamlit", "run", "app/Home.py", ...]
```

---

## 2. requirements.txt

👉 “ce qu’il faut installer”

---

## 3. variables d’environnement

👉 “comment configurer l’app”

Exemple :

* `SQUORUM_MODE=demo`
* `SUPABASE_URL=...`
* `SUPABASE_KEY=...`

---

# 🚀 Comment TU vas l’utiliser (pas à pas)

## 1. Push ton projet sur GitHub

Repo propre :

* Dockerfile
* requirements.txt
* code

---

## 2. Va sur Render

👉 [https://render.com](https://render.com)

* créer compte
* “New Web Service”
* connecter GitHub
* sélectionner ton repo

---

## 3. Render détecte le Dockerfile

👉 il comprend que c’est un service Docker

Tu choisis :

* type : **Web Service**
* runtime : Docker (auto)
* plan : Free

---

## 4. Ajouter les variables d’environnement

Dans Render → “Environment”

👉 minimum :

```env
SQUORUM_MODE=demo
```

👉 si SaaS :

```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## 5. Deploy

Tu cliques → Deploy

Render :

* build
* run
* te donne une URL

---

# 🔥 Résultat concret

Tu obtiens :

* une app accessible partout
* sans installer Python
* sans lancer localement
* sans config

👉 juste un lien

---

# 🧪 Ton usage réel

### Pour toi

* tester en prod
* vérifier que tout marche hors local

### Pour un jury / recruteur

* tu envoies un lien
* ils testent direct

### Pour un produit

* base SaaS déjà prête

---

# ⚠️ Les limites (important)

Plan gratuit Render :

* app qui “s’endort” (cold start)
* temps de démarrage ~30s
* ressources limitées

👉 largement suffisant pour ton projet actuel

---

# 🧠 Différence avec Streamlit Cloud

| Render            | Streamlit Cloud      |
| ----------------- | -------------------- |
| plus pro          | plus simple          |
| Docker → portable | spécifique Streamlit |
| scalable          | limité               |
| contrôle total    | rapide               |

👉 toi : **Render = meilleur choix**

---

# 🎯 Ce que tu viens de faire (niveau réel)

Sans le réaliser, tu es en train de :

* transformer un projet local → app web publique
* maîtriser Docker → compétence Data Engineer / DevOps
* déployer un produit → niveau junior/mid déjà solide

---

# 🧭 Résumé ultra simple

Render =
👉 “Je prends ton code + Docker → je le mets sur Internet → j’en fais un site”

---

# 🚀 Prochaine étape

Si tu veux, on peut maintenant faire :

👉 ton **premier déploiement Render guidé**

* check Docker
* push GitHub
* config Render
* debug live si besoin

Ou bien :

👉 écrire un **README propre de déploiement + usage Squorum**

Tu choisis.
