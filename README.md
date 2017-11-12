Example Output Device
=====================

This is an example output device plug-in for Uranium. Uranium is the underlying framework used in Ultimaker Cura.

Output devices are meant to communicate with a place where the output of the application can be stored. For instance, an export of the model or a result of computation.

An output device plug-in starts with a `start()` method and stops with a `stop()` method. This allows you to make a connection with your device while in the loading screen. This should then add one or more `OutputDevice` instances. For instance, a plug-in could continuously listen for incoming internet connections and add an output device whenever a new connection is made.

The actual output device finds the desired file type to write with, and then provides that file type's file writer with a stream that it can write to. The file writer does the rest.

Packaging
---------

To create a plugin you can create a ZIP file from your complete plugin directory and rename it to use a .umplugin or .curaplugin extension.
