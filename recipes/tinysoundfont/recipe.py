from os.path import join
import os
import shlex
import shutil
import subprocess

from pythonforandroid.recipe import Recipe


class TinySoundFontRecipe(Recipe):
    version = "0.9-local"
    url = None
    depends = []
    built_libraries = {"libpianosynth.so": None}

    def should_build(self, arch):
        return not self.ctx.has_lib(arch.arch, "libpianosynth.so")

    def build_arch(self, arch):
        recipe_dir = self.get_recipe_dir()
        env = self.get_recipe_env(arch)
        compiler = shlex.split(env.get("CC", "clang"))
        command = compiler + shlex.split(env.get("CFLAGS", "")) + [
            "-shared", "-fPIC", "-O3", "-std=c99",
            "-I", recipe_dir,
            join(recipe_dir, "piano_synth.c"),
            "-lm", "-o", join(recipe_dir, "libpianosynth.so"),
        ] + shlex.split(env.get("LDFLAGS", ""))
        subprocess.run(command, cwd=recipe_dir, env=env, check=True)
        output_dir = self.ctx.get_libs_dir(arch.arch)
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy2(join(recipe_dir, "libpianosynth.so"), join(output_dir, "libpianosynth.so"))


recipe = TinySoundFontRecipe()
