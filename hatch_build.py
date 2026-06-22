import os
import shutil
from typing import Any
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

RELEASE_FOLDERS = []

RELEASE_FILES = [
    "run.bat",
]

class CustomBuildHook(BuildHookInterface):

    def initialize(self, version, build_data):
        for folder in RELEASE_FOLDERS:
            input_folder = os.path.join(self.root, folder)
            output_folder = os.path.join(self.directory, folder)
            shutil.copytree(input_folder, output_folder, dirs_exist_ok=True)

        for file in RELEASE_FILES:
            input_path = os.path.join(self.root, file)
            output_path = os.path.join(self.directory, file)
            shutil.copy(input_path, output_path)
        super().initialize(version, build_data=build_data)

    def finalize(
        self, version: str, build_data: dict[str, Any], artifact_path: str
    ) -> None:
        super().finalize(version, build_data, artifact_path)
        dist_dir = os.path.join(self.root, "dist")
        zip_name = f"image_viewer_{self.build_config.builder.metadata.version}"
        zip_full_path = os.path.join(self.root,"release", zip_name)

        if os.path.exists(dist_dir) and os.listdir(dist_dir):
            print(f"Creating archive: {zip_name}.zip from {dist_dir}")

            shutil.make_archive(
                base_name=zip_full_path, format="zip", root_dir=dist_dir
            )
