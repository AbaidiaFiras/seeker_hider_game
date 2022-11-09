# Hider and Seeker game using Reinforcement learning stable baseline3
Ce projet représente une implémentation du jeu hider and seeker (cache-cache) en utilisant Reinforcement learning. Il est composé principalement de 4 fichiers:
* **hide_seek_env.py:** qui est nécessaire pour créer notre environnement personnalisé "custom env", ce fichier contient les méthodes nécessaires pour notre jeu  et l'environnement qui est la classe ```class hasEnv(gym.Env)```.
* **checkenv.py:** permet de vérifier l'environnement personnalisé "custom env" et afficher des avertissements supplémentaires si trouvés.
* **doublecheck_env.py:** permet de s'assurer que les récompenses semblent correctes, que les épisodes se terminent et que le processus redémarre comme prévu. 
* **hide_seek_learn.py:** pour former notre modèle RL et permettre à notre agent "Hider" de se cacher. 
# Tech/Framework Utilisé
* **Stable baseline3 Framework:**
  Stable-Baselines3 (SB3) est une bibliothèque fournissant des implémentations fiables d'algorithmes d'apprentissage par renforcement qui sont basés sur OpenAI Baselines.. 
* **GYM Framework:**
  est une bibliothèque Python open source pour développer et comparer des algorithmes d'apprentissage par renforcement en fournissant une API standard pour communiquer entre les algorithmes d'apprentissage et les environnements, ainsi qu'un ensemble standard d'environnements conformes à cette API.
* **Pygame :**
  est un module qui offre des outils permettant de créer des jeux. Le module est lui-même subdivisé en plusieurs sous-modules, ce qui permet de ne pas appeler des modules qui seraient inutiles.
* **Turtle library:**
"Turtle" est une fonction Python comme une planche à dessin, qui nous permet de commander une tortue pour qu'elle dessine partout. Lors de ce projet, on l'a utliser pour dessiner la matrice (12x12).
 
# To run my model
## 1.Environnement d'exécution 
xxxxx
## 2.Préparer et vérifier l'environnement personnalisé (custom env)
Pour commencer, notre environnement personnalisé (custom env qui est ```class hasEnv(gym.Env)```) est préparé dans hide_seek_env.py, on doit s'assurer de son fonctionnement avant de l'introduire au gym. Il suffit alors d'exécuter ce code, qui utilise une méthode de Stable Baseline3 SB3 dédié pour le test d'environnement: 
```bash
python checkenv.py
```
A cette étape, on doit voir l'interface  de l'environnement et, espérons-le, aucune erreur.
Mais avant de passer à former notre modèle pour apprendre à se cacher, une vérification supplémentaire est nécessaire. Celle ci va permettre de s'assurer que les récompenses (reward) semblent correctes, que les épisodes se terminent et que le processus redémarre comme prévu. 
```bash
python doublecheckenv.py
```
## 3.Formation du modèle 
Il est temps d'essayer de former un modèle. En effet la bibliothèque stable-baslines contient de nombreux algorithmes d'apprentissage par renforcement différents.
Nous avons choisi PPO Proximal Policy Optimization, mais vous pouvez facilement changer l'algorithme  par un autre algorithme RL proposé par [stable-baselines3 zoo](https://stable-baselines3.readthedocs.io/en/master/guide/rl_zoo.html). 


```bash
python hide_seek_learn.py
```
