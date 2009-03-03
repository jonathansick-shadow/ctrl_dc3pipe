# -*- python -*-
#
# Setup our environment
#
import glob, os.path, re, os
import lsst.SConsUtils as scons

env = scons.makeEnv("dc3pipe", r"$HeadURL$")



env['IgnoreFiles'] = r"(~$|\.pyc$|^\.svn$|\.o$)"

# the "install" target
#
Alias("install", [env.Install(env['prefix'], "bin"),
                  env.Install(env['prefix'], "etc"),
                  env.Install(env['prefix'], "exposureLists"),
                  env.Install(env['prefix'], "pipeline"),
                  env.InstallEups(env['prefix'] + "/ups",
                                  glob.glob("ups/*.table"))])

scons.CleanTree(r"*~ core *.os *.o")

#
# Build TAGS files
#
files = scons.filesToTag()
if files:
    env.Command("TAGS", files, "etags -o $TARGET $SOURCES")

env.Declare()
env.Help("""
LSST package for executing DC3
""")
