# blender_data_gather

## installation
install dependencies for this addon
```
> mkdir ./libz
> cd ./libz
> mkdir ./modules
> cd ./modules
> pip install lose==1.0.0 tables==3.5.2 -t .
```
then add the `libz` folder to `Blender Preferences`->`File Paths`->`Data`->`Scripts`

install the addon through `Blender Preferences`->`Add-ons`->`Install...`->select the `gather_data.py` file

## usage
press space and search for `data grabber`, press enter

it will look like blender crashed, but it didn't, i recommend you open the console before you start it to see the progress


## what it will do
the addon will look for an object named `tracker1` in your scene to pull positional data from, make sure it exists(i recommend you make it an empty and maybe parent it to something)

save path for the data is set by blender output settings

also data sequence length is dictated by blender's animation duration settings

save data is a frame sequence synced with positional data from the tracker object

frame sequence is saved as is, positional data is save using `lose.Loser` data handler

[more on `lose`](https://github.com/okawo80085/lose)

you can do whatever with the tracker object, just don't remove it

you can also do whatever with your scene