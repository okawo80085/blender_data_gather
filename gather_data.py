bl_info = {
    "name": "data grabber",
    "author": "okawo80085",
    "version": (0, 1, 0),
    "blender": (2, 80, 1),
    "location": "See Add-ons Preferences",
    "description": "gathers location data synced with frames from the tracker object",
    "tracker_url": "https://github.com/okawo80085/blender_data_gather",
    "category": "Development",
}

import bpy
import lose
import os
import numpy as np
import tables as t


class Gatherer(bpy.types.Operator):
    """Object data grabber"""
    bl_idname = "object.data_grabber"
    bl_label = "start data grab"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        trkr = bpy.data.objects['tracker1'] # this script looks for an object named tracker1

        fp = scene.render.filepath # get existing output path

        handler = lose.Loser(os.path.normpath(f'{fp}/ground_truth.h5'))

        handler.new_group(fmode='w', mat44=(4, 4), pos=(3,), rot_q=(4,))
        handler.new_group(atom=t.IntAtom(), frame_id=(1,))

        frames_path = '{}/frames/{}'

        print ('starting to gather data\n\nframes will be saved to "' + os.path.normpath(frames_path.format(fp, '')) + '"')

        print ('this handler will be used to save data:')
        print (handler)

        print ('starting render...\n')

        try:
            with handler:
                # sequence length is pulled from blender animation duration settings
                for i in range(scene.frame_start, scene.frame_end+1, scene.frame_step):
                    scene.frame_set(i)
                    scene.render.filepath = os.path.normpath(frames_path.format(fp, i))
                    bpy.ops.render.render(write_still=True) # render still

                    mat_temp = trkr.matrix_world
                    # save tracker data
                    handler.save(mat44=[np.array(mat_temp)], pos=[np.array(mat_temp.to_translation())], rot_q=[np.array(mat_temp.to_quaternion())], frame_id=[[i]])
                    print (f'frame {i} data saved')

        finally:
            scene.render.filepath = fp

        return {'FINISHED'}

def register():
    bpy.utils.register_class(Gatherer)


def unregister():
    bpy.utils.unregister_class(Gatherer)

if __name__ == "__main__":
    register()