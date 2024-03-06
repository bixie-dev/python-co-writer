import os
import time
import copy
from plyer import notification

header_text = """
Writing simultaneously ...

Input the folders you have to sync.
If done, please input X or x

------------------------------------------
"""

app_name = 'File Sync'
# app_icon = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTi8Aqk31nBzI-j5BfALbPP2UdGYgmsiG0rt99TMoSu7lA-Hlxl0RydQeNZKfD_Z15r6L8&usqp=CAU'
timeout = 5

print(header_text)

folders: dict = {}
old_folder_datas: dict[dict] = {}

def getInput():
  count = 0
  while (True):
    text = input(f'[{count}]: ')
    if (text == 'x' or text == 'X'):
      os.system('cls')
      print('sync-ing folders')
      print('------------------------------------------')
      for id, folder in folders.items():
        print(f'[{id}]: {folder}')
      print('------------------------------------------')
      break

    folders[str(count)] = text
    count += 1


def file_data_list(root: str, folder: str):
  entries = os.listdir(folder)
  paths = [os.path.join(folder, entry) for entry in entries]

  result = {}
  for path in paths:
    if (os.path.isfile(path)):
      file = open(path)
      result[os.path.relpath(path, root)] = file.read()
      file.close()
    if (os.path.isdir(path)):
      result.update(file_data_list(root, path))

  return result


def remove_files(folder: str):
  entries = os.listdir(folder)
  paths = [os.path.join(folder, entry) for entry in entries]

  for path in paths:
    try:
      if (os.path.isfile(path)):
        os.remove(path)
      if (os.path.isdir(path)):
        remove_files(path)
        os.rmdir(path)
    except:
      print(f'{path} not removed')
      notification.notify(
        title='File not removed',
        message=f'File: {path}',
        app_name=app_name,
        # app_icon=app_icon,
        timeout=timeout
      )


def get_folder_datas() -> dict:
  data: dict = {}
  for key, folder in folders.items():
    try:
      data[key] = file_data_list(root=folder, folder=folder)
    except:
      print(f'Error occured, folder: {folder}')
      notification.notify(
        title='Error occured',
        message=f'Folder: {folder}',
        app_name=app_name,
        # app_icon=app_icon,
        timeout=timeout
      )
      
  return data


def compare_folder_datas(old_datas: dict, new_datas: dict) -> str | None:
  for key in new_datas.keys():
    if (old_datas[key] != new_datas[key]):
      return key
  return None


def watch_folders():
  old_folder_datas = get_folder_datas()

  while True:
    time.sleep(1)
    new_folder_datas = get_folder_datas()
    changed_folder_id = compare_folder_datas(old_folder_datas, new_folder_datas)

    if changed_folder_id is not None:
      changed_folder = folders[changed_folder_id]
      print(f'Detected changes on {changed_folder}\r')

      changed_folder_data: dict = new_folder_datas[changed_folder_id]

      for key, folder in folders.items():
        if (key == changed_folder_id):
          old_folder_datas[key] = copy.deepcopy(changed_folder_data)
          continue

        remove_files(folder)
        
        for file_name, file_data in changed_folder_data.items():
          try:
            file_path = os.path.join(folder, file_name)
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)

            file = open(file_path, 'w')
            file.write(file_data)
            file.close()
          except:
            print(f'{file_name} not updated')
            notification.notify(
              title='Files not updated',
              message=f'File: {file_name}',
              app_name=app_name,
              # app_icon=app_icon,
              timeout=timeout
            )

        old_folder_datas[key] = copy.deepcopy(changed_folder_data)

      notification.notify(
        title='Files Synced',
        message='All files are successfully updated',
        app_name=app_name,
        # app_icon=app_icon,
        timeout=timeout
      )


def main():
  getInput()

  print('')
  print('Watching files ...')

  watch_folders()

  
if __name__ == '__main__':
  main()