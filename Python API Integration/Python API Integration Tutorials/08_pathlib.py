from pathlib import Path

# curr working dir.
config_dir = Path(".")
filename = "settings.yaml"

# print(config_dir, type(config_dir))

# joining paths
config_path = config_dir / filename\

    # print(config_path)
# provides absolute path
    # print(config_path.resolve())

##############################################################

service_log = Path("/var/log/app/service.log")

# print(f"Exists: {service_log.exists()}")
# print(f"isFile: {service_log.is_file()}")
# print(f"isDir: {service_log.is_dir()}")
# print(f"Parent Path: {service_log.parent}")
# print(f"Name: {service_log.name}")
# print(f"Prefix or Stem: {service_log.stem}")
# print(f"Suffix: {service_log.suffix}")

###############################################################

course_parent = Path(".")

# print("Immediate Children:")
# for child in course_parent.iterdir():
#     print(f" {child.name} - {child.is_dir()}")

# print("Traverse Files Recursively")
# for i, child in enumerate(course_parent.glob("**/*.py")):
#     print(f" {child.name} - {child.is_dir()}")
#     if i >= 5: break

###############################################################

test_file = Path("demo.txt")

# test_file.write_text("Hello, from pathlib !!", encoding="utf-8")
# print(f"Read back: {test_file.read_text(encoding="utf-8")}")

# with test_file.open(mode="a",encoding="utf-8") as file:
#     file.write("\nAppended line")

# print(f"Read back: {test_file.read_text(encoding="utf-8")}")

# # to clean and remove the file
# test_file.unlink()