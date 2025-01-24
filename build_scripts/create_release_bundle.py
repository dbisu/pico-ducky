import os
import shutil
import re
import sys
import zipfile

languages = [ "MAC_FR",
              "US_DVO",
              "WIN_BR",
              "WIN_CZ",
              "WIN_CZ1",
              "WIN_DA",
              "WIN_DE",
              "WIN_ES",
              "WIN_FR",
              "WIN_HU",
              "WIN_IT",
              "WIN_PO",
              "WIN_SW",
              "WIN_TR",
              "WIN_UK" ]

supported_boards = ["raspberry_pi_pico",
                    "raspberry_pi_pico_w",
                    "raspberry_pi_pico2",
                    "raspberry_pi_pico2_w"]

files_to_bundle = ["boot.py",
                   "code.py",
                   "duckyinpython.py",
                   "wsgiserver.py",
                   "webapp.py",
                   "secrets.py",
                   "payload.dd",
                   "payload2.dd",
                   "payload3.dd",
                   "payload4.dd",
                   "INSTALL.txt"]

dirs_to_bundle = ["lib"]


def bundle_files_to_zip(source_dir, destination_dir, file_list, target_file, replacement_dict, version):
  """
  Bundles files from a source directory into a new directory with a unique name.

  Args:
    source_dir: Path to the source directory containing the files.
    destination_dir: Path to the destination directory where bundles will be created.
    file_list: List of filenames to be included in the bundle.
    target_file: Filename of the file to be modified.
    replacement_dict: Dictionary containing key-value pairs for text replacements.

  Returns:
    None
  """

  if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

  # Generate a unique bundle name (e.g., using a timestamp)
  bundle_name = f"pico-ducky-{version}-{destination_dir}.zip"
  bundle_path = os.path.join(destination_dir, bundle_name)

  # Create a temporary directory for the bundle contents
  temp_dir = os.path.join(destination_dir, "temp_bundle")
  os.makedirs(temp_dir)

  for filename in file_list:
    source_file = os.path.join(source_dir, filename)
    destination_file = os.path.join(temp_dir, filename)

    if filename == target_file:
      with open(source_file, 'r') as f:
        file_content = f.read()

      for key, value in replacement_dict.items():
        file_content = re.sub(key, value, file_content)

      with open(destination_file, 'w') as f:
        f.write(file_content)
    else:
      shutil.copy2(source_file, destination_file)

  for dir in dirs_to_bundle:
      shutil.copytree(os.path.join(source_dir,dir),os.path.join(temp_dir,dir))

  #find uf2 files for supported boards
  for root, dirs, files in os.walk(source_dir):
    for file in files:
        for board in supported_boards:
            if '-'+board+'-' in file:
                source_file = os.path.join(source_dir, file)
                destination_file = os.path.join(temp_dir, file)
                shutil.copy2(source_file, destination_file)

    # Create the ZIP archive
  with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(temp_dir):
      for file in files:
        file_path = os.path.join(root, file)
        archive_path = os.path.relpath(file_path, temp_dir)
        zipf.write(file_path, archive_path)

  # Remove the temporary directory
  shutil.rmtree(temp_dir)

def main(argv):
    version = argv[0]
    for dest_dir in languages:
        source_directory = "US"

        target_file_to_modify = "duckyinpython.py"
        replacements = {
            "#from keyboard_layout_win_LANG": "from keyboard_layout_"+dest_dir.lower(),
            "#from keycode_win_LANG": "from keycode_"+dest_dir.lower(),
            "from adafruit_hid.keyboard_": "#from adafruit_hid.keyboard_",
            "from adafruit_hid.keycode": "#from adafruit_hid.keycode"
        }

        bundle_files_to_zip(source_directory, dest_dir, files_to_bundle,
                        target_file_to_modify, replacements, version)

if __name__ == "__main__":
   main(sys.argv[1:])
