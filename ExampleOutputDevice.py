# Copyright (c) 2017 Ultimaker B.V.
# This example is released under the terms of the AGPLv3 or higher.

import os.path #To get a file name to write to.
import zipfile #To write to zip files.

from UM.Application import Application #To find the scene to get the current g-code to write.
from UM.FileHandler.WriteFileJob import WriteFileJob #To serialise nodes to text.
from UM.Logger import Logger
from UM.OutputDevice.OutputDevice import OutputDevice #An interface to implement.
from UM.OutputDevice.OutputDeviceError import WriteRequestFailedError #For when something goes wrong.
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin #The class we need to extend.

class ExampleOutputDevicePlugin(OutputDevicePlugin): #We need to be an OutputDevicePlugin for the plug-in system.
    ##  Called upon launch.
    #
    #   You can use this to make a connection to the device or service, and
    #   register the output device to be displayed to the user.
    def start(self):
        self.getOutputDeviceManager().addOutputDevice(ExampleOutputDevice()) #Since this class is also an output device, we can just register ourselves.

    ##  Called upon closing.
    #
    #   You can use this to break the connection with the device or service, and
    #   you should unregister the output device to be displayed to the user.
    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("example_output_device")

class ExampleOutputDevice(OutputDevice): #We need an actual device to do the writing.
    def __init__(self):
        super().__init__("example_output_device") #Give an ID which is used to refer to the output device.

        #Optionally set some metadata.
        self.setName("Example Output Device") #Human-readable name (you may want to internationalise this). Gets put in messages and such.
        self.setShortDescription("Save Example") #This is put on the save button.
        self.setDescription("Save Example")
        self.setIconName("save")

    ##  Called when the user clicks on the button to save to this device.
    #
    #   The primary function of this should be to select the correct file writer
    #   and file format to write to.
    #
    #   \param nodes A list of scene nodes to write to the file. This may be one
    #   or multiple nodes. For instance, if the user selects a couple of nodes
    #   to write it may have only those nodes. If the user wants the entire
    #   scene to be written, it will be the root node. For the most part this is
    #   not your concern, just pass this to the correct file writer.
    #   \param file_name A name for the print job, if available. If no such name
    #   is available but you still need a name in the device, your plug-in is
    #   expected to come up with a name. You could try `uuid.uuid4()`.
    #   \param limit_mimetypes Limit the possible MIME types to use to serialise
    #   the data. If None, no limits are imposed.
    #   \param file_handler What file handler to get the mesh from.
    #   \kwargs Some extra parameters may be passed here if other plug-ins know
    #   for certain that they are talking to your plug-in, not to some other
    #   output device.
    def requestWrite(self, nodes, file_name = None, limit_mimetypes = None, file_handler = None, **kwargs):
        #The file handler is an object that provides serialisation of file types.
        #There's several types of files. If not provided, it is assumed that we want to save meshes.
        if not file_handler:
            file_handler = Application.getInstance().getMeshFileHandler()
        file_types = file_handler.getSupportedFileTypesWrite()
        if not file_types:
            Logger.log("e", "No supported file types for writing.")
        file_type = file_types[0] #For this example, we'll just pick an arbitrary file type. Normally you may want to choose the device's preferred type or let the user choose.
        file_writer = file_handler.getWriterByMimeType(file_type["mime_type"]) #This is the object that will serialize our file for us.
        if not file_writer:
            raise WriteRequestFailedError("Can't find any file writer for the file type {file_type}.".format(file_type = file_type))

        #For this example, we will write to a file in a fixed location.
        output_file_name = os.path.expanduser("~/output.txt")
        file_stream = open(output_file_name, "w")
        job = WriteFileJob(file_writer, file_stream, nodes, file_type["mode"]) #We'll create a WriteFileJob, which gets run asynchronously in the background.

        job.progress.connect(self._onProgress) #You can listen to the event for when it's done and when it's progressing.
        job.finished.connect(self._onFinished) #This way we can properly close the file stream.

        job.start()

    def _onProgress(self, job, progress):
        Logger.log("d", "Saving file... {progress}%".format(progress = progress))

    def _onFinished(self, job):
        job.getStream().close()
        Logger.log("d", "Done saving file!")