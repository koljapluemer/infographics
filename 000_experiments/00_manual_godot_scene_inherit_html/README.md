- `ln -s`'d an Obsidian note here:
    - `/home/b/MEGA/Obsidian/Zettelkasten/Thoughts/infographic﹕\ godot\ scene\ instantiation.md`
    - this end is `infographic.md`
    - with `md_to_json infographic.md  > infographic.json` we can make it JSON

- see parent README, we're cooperating with `godot-sandbox` here
- images are also just saved anywhere (assets in the godot project), not sure how to handle that
- also md isn't yet handled as md
- we have `index.html` here, which is a hard-coded mock attempt of doing the whole thing in HTML
    - does not load vue yet
    - going into dev mode in Chrome, setting target res then taking screenshot works just fine for png export. 
        - not PDF yet, but ya know, MVP


### Next Up

- write the entire content
- manage images sanely, and create all of them
- hook into a vue file
- get done
- post