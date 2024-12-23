import importlib
import logging
import os
import inspect
import time
from django.conf import settings
import os
import django


from django.core.management.base import BaseCommand
from multiprocessing import Process
from pathlib import Path
logger = logging.getLogger(__name__)


strategy_map = {}

module_path = f'{Path(__file__).resolve().parent.parent.parent}/strategies'  # 假设代码都在这个目录下

classes_in_files = []
# 遍历指定目录及其子目录中的所有 .py 文件并找到里面的类
for root, _, files in os.walk(module_path):
    for file in files:
        if file.endswith('.py') and file != "base_strategy.py":
            file_path = os.path.join(root, file)
            module_name = os.path.splitext(file)[0]

            # 动态加载模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)

                    # for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
                    #     print(cls_name)
                    #     print(cls_obj)
                    # 查找模块中的类
                    classes = [
                        cls_obj for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass)
                        if cls_obj.__module__ == module_name
                    ]
                    classes_in_files.append(classes[0])

                    strategy_map[classes[0].__name__] = classes[0]
                except Exception as e:
                    logger.error(f"无法加载文件 {file_path}：{e}")


def start_sub_process(name):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analyse_engine.settings')
    django.setup()
    logger.debug(f"{name}开始启动")
    strategy_map[name].start()
class Command(BaseCommand):

    @staticmethod
    def start():
        TARGET_STRATEGY = ["DoubleMaOkex"]
        jobs = []
        for klass in classes_in_files:
            p = Process(name=klass.__name__,target=start_sub_process, args=(klass.__name__,), daemon=True)
            p.start()
            jobs.append(p)

        for i in jobs:
            i.join()

    def handle(self, *args, **options):
        self.start()


if __name__ == '__main__':
    logger.info(Path(__file__).resolve().parent.parent.parent)






