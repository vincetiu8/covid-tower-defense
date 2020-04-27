# Sergeant T-Cell and the Abnormally Impressive Invasion of Illnesses

Welcome to the repository! Whether you are a coder, artist or just
someone looking to have fun making a game, you've come to the right
place.

## Table of Contents

## Playing the Game
If you just want to play the latest release of the game, go to the releases section of
the repository and download the latest release.

If you want to play the latest developmental release (where we're currently at) or no release
has been made for your operating system, press the `clone or download` button. If you don't
intend to add or help out the game, you can just download the ZIP file and extract it. If you
do intend on helping out, follow the steps below to set up the repository correctly.

### Pre-requisites
If you are running the developmental release, you need to have these things installed
on your computer:
```
python 3
├── pygame 1.9.6 (2.0.0 for OS Catalina users)
├── pytmx 3.21.7
├── numpy 1.16.2
```

You can install Python 3 from [the python website](https://www.python.org/). You need
to install the Python packages (pygame, pytmx, numpy) 
[via the command line using pip](https://www.w3schools.com/python/python_pip.asp).

Once you've cloned the repository, run `sergeant_t_cell.py` and enjoy the game!

## Working with GitHub
GitHub is a version management software, meaning it helps us work and build on the
project on separate computers. To help make changes to the repository, you need a way
to access Github from your computer. For non-coders, the easiest way to do this is
through [GitHub Desktop](https://desktop.github.com/).

### Setting up a Local Repository
To clone our remote repository onto your computer so you can edit the files, open 
Github Desktop. You should see a button called `current repository` on the top left.
Click on this, and click on the `add` button. This will bring a drop-down menu.
From the options, select `clone repository`. This will bring up a menu, defaulting 
to the page `GitHub.com`. If you can see our repository (`covid-tower-defense`), 
select that option. If you can't, press the URL header and enter  
`https://github.com/Invincibot/covid-tower-defense.git`  
into the URL textbox. Choose the local path (where the files will be downloaded) and
press clone. This should clone the remote files on our repository into your computer.

### Fetching Remote Changes
If there are any changes in the remote repository, you want to update your local
repository so you have the latest version. To do this on GitHub Desktop, press
`fetch origin`.

### Making Local Changes
If you want to edit the files or add towers, enemies or levels, you are going to be
making local changes. If you want to do this, the first thing you want to do is
open a branch. **ALWAYS REMEMBER TO MAKE A NEW BRANCH BEFORE MAKING CHANGES**.

You can make a new branch in GitHub Desktop by pressing on the `current branch`
header. This will bring up a list of branches. Before making a new branch, you want
to fetch remote changes and then checkout the branch you want to base your new branch
on. Normally, you want to base changes on the `dev` branch, which has the latest
updates, so checkout this one. Then, press make a new branch and select `dev` when it
asks you which branch you want to make it off from. Once you have created your new
branch, you're ready to make changes!

### Committing Changes
After you have made some changes to the files or added some enemies, towers or
levels, you want to commit these changes to your branch. This means making a 'save' of
what you have done so far. On GitHub Desktop, you can do this by clicking on the `changes`
button on the left side of the screen. Then, select all the files which you want to 
save changes from. At the bottom left, you can see a small box with a title and a
description. In the title, enter the title of your changes, like `Add new tower` or
`Fix bugs`. In the description, give a short description of the changes you've made,
like `This commit adds a new tower, called the phagocyte, into the game.` Once you're happy
with the title and description, press the commit button at the bottom.

### Pushing Changes
Once you've made some changes, you ideally want to 'push' them back to the remote
repository. This will save them there, so even if your computer gets wiped the changes
will still be saved. First, you want to commit any changes. Then, you will see the
`fetch origin` button will change to the `push changes` button. Click on this and it
will push your changes.

### Making an Issue
Perhaps there's a feature you'd like in the game or a bug you need to report. In this
case, you should make an issue on the repository on GitHub. Navigate to the `issues` page
and press `create issue`. In the issue, describe what problem/feature you are encountering
and any suggestions you have for its implementation. Tag this with the appropriate tags:
`bug` for bugs or problems, `enhancement` for important changes, `nice to have` for smaller, 
not so important changes.

### Pull Requests
If you're happy with all the changes you've made on your new branch and want to merge
them into the main code, you need to open a 'pull request' on GitHub. Go online to the
repository and go to the `pull requests` page. If you've recently pushed a branch, there
should be a yellow bar with your branch's name and a green button with the sign
`new pull request`. Click on this. If you don't see a bar, click on the `new pull request`
button on the screen. Then change the 'base' to `dev` or whatever branch you want to merge
to and 'compare' to your current branch.

Once you've done this, you should be brought to a different screen. There should be a box
to enter a title and a description of the pull request. This should be straightforward. In
the description, enter any hashes of issues your pull request is solving (if any) and then
press `create pull request`. This creates a pull request for your changes.

And now, wait. Other people will come and review the changes you've made to the
repository. **DON'T PULL YOUR OWN PULL REQUEST. WAIT FOR SOMEONE TO CHECK IT FIRST**.
They may suggest changes that you need to make before the branch is pulled in,
or pull the branch. Once they've pulled the branch, congrats! Your changes have been
successfully merged!

## Using the Game's Developer Tools
The game currently has built-in developer tools to allow non-coders to make enemies and
towers.

Enemy and tower names must follow snake case. This means no spaces between words and
no capital letters. In our case, punctuation is not allowed either. Words are separated by `_` instead. For example:
```
sergeant_t_cell
python_3
foo_bar
```
are all valid examples of snake case. Wrong examples are:  
```
Virus  
coding is fun
oh, you're approaching me?
```  

### Making an Enemy
An enemy in the game tries to get past the player's defenses and reach the goal, where
it will cause the player to lose a certain amount of lives.

Say you want to add an enemy to the game. Let's call this tower the
'virus'. The first thing you want to do is create all the necessary
assets for the virus. These are:
- An image
    You need to name the enemy's image by the format:
    `(enemy name).png`
    where _enemy name_ is the name of the enemy. For the 'virus'm this should be named
    `virus.png`
    >This image shouldn't be larger than 40 x 40 pixels. Note, all images must be of the file format .png. 

- A sound effect when it dies  
    You need to name the sound effect by the format:  
    `(enemy name).wav`,
    where _enemy name_ is the name of the tower. For the 'virus', the sound effect
    should be named `virus.wav`.
    
    >The sound effect should be of the format .wav and ideally be shorter than 0.2 seconds long.

Once you have all of these assets, you're ready to add the tower
in-game!

First, we need to add these assets into the correct folders. They should be added in:
```
.
├── data
    ├── audio
        ├── enemies
            (add the enemy sound effect here)
    ├── img
        ├── enemies
            (add the enemy image here)
```

Once we've moved the assets to the correct folders, run `sergeant_t_cell.py` in the
base folder. This will launch the game. Once in the game, in the Menu click on the
`Enemy Preview` button. This will open up the enemy preview screen. At the very top,
there will be a text box with the text `enemy name...`. Enter the enemy name into this
box. For the 'virus', simply enter `virus` and press the `create enemy` button. This
will load the enemy into the game.

Once the enemy has been loaded, its in-game attributes can be edited by using the
buttons in the enemy preview menu. Once you are happy with how the enemy functions,
click `save settings` at the bottom of the screen. Once you have saved these settings,
you can exit the game and push your changes to Github for others to review.

### Making a Tower
A tower in the game tries to stop enemies from reaching the goal,
normally by shooting then with something. Each tower has 3 levels and
paying the upgrade cost allows the user to upgrade the tower to its
next level. Each tower has a base (something that stays stationary) and
a gun (something that rotates to target enemies). All towers also play
a sound whenever they shoot.

Say you want to add a tower to the game. Let's call this tower the
'phagocyte'. The first thing you want to do is create all the necessary
assets for the phagocyte. These are:
- A base image (one for each level)  
    You need to name the base images by the format:  
    `(tower name)_base(level).png`,   
    where _tower name_ is the name of the tower and _level_ is the tower's level 
    (0, 1 or 2). For the 'phagocyte', the level 0 base image should be named
    `phagocyte_base0.png`, the level 1 base image should be named `phagocyte_base1.png` 
    and so on for the level 2 base image.

    > The base images should be of the size 42 x 42 pixels. There can be transparent
    pixels, however, it should aim to cover most of the square.

- A gun image (one for each level)
    You need to name the gun images by the format:  
    `(tower name)_gun(level).png`,  
    where _tower name_ is the name of the tower and _level_ is the tower's level
    (0, 1 or 2), similar to the base image. For the 'phagocyte', the level 0 gun
    image should be named `phagocyte_gun0.png`, the level 1 base image should be 
    named `phagocyte_gun1.png` and so on for the level 2 gun image.

    >The gun images should also be of the size 42 x 42 pixels. They will rotate around
    the center of the image, so make sure the center of the gun is at the center of
    the image.

    >Note, all images must be of the file format .png. 

- A sound effect when it shoots  
    You need to name the sound effect by the format:  
    `(tower name).wav`,
    where _tower name_ is the name of the tower. For the 'phagocyte', the sound effect
    should be named `phagocyte.wav`.
    
    >The sound effect will be the same for all levels of the tower. It should be of the
    format .wav and ideally be shorter than 0.2 seconds long.

Once you have all of these assets, you're ready to add the tower
in-game!

First, we need to add these assets into the correct folders. They should be added in:
```
.
├── data
    ├── audio
        ├── towers
            (add the tower sound effect here)
    ├── img
        ├── towers
            (add all the base and gun images here)
```

Once we've moved the assets to the correct folders, run `sergeant_t_cell.py` in the
base folder. This will launch the game. Once in the game, in the Menu click on the
`Tower Preview` button. This will open up the tower preview screen. At the very top,
there will be a text box with the text `tower name...`. Enter the tower name into this
box. For the 'phagocyte', simply enter `phagocyte` and press the `create tower` button. This
will load the tower into the game.

Once the tower has been loaded, its in-game attributes can be edited by using the
buttons in the tower preview menu. Once you are happy with how the tower functions,
click `save settings` at the bottom of the screen. Once you have saved these settings,
you can exit the game and push your changes to Github for others to review.

## Building the Game
For coders, in order to make a production-ready version of the game, we need to
'build' it. The process is different for different platforms:

How to create the .exe for Windows:
1. Install pyinstaller
2. Navigate to the download folder with `sergeant_t_cell.py`
3. Run the command:
`pyinstaller --onefile -w --add-data 'data;data' sergeant_t_cell.py`
4. This will create a folder called `dist` among other folders.  
Open this folder to get the exe.
5. Enjoy the game!
