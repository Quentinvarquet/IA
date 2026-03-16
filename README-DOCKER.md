# JSON Anonymizer - Déploiement Docker Local

## Prérequis
- Docker & Docker Compose installés

## Démarrage rapide

```bash
# Cloner le projet (si depuis GitHub)
git clone <votre-repo>
cd <votre-repo>

# Lancer tous les services
docker-compose up -d --build

# Vérifier que tout tourne
docker-compose ps
```

## Accès

| Service  | URL                      |
|----------|--------------------------|
| Frontend | http://localhost:3000    |
| Backend  | http://localhost:8001    |
| API Doc  | http://localhost:8001/docs |
| MongoDB  | localhost:27017          |

## Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes (reset DB)
docker-compose down -v

# Rebuilder après modifications
docker-compose up -d --build
```

## Configuration

### Variables d'environnement Backend
Modifiables dans `docker-compose.yml` :
- `MONGO_URL` : URL MongoDB
- `DB_NAME` : Nom de la base de données
- `CORS_ORIGINS` : Origines autorisées

### URL Backend pour Frontend
Modifier l'argument `REACT_APP_BACKEND_URL` dans `docker-compose.yml` si vous déployez sur un serveur distant.

## Structure des fichiers Docker

```
/app/
├── docker-compose.yml      # Orchestration des services
├── backend/
│   └── Dockerfile          # Image Python/FastAPI
├── frontend/
│   ├── Dockerfile          # Image Node build + Nginx
│   └── nginx.conf          # Configuration Nginx
└── README-DOCKER.md        # Ce fichier
```

## Déploiement sur serveur distant

1. Modifier `REACT_APP_BACKEND_URL` avec l'URL publique du backend
2. Modifier `CORS_ORIGINS` pour autoriser le domaine frontend
3. Configurer un reverse proxy (Traefik, Nginx) si nécessaire

```yaml
# Exemple pour serveur distant
args:
  - REACT_APP_BACKEND_URL=https://api.mondomaine.com
environment:
  - CORS_ORIGINS=https://mondomaine.com
```
