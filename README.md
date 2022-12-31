# Roguelikey

## Table of Contents
  * [Description](#description)
  * [Usage](#usage)

#### [Video Demo](https://youtu.be/oQWMZNh5Ph8)

## Description

This is the final project of [CS50p](cs50.harvard.edu/python/) for experience and recreational propourses.

I'm very interested in develop games, I like them and I thought this project could be the step I need to start.
Roguelikes is my favorite game genre, playing a lot until now and thinking "Why not build one by my self?".

This is a terminal interface roguelike game based on [this tutorial](http://rogueliketutorials.com/tutorials/tcod/v2/),
using python 3.10, numpy and libtcod.

### The diff features
Some aspects of the game I made by my self, trying something different from the tutorial:
  - 3 rooms with different shapes
    - oval
    - elliptical (circular too)
    - and rectangular (squared bruh)
  - more equiments make the game more modular
    - rings
    - helmets
  - good looking but not so colorful, looks like a modern terminal app now
  - critical hit implement
    - enemies can do more damage even player defense is high
  - more enemies
    - globin
    - hobglobin
    - golem
  - game balancing? Maybe not.

### The project
It is a caos, although this is what I made:
  - generation folder: all files related about procedural generation 
  - components folder: classes for composing, generaly with the entities
  - assets folder: self descripted
  - input_handling file: user event handling
  - action file: all entity action are coded
  - entity file: is what compose the game
  - other file: auxiliary file, to try to prevent spaghetti code
  - project file: the magic

## Usage

```console
# clone this repo
git clone https://gitlab.com/potential-garbage/cs50/roguelikey.git

# enter dir
cd roguelikey

# install requirements
pip install -r requirements.txt

# have fun!
python project.py
```
