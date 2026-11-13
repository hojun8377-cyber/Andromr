from os.path import join, isfile
import os
import shlex
import subprocess

from pythonforandroid.recipe import Recipe


class TinySoundFontRecipe(Recipe):
    version = "0.9-local"
    url = None
    depends = []
    archs = ["arm64-v8a"]
    built_libraries = {"libpianosynth.so": None}

    def should_build(self, arch):
        return not isfile(join(self.get_build_dir(arch.arch), "libpianosynth.so"))

    def build_arch(self, arch):
        recipe_dir = self.get_recipe_dir()
        build_dir = self.get_build_dir(arch.arch)
        os.makedirs(build_dir, exist_ok=True)
        env = self.get_recipe_env(arch)
        compiler = shlex.split(env.get("CC", "clang"))
        output = join(build_dir, "libpianosynth.so")
        command = compiler + shlex.split(env.get("CFLAGS", "")) + [
            "-shared", "-fPIC", "-O3", "-std=c99",
            "-I", recipe_dir,
            join(recipe_dir, "piano_synth.c"),
            "-lm", "-o", output,
        ] + shlex.split(env.get("LDFLAGS", ""))
        subprocess.run(command, cwd=recipe_dir, env=env, check=True)


recipe = TinySoundFontRecipe()
