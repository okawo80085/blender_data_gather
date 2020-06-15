# blender_data_gather

to use this script with blender add the `blender_scripts` folder path as a the `Scripts` path in blender preferences

then switch to scripting layout and open the `gather_data.py` script

the script will look for an object named `tracker1` in your scene to pull positional data from, make sure it exists(i recommend you make it an empty and maybe parent it to something)

save path for the data is set by blender output settings

save data is a frame sequence synced with positional data from the tracker object

frame sequence is saved as is, positional data is save using `lose.Loser` data handler

[more on `lose`](https://github.com/okawo80085/lose)

you can do whatever with the tracker object, just don't remove it

you can also do whatever with your scene