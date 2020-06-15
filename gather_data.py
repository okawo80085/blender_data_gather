import bpy
import lose
import os
import numpy as np

scene = bpy.context.scene
trkr = bpy.data.objects['tracker1'] # this script looks for an object named tracker1

fp = scene.render.filepath # get existing output path

handler = lose.Loser(os.path.normpath(f'{fp}/ground_truth.h5'))

handler.new_group(fmode='w', mat44=(4, 4), pos=(3,), rot_q=(4,), frame_id=(1,))


max_frames = 80 # number of frames to render, you may wanna change this

frames_path = '{}/frames/{}'

print ('starting to gather data\n\nframes will be saved to "' + os.path.normpath(frames_path.format(fp, '')) + '"')

print ('this handler will be used to save data:')
print (handler)

print ('starting render...\n')

with handler:
    for i in range(max_frames):
        scene.frame_set(i)
        scene.render.filepath = os.path.normpath(frames_path.format(fp, i))
        bpy.ops.render.render(write_still=True) # render still

        mat_temp = trkr.matrix_world
        # save tracker data
        handler.save(mat44=[np.array(mat_temp)], pos=[np.array(mat_temp.to_translation())], rot_q=[np.array(mat_temp.to_quaternion())], frame_id=[[i]])
        print (f'frame {i} data saved')

scene.render.filepath = fp