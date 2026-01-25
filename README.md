# P9 : Développer une application web en utilisant Django - Projet LITRevu

## 📖 Description

Ce projet est un **site web Django** permettant à une communauté d'utilisateurs de publier des critiques
de livres ou d’articles et de consulter ou de solliciter une critique à la demande.  

---

## ✨Fonctionnalités

Un visiteur non connecté peut : 
- s'inscrire ;
- se connecter.

Un utilisateur connecté peut :
- consulter son flux contenant les derniers billets et les critiques des utilisateurs qu’il suit, 
classés par ordre antéchronologique ;
- créer de nouveaux billets pour demander des critiques sur un livre ou un article ;
- créer de nouvelles critiques en réponse à des billets ;
- créer un billet et une critique sur ce même billet en une seule étape ;
- voir, modifier et supprimer ses propres billets et critiques ;
- suivre les autres utilisateurs en entrant leur nom d'utilisateur ;
- voir qui il suit et suivre qui il veut ;
- arrêter de suivre un utilisateur.

---

## 🏗️ Organisation du projet

Le projet repose sur un projet Django de configuration, `litrevu`, qui centralise les paramètres globaux de l’application.  
La logique fonctionnelle est répartie dans deux applications distinctes :

- `authentication` : gère l’inscription, la connexion et l’authentification des utilisateurs.
- `reviews` : gère les critiques de livres et d’articles, ainsi que les abonnements entre utilisateurs et les interactions associées.

---

## 🛠️ Pré-requis

Avant de commencer, assurez-vous d'utiliser les versions suivantes de Python et pip :
- **Python 3.14**  
- **pip 25.3**

---

## 💻 Installation

### 1. **Clonez le dépôt** sur votre machine locale :

```
git clone https://github.com/myriamdesporte/P9.git
```

### 2. **Créez un environnement virtuel** :

Assurez-vous d'être dans le dossier racine du projet:

```
cd P9
```

puis

```
python -m venv env
```

### 3. **Activez l'environnement virtuel** :

- Sur Linux/macOS :
  ```
  source env/bin/activate
  ```
- Sur Windows :
  ```
  .\env\Scripts\activate
  ```

### 4. **Installez les dépendances** à partir du fichier `requirements.txt`:

```
pip install -r requirements.txt
```

Les dépendances principales incluent notamment `Django`, `flake8` et `Pillow`.

### 5. **Configurez la base de données** :

> 💡 **Bonnes pratiques :** Ici le fichier `db.sqlite3` est fourni comme spécifié dans le cahier des charges,
> pour faciliter l’installation locale, mais en général, on ne versionne pas la base de données.

Pour créer les fichiers de migration à partir des modèles Django :
```
python manage.py makemigrations
```

Pour appliquer les migrations et crée les tables dans SQLite :
```
python manage.py migrate
```

---

## 🚀 Lancer le serveur Django

```
python manage.py runserver
```
Le site sera accessible à l’adresse : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🛡️ Accès à l’interface d’administration

Django fournit une interface d’administration prête à l’emploi pour gérer le contenu et les utilisateurs du site.

Pour créer un super utilisateur (compte administrateur) :

```
python manage.py createsuperuser
```

Une fois le compte créé, l’interface d’administration est accessible à l’adresse : 
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ✅ Vérification du code avec Flake8

Ce projet utilise `flake8` pour vérifier la conformité du code à la norme **PEP8**.

Un rapport HTML est généré automatiquement à chaque exécution de la commande `flake8 .` et disponible 
dans le dossier `flake8_report/`.