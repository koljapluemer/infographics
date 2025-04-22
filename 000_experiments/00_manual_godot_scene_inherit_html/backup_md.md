---
aliases: 
created-at: 24.09.2024
q-type: 
---
# Godot Scene Instantiation Techniques

## Original Scene

![[car_default.png]]
### `car.tscn`

![[socialscreenshots-9_24_2024, 4_18_36 PM.png]]

### `car.gd`

### Duplicate

- #1
- **how?**
	- Duplicate the scene file by right-clicking it and selecting `Duplicate` or press `Ctrl+D`
	- Duplicate it to a different location by right-clicking it, selecting `Move/Duplicate To...` and choosing a target
- **what will happen?**
	- You get another scene with its own file with that is exactly the same as the original
	- Now you can change the scenes completely independently of each other
- **when and why to use this?**
	- You want to reuse some of the ideas of another scene once to make a completely new and independent scene.
- **example**
	- You duplicate `car.tscn` to make `bike.tscn`, which will have roughly the same note, but will go into a different part of your game and work completely differently.
- **note:**
	- If `Nodes` have scripts attached, they will be shared with the original scene, unless you disconnect them and create new ones.
	- When you use this to create a lot of similar scenes with this technique, you will have to manually change all of the scenes when you make a change that should affect all of them.
