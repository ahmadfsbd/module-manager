#Pre-reqs
Before running the script you need to mount the /software from the farm onto a location in your VM.

#How to
Run `bash softpack-to-tre.sh <path to the singularity.sif>`

This will create a new folder in library red with an appropriate name, which will be populated with the singularity.sif file itself,
and a newly created meta.yaml file containing the packages and executables. Once the command completes you should be able to use
the module from inside module-manager.


