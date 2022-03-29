## Exploring engine telemetry dataset

Use the tensorflow autoencoder trained on the normal (non-fault) engine data, visualize (Dash) decode errors for various types of the engine faults.

### The datasets:
http://www02.smt.ufrj.br/~offshore/mfs/page_01.html

### The vibration dashboard:

<b>Usage:</b>
```sh
python demo_sound.py
```

![sound_dash](https://user-images.githubusercontent.com/86562899/160699771-80ac6464-aa52-4648-abcc-aeb59bdfa824.gif)


### The noise dashboard:

<b>Usage:</b>
```sh
python demo_underhang.py
```

![underhang_dash](https://user-images.githubusercontent.com/86562899/160699818-ec5d59fe-e06f-46e9-a1d1-da1de3317366.gif)
