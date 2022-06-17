
## DEVOPS - TP3 - DOCKER
## ARTHUR ALLIE - EFREI - M1 BDIA APP

### Rappel des objectifs de ce TP : 
- Déployer sur Azure Container Instance (ACI) using Github Actions
- Mettre à disposition son image (format API) sur Azure Container Registry (ACR) using Github Actions
- Mettre à disposition son code dans un repository Github

---

-- Repository GitHub associé à mon TP : 
https://github.com/efrei-devops-apprentis-bdml/tp3-arthur-allie

---

### Solutions techniques employées : 
Pour réaliser ce travail, j'ai utilisé le langage de programmation ***Python***. 
Afin de requêter une API, j'ai utilisé en plus de Python le micro framework dédié ***Flask***.
L'OS que j'utilise est ***Windows 10***, avec le CLI ***WSL2***, de manière à bénéficier de certaines commandes Unix.

---

### Travail réalisé étape par étape : 

### 1. Installations préliminaires (facultatif) : 
- #### Je commence par créer un répertoire de projet en local, que je nomme *docker-devops-tp3*:
````bash
$ cd ../..
$ cd Users/arthu/Efrei/DEVOPS
$ mkdir docker-devops-tp3
$ cd docker-devops-tp3
````

- *Je crée ensuite un environnement virtuel *myvenv* au sein de ce répertoire projet; cela me permettra d'installer toutes les librairies dont j'aurai besoin ultérieurement, tout en isolant mon application d'un point de vue code. En effet, en procédédant ainsi, les versions des librairies que j'installerai dans mon environnement virtuel seront toujours disponibles au sein de cet environnement, ce qui m'assurera que mon code fonctionnera toujours correctement en son sein :* 
````bash
$ python3 -m venv myvenv
````

- #### Activation de l'environnement virtuel *myvenv* : 
````bash
$ source myvenv/bin/activate
````
-> *Ce qui donne :* 
````bash
(myvenv) toto@DESKTOP-OBTCMJQ:/mnt/c/Users/arthu/Efrei/DEVOPS/docker-devops-tp3$
````
*A présent, je lancerai toujours de nouvelles commandes à partir de cet environnement virtuel.*

---

### 2. Création d'un nouveau répertoire de projet dans le groupe d'organisation GitHub de l'Efrei: 
##### - Se rendre sur https://github.com/efrei-devops-apprentis-bdml : 
##### - *-> "New"* -> *"tp3-arthur-allie"* 
*-> Mon projet est maintenant accessible à l'adresse suivante : https://github.com/efrei-devops-apprentis-bdml/tp3-arthur-allie*
##### - Je crée les fichiers suivants : *"Dockerfile"*, *"main.py"*, *"requirements.txt"*
  *-> Le fichier "main.py" contient la configuration de mon API*
  *-> En pratique, j'ai cloné et déposé ces fichiers depuis le repository suivant : https://github.com/efrei-devops-apprentis-bdml/vincent-domingues-tp2*

- #### Configurer le GitHub Actions workflow :
##### - Enable GitHub Container Registry : *Cliquer sur "Profile"* -> *"Feature Preview"* -> *"Improved Container Support"* -> *"Enable"*
##### - Retourner sur le repository du projet : https://github.com/efrei-devops-apprentis-bdml/tp3-arthur-allie
##### - Aller dans l'onglet *"Actions"* du menu principal, puis *"set up a workflow as yourself"*
*-> Cela me permet de modifier le contenu du fichier **"main.yml"** : https://github.com/efrei-devops-apprentis-bdml/tp3-arthur-allie/blob/main/.github/workflows/main.yml*
##### - Je consulte ensuite la documentation Microsoft pour configurer ce fichier : https://docs.microsoft.com/en-us/azure/container-instances/container-instances-github-action
  ##### - J'y inscris le code suivant : 
````bash
name: GitAction - Azure CI

on:
  push:
    branches: [ main ]

jobs:
  push_to_registry:
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3
          
      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: 'Build and push image'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker build . -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210311:latest
          docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210311:latest
      
      - name: 'Deploy to Azure Container Instances'
        uses: 'azure/aci-deploy@v1'
        with:
          resource-group: ${{ secrets.RESOURCE_GROUP }}
          dns-name-label: devops-20210311
          image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210245:latest
          registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          registry-username: ${{ secrets.REGISTRY_USERNAME }}
          registry-password: ${{ secrets.REGISTRY_PASSWORD }}
          environment-variables: API_KEY=${{ secrets.API_KEY }}
          name: '20210311'
          location: 'france central'
````
##### - Cliquer sur *"Start commit"* puis *"Commit new file"*
*-> Dans ce fichier, le paramètre "API_KEY" doit être renseigné dans mes "secrets" : je dois récupérer ma clé d'API générée sur openweather*
*-> Il faut aussi renseigner ses identifiants EFREI dans les paramètres : **"docker build ."** , **"docker push"**, **"dns-name-label"** et **"name"** (cf ci-dessus)*
*-> **location: 'france central'***


- #### Ajout de cet identifiant comme secrets dans l'interface utilisateur des secrets de GitHub :
##### - Se rendre sur https://github.com/efrei-devops-apprentis-bdml/tp3-arthur-allie : 
##### - Aller dans : *"Settings"* -> *"Secrets"* -> *"Actions"* -> *"New repository secret"*
##### *-> Ici, je renseigne un "secret" :* 
*-> Name : **"API_KEY"**, Value : **"68e3a32******"** (API KEY provenant d'openweather)
	*-> Je termine en cliquant sur **"Add secret".***


- #### Modification de mon fichier "Dockerfile" :
##### - Dans mon fichier **"Dockerfile"**, je renseigne le paramètre de port **"Expose"** : 
````bash
FROM python:3.11.0a7-alpine3.15

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python3", "main.py"]
````
*-> Je renseigne le numéro de port auquel je veux me connecter : **EXPOSE 80***

- #### Modification de mon fichier "main.py" :
##### - Dans mon fichier **"main.py"**, je  renseigne les paramètres *"host"* et *"port"* de l'*"app.run"* : 
````python
import os
import requests
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from marshmallow import Schema, fields

class WeatherQuerySchema(Schema):
	key1 = fields.Str(required=True)
	key2 = fields.Str(required=True)

app = Flask(__name__)
api = Api(app)
schema = WeatherQuerySchema()

api_key = os.environ['API_KEY']


class Weather(Resource):
	def get(self):
		errors = schema.validate(request.args)
		print(request.args)
		url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" % (request.args['lat'], request.args['lon'], api_key)
		response = requests.get(url)
		data = json.loads(response.text)
		return data

api.add_resource(Weather, '/')

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=80)
````
*-> Je renseigne le numéro de port auquel je veux me connecter : **port=80***


-> *Après avoir ajouté cet API KEY dans mes secrets et modifié mes fichiers **Dockerfile** et **main.py**, mon image a bien été envoyée sur le portal Azure, à l'adresse suivante : https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.ContainerInstance%2FcontainerGroups*
-> *Les différentes étapes de ce processus d'envoi sont :*
- Set up job
- Check out the repo
- Login via Azure CLI
- Build and push image
- Run docker build .t ***/20210311:latest
- Deploy to Azure Container Instances
- Post Check out the repo
- Complete job

----

### 3. Vérification de la création de la ressource sur le portal Azure : 
##### - Aller sur https://portal.azure.com/#home 
##### - Puis aller dans : *"settings"* -> *"Filtre d’abonnement par défaut"* -> *"Efrei - Apprentis BDML"*
##### - Chercher *"Instances de conteneur"* dans la barre de recherche -> connexion au groupe de ressources "devops-TP3"

*-> Ma ressource a bien été crée dans cet environnement Azure.*

----

### 4. API qui renvoie la météo :
##### - Dans ma CLI WSL2, je tape la commande suivante : 
````bash
curl "http://devops-20210311.francecentral.azurecontainer.io/?lat=5.902785&lon=102.754175"
````
*-> Je récupère le résultat suivant :*
````bash
{
    "coord": {
        "lon": 102.7542,
        "lat": 5.9028
    },
    "weather": [
        {
            "id": 501,
            "main": "Rain",
            "description": "moderate rain",
            "icon": "10n"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 300.54,
        "feels_like": 302.99,
        "temp_min": 300.54,
        "temp_max": 300.54,
        "pressure": 1009,
        "humidity": 73,
        "sea_level": 1009,
        "grnd_level": 982
    },
    "visibility": 10000,
    "wind": {
        "speed": 4.24,
        "deg": 118,
        "gust": 4.58
    },
    "rain": {
        "1h": 1.68
    },
    "clouds": {
        "all": 99
    },
    "dt": 1655465527,
    "sys": {
        "country": "MY",
        "sunrise": 1655420157,
        "sunset": 1655465023
    },
    "timezone": 28800,
    "id": 1736405,
    "name": "Jertih",
    "cod": 200
}
````

----

### Intérêt d'un tel travail : 

-   Bénéficier du versioning de GitHub et de sa puissance
-   Automatisation des process et du workfow via GitHub Actions : on peut créer, tester et déployer son code directement depuis GitHub, sans soucis de configurations et de lignes de commandes supplémentaires ultérieures.
-   Travail collaboratif, avec les revues de code, la gestion des branches et la gestion fluide des erreurs

----

### Bonus : 
### 1. Add hadolint to GitHub workflow : 
##### - Dans mon fichier *"main.yml"*, j'ajoute les lignes de commandes suivantes : 
````bash
      -
        uses: hadolint/hadolint-action@v2.0.0
        with:
          dockerfile: Dockerfile          
````
 *-> Ce fichier devient :*
  ````bash
name: GitAction - Azure CI

on:
  push:
    branches: [ main ]

jobs:
  push_to_registry:
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3

      -
        uses: hadolint/hadolint-action@v2.0.0
        with:
          dockerfile: Dockerfile
          
      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: 'Build and push image'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker build . -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210311:latest
          docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210311:latest
      
      - name: 'Deploy to Azure Container Instances'
        uses: 'azure/aci-deploy@v1'
        with:
          resource-group: ${{ secrets.RESOURCE_GROUP }}
          dns-name-label: devops-20210311
          image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210245:latest
          registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          registry-username: ${{ secrets.REGISTRY_USERNAME }}
          registry-password: ${{ secrets.REGISTRY_PASSWORD }}
          environment-variables: API_KEY=${{ secrets.API_KEY }}
          name: '20210311'
          location: 'france central'
````
*-> Ceci me permet :*
- De vérifier que mon **Dockerfile** est correctement rédigé (respect des bonnes pratiques)
- Ceci se vérifie avec l'ajout de la ligne ***"Run hadolint/hadolint-action@v2.0.0"*** dans les étapes d'envoi du GitHub Action workflow

----

### 2. Configurer une probe liveness HTTP : 
##### - J'ajoute un un nouveau fichier .yml, *"probe.yml"*, cette fois-ci à la racine de mon repository : 
````bash
apiVersion: 2022-06-17
location: 'france central'
name: livenesstest
properties:
  containers:
  - name: 20210311
    properties:
      image: efreidevops.azurecr.io/20210311:v1
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 1.5
      livenessProbe:
        httpGet:
          path: /health
        periodSeconds: 5
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
tags: null
type: Microsoft.ContainerInstance/containerGroups
````
*-> Je personnalise notamment les champs **"location"**, **"name"** et **"image"**, de manière analogue au fichier main.yml (voir ci-dessus), en m'aidant de la documentation microsoft : https://docs.microsoft.com/en-us/azure/container-instances/container-instances-liveness-probe*

*-> Je configure la *"probe liveness"* avec le paramètre **"periodSeconds"**, de façon à ce qu'elle s'exécute toutes les 5 secondes.*

##### - A la fin du fichier  _“main.yml”_, j'ajoute les lignes suivantes :
````bash
azcliversion: 2.30.0
inlineScript: |
  az container create --resource-group ${{ secrets.RESOURCE_GROUP }} --image ${{ secrets.REGISTRY_LOGIN_SERVER }}/20210311:v1 --dns-name-label devops-20210311 --registry-login-server ${{ secrets.REGISTRY_LOGIN_SERVER }} --registry-username ${{ secrets.REGISTRY_USERNAME }} --registry-password ${{ secrets.REGISTRY_PASSWORD }} --secure-environment-variables API_KEY=${{ secrets.API_KEY }} --location 'france central' --ports 80 -f probe.yml
          
````

*-> Ceci me permet de : m'assurer que la reprise d'un conteneur par un autre conteneur se fera correctement si ce premier conteneur ne fonctionne plus.*
*-> Ici, le problème suivant se pose : Azure CLI ne me permet pas d'enregistrer les différents secrets ci-dessus dans mon repository Github.*
